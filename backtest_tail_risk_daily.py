import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import statsmodels.api as sm
from kl_tail_risk_measure import KLTailRiskAnalysis
import warnings

warnings.filterwarnings("ignore")

class TailRiskBacktester:
    def __init__(self, tickers=None, market_ticker='^GSPC', start_date="2020-01-01", 
                 end_date="2024-01-01", horizons=None, load_optimized_params=True):
        if tickers is None:
            self.tickers = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
                'JPM', 'V', 'MA', 'BAC', 'GS', 'MS', 'WFC', 'C',
                'LLY', 'JNJ', 'PFE', 'ABBV', 'MRK', 'TMO', 'UNH',
                'WMT', 'PG', 'KO', 'PEP', 'COST', 'T', 'VZ',
                'DIS', 'NFLX', 'XOM', 'CVX', 'AVGO', 'AMD', 'ORCL', 'CRM',
                'INTC', 'HD', 'BA'
            ]
        else:
            self.tickers = tickers
            
        if horizons is None:
            self.horizons = [1, 5, 10, 21]
        else:
            self.horizons = horizons
            
        self.market_ticker = market_ticker
        self.start_date = start_date
        self.end_date = end_date
        
        self.stock_returns = None
        self.market_returns = None
        self.market_prices = None
        self.signals = None
        self.data = None
        self.fwd_returns = None
        self.fwd_vol_ratios = None
        
        self.params = {
            'KJ_Lambda': {'window': 60, 'quantile': 0.05},
            'KL_MEES': {'window': 30, 'n_pca': 4, 'alpha': 0.10}
        }
        
        if load_optimized_params:
            self._load_optimized_file()
            
    def _load_optimized_file(self):
        import os
        import json
        param_file = 'optimized_params.json'
        if os.path.exists(param_file):
            try:
                with open(param_file, 'r') as f:
                    all_params = json.load(f)
                
                if self.market_ticker in all_params:
                    market_cfg = all_params[self.market_ticker]
                    for measure in ['KJ_Lambda', 'KL_MEES']:
                        if measure in market_cfg:
                            self.params[measure].update(market_cfg[measure])
                    print(f"Loaded optimized parameters for {self.market_ticker}: {self.params}")
            except Exception as e:
                print(f"Failed to load {param_file}: {e}")
        
    def fetch_data(self):
        print(f"Downloading data for {len(self.tickers)} stocks and market proxy {self.market_ticker}...")
        data = yf.download(self.tickers + [self.market_ticker], start=self.start_date, end=self.end_date, progress=False)['Close']
        stock_prices = data[self.tickers]
        market_prices = data[self.market_ticker]
        
        stock_returns = stock_prices.pct_change().dropna(how='all').fillna(0)
        market_returns = market_prices.pct_change().dropna()
        
        common_idx = stock_returns.index.intersection(market_returns.index)
        
        self.stock_returns = stock_returns.loc[common_idx]
        self.market_returns = market_returns.loc[common_idx]
        self.market_prices = market_prices.loc[common_idx]
        self.data = data

    def compute_daily_kj_lambda(self, window=None, quantile=None):
        if window is None: window = self.params['KJ_Lambda']['window']
        if quantile is None: quantile = self.params['KJ_Lambda']['quantile']
        
        if self.stock_returns is None:
            self.fetch_data()
            
        print("Computing daily rolling KJ Lambda (trailing window)...")
        lambdas = pd.Series(index=self.stock_returns.index, dtype=float, name="KJ_Lambda")
        
        # Calculate rolling market variance
        market_var = self.market_returns.rolling(window).var()
        betas = pd.DataFrame(index=self.stock_returns.index, columns=self.stock_returns.columns)
        
        for col in self.stock_returns.columns:
            cov = self.stock_returns[col].rolling(window).cov(self.market_returns)
            betas[col] = cov / market_var
            
        stock_mean = self.stock_returns.rolling(window).mean()
        market_mean = self.market_returns.rolling(window).mean()
        intercepts = stock_mean - betas.multiply(market_mean, axis=0)
        
        # Use lagged beta/intercept to calculate residual on day t to avoid look-ahead
        shifted_betas = betas.shift(1)
        shifted_intercepts = intercepts.shift(1)
        
        residuals = self.stock_returns - (shifted_intercepts + shifted_betas.multiply(self.market_returns, axis=0))
        
        # Kelly-Jiang Lambda estimation
        for i in range(window, len(residuals)):
            # Pool trailing window residuals
            window_res = residuals.iloc[i-window+1:i+1].values.flatten()
            window_res = window_res[~np.isnan(window_res)]
            
            if len(window_res) < 20:
                continue
                
            u_t = np.percentile(window_res, quantile * 100)
            exceedances = window_res[window_res < u_t]
            
            if len(exceedances) > 0:
                lambda_val = np.mean(np.log(np.abs(exceedances) / np.abs(u_t)))
                lambdas.iloc[i] = lambda_val
                
        return lambdas.dropna()

    def compute_daily_kl_mees(self, window=None, n_pca=None, alpha=None):
        if window is None: window = self.params.get('KL_MEES', {}).get('window', 30)
        if n_pca is None: n_pca = self.params.get('KL_MEES', {}).get('n_pca', 4)
        if alpha is None: alpha = self.params.get('KL_MEES', {}).get('alpha', 0.10)
        
        if self.stock_returns is None:
            self.fetch_data()

        print("Computing daily rolling KL MEES...")
        # Use KLTailRiskAnalysis for its PCA/MEES math – no data fetching needed
        analyzer = KLTailRiskAnalysis(
            tickers=self.tickers,
            target_index=self.market_ticker,
            enable_pca=True,
            target_portfolios=n_pca,
            window=window,
            n_pca=n_pca,
            alpha=alpha,
        )

        eval_dates = self.stock_returns.index[window:]
        mees_daily = pd.Series(index=eval_dates, dtype=float, name="KL_MEES")
        daily_loadings = {}

        for date in eval_dates:
            mees_val, _, pca_loadings = analyzer.calculate_single_day_mees(
                target_date=date,
                returns_df=self.stock_returns,
                window=window,
                alpha=alpha,
            )
            mees_daily.loc[date] = mees_val
            if pca_loadings is not None:
                daily_loadings[date] = pca_loadings

        self.latest_kl_loadings = daily_loadings
        return mees_daily.dropna()

    def prepare_forward_returns(self):
        """Build forward return and vol-ratio DataFrames. Must be called after fetch_data()."""
        if self.market_returns is None:
            self.fetch_data()
        self.fwd_returns = pd.DataFrame(index=self.market_returns.index)
        self.fwd_vol_ratios = pd.DataFrame(index=self.market_returns.index)

        for h in self.horizons:
            future_return = (self.market_prices.shift(-h) / self.market_prices - 1)
            self.fwd_returns[f"Return_{h}d"] = future_return

            if h > 1:
                future_vol = self.market_returns.rolling(window=h).std() * np.sqrt(252)
            else:
                future_vol = self.market_returns.abs() * np.sqrt(252)

            current_vol = self.market_returns.rolling(window=21).std().shift(1) * np.sqrt(252)
            vol_ratio = future_vol.shift(-h) / current_vol
            self.fwd_vol_ratios[f"VolRatio_{h}d"] = vol_ratio

    def generate_signals(self):
        kj_lambda = self.compute_daily_kj_lambda()
        kl_mees = self.compute_daily_kl_mees()
        self.signals = pd.concat([kj_lambda, kl_mees], axis=1).dropna()
        print(f"Generated {len(self.signals)} days of overlapping signals.")

        if not self.horizons:
            return

        self.prepare_forward_returns()

        # Align all dataframes
        common_index = self.signals.index.intersection(self.fwd_returns.index).intersection(self.fwd_vol_ratios.index)
        self.signals = self.signals.loc[common_index]
        self.fwd_returns = self.fwd_returns.loc[common_index]
        self.fwd_vol_ratios = self.fwd_vol_ratios.loc[common_index]


    def run_regressions(self, measure_col='KJ_Lambda', include_velocity=True):
        """
        Run regressions for the specified measure to predict future returns and volatility.
        Optionally includes the 5-day velocity (momentum) of the measure as a multivariate predictor.
        """
        if measure_col not in self.signals:
            print(f"Signal {measure_col} not found. Please generate signals first.")
            return None, None
            
        if self.fwd_returns is None or self.fwd_vol_ratios is None:
            print("Forward testing metrics not instantiatied. Returning empty frame.")
            return pd.DataFrame(), pd.DataFrame()

        aligned_data = pd.concat([self.signals, self.fwd_returns, self.fwd_vol_ratios], axis=1).dropna()
        
        X_level = aligned_data[measure_col]
        # Calculate 5-day Velocity (momentum)
        X_velocity = X_level.diff(periods=5)
        aligned_data['Velocity'] = X_velocity
        aligned_data = aligned_data.dropna()
        
        if aligned_data.empty:
             print("No overlapping data found for regressions.")
             return pd.DataFrame(), pd.DataFrame()
        
        X_level = aligned_data[measure_col]
        X_vel = aligned_data['Velocity']

        ret_results = []
        vol_results = []

        for h in self.horizons:
            # Predict Returns
            y_ret = aligned_data[f'Return_{h}d']
            
            if include_velocity:
                X_multi = sm.add_constant(pd.DataFrame({measure_col: X_level, f'{measure_col}_Velocity': X_vel}))
                model_ret = sm.OLS(y_ret, X_multi).fit(cov_type='HAC', cov_kwds={'maxlags': h})
                ret_results.append({
                    'Horizon (Days)': h,
                    f'{measure_col} Beta': model_ret.params.get(measure_col, np.nan),
                    f'{measure_col} t-stat': model_ret.tvalues.get(measure_col, np.nan),
                    f'{measure_col}_Vel Beta': model_ret.params.get(f'{measure_col}_Velocity', np.nan),
                    f'{measure_col}_Vel t-stat': model_ret.tvalues.get(f'{measure_col}_Velocity', np.nan),
                    'Adj. R-squared': model_ret.rsquared_adj
                })
            else:
                X_uni = sm.add_constant(X_level)
                model_ret = sm.OLS(y_ret, X_uni).fit(cov_type='HAC', cov_kwds={'maxlags': h})
                ret_results.append({
                    'Horizon (Days)': h,
                    f'{measure_col} Beta': model_ret.params[measure_col],
                    f'{measure_col} t-stat': model_ret.tvalues[measure_col],
                    'Adj. R-squared': model_ret.rsquared_adj
                })

            # Predict Volatility Ratio
            y_vol = aligned_data[f'VolRatio_{h}d']
            
            if include_velocity:
                X_multi = sm.add_constant(pd.DataFrame({measure_col: X_level, f'{measure_col}_Velocity': X_vel}))
                model_vol = sm.OLS(y_vol, X_multi).fit(cov_type='HAC', cov_kwds={'maxlags': h})
                vol_results.append({
                    'Horizon (Days)': h,
                    f'{measure_col} Beta': model_vol.params.get(measure_col, np.nan),
                    f'{measure_col} t-stat': model_vol.tvalues.get(measure_col, np.nan),
                    f'{measure_col}_Vel Beta': model_vol.params.get(f'{measure_col}_Velocity', np.nan),
                    f'{measure_col}_Vel t-stat': model_vol.tvalues.get(f'{measure_col}_Velocity', np.nan),
                    'Adj. R-squared': model_vol.rsquared_adj
                })
            else:
                X_uni = sm.add_constant(X_level)
                model_vol = sm.OLS(y_vol, X_uni).fit(cov_type='HAC', cov_kwds={'maxlags': h})
                vol_results.append({
                    'Horizon (Days)': h,
                    f'{measure_col} Beta': model_vol.params[measure_col],
                    f'{measure_col} t-stat': model_vol.tvalues[measure_col],
                    'Adj. R-squared': model_vol.rsquared_adj
                })

        return pd.DataFrame(ret_results).set_index('Horizon (Days)').round(4), pd.DataFrame(vol_results).set_index('Horizon (Days)').round(4)
        

    def visualize_signals(self, save_path='daily_tail_risk_prediction.png'):
        if self.signals is None:
            self.generate_signals()
            
        # Prepare data for plotting
        plot_data = pd.concat([self.market_prices, self.signals], axis=1).dropna()
        
        # Create subplots dynamically based on the number of signals
        num_signals = len(self.signals.columns)
        fig, axes = plt.subplots(num_signals, 1, figsize=(14, 6 * num_signals), sharex=True)
        
        # Ensure axes is an array even if there's only one signal
        if num_signals == 1:
            axes = [axes]

        for i, col in enumerate(self.signals.columns):
            ax1 = axes[i]
            
            # Plot the market proxy on the left y-axis
            color = 'tab:blue'
            ax1.set_xlabel('Date')
            ax1.set_ylabel(self.market_ticker, color=color)
            ax1.plot(plot_data.index, plot_data[self.market_ticker], color=color, label='Market Proxy')
            ax1.tick_params(axis='y', labelcolor=color)

            # Plot the tail risk signal on the right y-axis
            ax2 = ax1.twinx()  
            color = 'tab:red'
            ax2.set_ylabel(col, color=color)
            
            # Calculate the 50-day moving average as a smoothed signal trace overlay
            ax2.plot(plot_data.index, plot_data[col], color=color, alpha=0.9, label=col)
            ax2.plot(plot_data.index, plot_data[col].rolling(window=50).mean(), 
                     color='tab:orange', linestyle='--', alpha=0.8, linewidth=1.5, label='50d MA')
            ax2.tick_params(axis='y', labelcolor=color)

            # Calculate and dynamically shade "red zones" for High Risk regimes (>90th percentile historical)
            sig_series = plot_data[col]
            if not sig_series.empty:
                threshold_90 = np.percentile(sig_series.dropna(), 90)
                ax2.axhline(threshold_90, color='darkred', linestyle=':', alpha=0.6, label='90th Pct Alarm')
                
                # Fill areas red where the signal breaches the 90th percentile
                ax2.fill_between(plot_data.index, 
                                 sig_series.min(), 
                                 sig_series,
                                 where=(sig_series >= threshold_90), 
                                 color='red', 
                                 alpha=0.15,
                                 interpolate=False)

            # Merge legends
            lines, labels = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc='upper left')
            
            ax1.set_title(f'{self.market_ticker} vs {col}')
            ax1.grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path)
        print(f"\nSaved visualization to '{save_path}'.")

    def run_full_analysis(self):
        self.generate_signals()
        
        print("\n==========================================================")
        print("--- Kelly-Jiang (KJ) Lambda Predictive Backtest ---")
        kj_ret, kj_vol = self.run_regressions('KJ_Lambda')
        print("\n* Future Market Returns *")
        print(kj_ret.to_string(float_format="%.4f"))
        print("\n* Future Market Volatility *")
        print(kj_vol.to_string(float_format="%.4f"))
        
        print("\n==========================================================")
        print("--- KL MEES Predictive Backtest ---")
        kl_ret, kl_vol = self.run_regressions('KL_MEES')
        print("\n* Future Market Returns *")
        print(kl_ret.to_string(float_format="%.4f"))
        print("\n* Future Market Volatility *")
        print(kl_vol.to_string(float_format="%.4f"))
        print("==========================================================")

        self.visualize_signals()


if __name__ == "__main__":
    backtester = TailRiskBacktester(
        tickers=None,  # Uses default Top 40 SPX universe
        market_ticker="^GSPC",
        start_date="2018-01-01",
        end_date="2026-02-27",
        horizons=[1, 5, 10, 21]
    )
    backtester.run_full_analysis()
