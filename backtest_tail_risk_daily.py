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
                 end_date="2024-01-01", horizons=None):
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

    def compute_daily_kj_lambda(self, window=60, quantile=0.05):
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

    def compute_daily_kl_mees(self, window=30, n_pca=4):
        if self.stock_returns is None:
            self.fetch_data()
            
        print("Computing daily rolling KL MEES...")
        # Utilize the previously built KL Analysis Class
        kl_analyzer = KLTailRiskAnalysis(enable_pca=True, target_portfolios=n_pca)
        eval_dates = self.stock_returns.index[window:]
        mees_daily = pd.Series(index=eval_dates, dtype=float, name="KL_MEES")
        
        for date in eval_dates:
            mees_val, _ = kl_analyzer.calculate_single_day_mees(
                target_date=date,
                returns_df=self.stock_returns,
                window=window,
                alpha=0.10
            )
            mees_daily.loc[date] = mees_val
            
        return mees_daily.dropna()

    def generate_signals(self):
        kj_lambda = self.compute_daily_kj_lambda()
        kl_mees = self.compute_daily_kl_mees()
        self.signals = pd.concat([kj_lambda, kl_mees], axis=1).dropna()
        print(f"Generated {len(self.signals)} days of overlapping signals.")

    def run_regressions(self, measure):
        """Runs the univariate backtest for a specific risk measure."""
        if measure not in ['KJ_Lambda', 'KL_MEES']:
            raise ValueError("Measure must be 'KJ_Lambda' or 'KL_MEES'")
            
        results_return = []
        results_vol = []
        
        for h in self.horizons:
            # Future Horizon Return (Prediction of market corrections)
            future_return = (self.market_prices.shift(-h) / self.market_prices - 1).dropna()
            future_return.name = f"Future_Ret_{h}d"
            
            # Future Realized Volatility
            if h > 1:
                future_vol = self.market_returns.rolling(window=h).std().shift(-h).dropna()
            else:
                future_vol = self.market_returns.abs().shift(-1).dropna()
            future_vol.name = f"Future_Vol_{h}d"
            
            df_ret = self.signals[[measure]].join(future_return, how='inner').dropna()
            df_vol = self.signals[[measure]].join(future_vol, how='inner').dropna()
            
            if len(df_ret) == 0:
                continue
                
            y_ret = df_ret[f"Future_Ret_{h}d"]
            X_ret = sm.add_constant(df_ret[[measure]])
            model_ret = sm.OLS(y_ret, X_ret).fit(cov_type='HAC', cov_kwds={'maxlags': h})
            
            results_return.append({
                'Horizon (Days)': h,
                f'{measure} Beta': model_ret.params[measure],
                f'{measure} t-stat': model_ret.tvalues[measure],
                'Adj. R-squared': model_ret.rsquared_adj
            })
            
            y_vol = df_vol[f"Future_Vol_{h}d"]
            X_vol = sm.add_constant(df_vol[[measure]])
            model_vol = sm.OLS(y_vol, X_vol).fit(cov_type='HAC', cov_kwds={'maxlags': h})
            
            results_vol.append({
                'Horizon (Days)': h,
                f'{measure} Beta': model_vol.params[measure],
                f'{measure} t-stat': model_vol.tvalues[measure],
                'Adj. R-squared': model_vol.rsquared_adj
            })
            
        res_ret_df = pd.DataFrame(results_return).set_index('Horizon (Days)')
        res_vol_df = pd.DataFrame(results_vol).set_index('Horizon (Days)')
        
        return res_ret_df, res_vol_df

    def visualize_signals(self, save_path='daily_tail_risk_prediction.png'):
        if self.signals is None:
            self.generate_signals()
            
        fig, (ax_price, ax1) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [1, 2]}, sharex=True)
        
        # 1. Plot Market Trend on Top Subplot
        idx = self.signals.index
        ax_price.plot(idx, self.market_prices.loc[idx], color='black', linewidth=1.5, label=f'Market Price ({self.market_ticker})')
        ax_price.set_title('Market Trend & Daily Tail Risk Measures', fontsize=16)
        ax_price.set_ylabel('Index Price')
        ax_price.grid(True, alpha=0.3)
        ax_price.legend(loc='upper left')
        
        # 2. Plot Signals on Bottom Subplot
        z_kj = (self.signals['KJ_Lambda'] - self.signals['KJ_Lambda'].mean()) / self.signals['KJ_Lambda'].std()
        z_kl = (self.signals['KL_MEES'] - self.signals['KL_MEES'].mean()) / self.signals['KL_MEES'].std()
        
        ax1.plot(idx, z_kj, label='Kelly-Jiang Lambda (Z-Score)', color='blue', alpha=0.7)
        ax1.plot(idx, z_kl, label='KL MEES (Z-Score)', color='red', alpha=0.7)
        
        # Overlay Future 21-day Volatility on secondary axis
        ax2 = ax1.twinx()
        vol_21 = self.market_returns.rolling(window=21).std().shift(-21).dropna()
        common_idx = idx.intersection(vol_21.index)
        ax2.plot(common_idx, vol_21.loc[common_idx] * np.sqrt(252), label='Future 21d SPX Annualized Volatility', color='black', linestyle='--')
        
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Tail Risk Signal (Z-Score)')
        ax2.set_ylabel('Annualized Market Volatility')
        
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
        
        ax1.grid(True, alpha=0.3)
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
