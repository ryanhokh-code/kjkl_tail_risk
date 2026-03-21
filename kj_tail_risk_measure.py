import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


# 1. DATA RETRIEVAL LOGIC (Independent Function)
from utils import fetch_financial_data

def get_kj_returns(tickers, market_ticker='SPY', period='5y'):
    import datetime
    end = datetime.date.today()
    start = end - datetime.timedelta(days=5*365)
    
    data = fetch_financial_data(tickers + [market_ticker], str(start), str(end))
    stock_prices = data[tickers]
    market_prices = data[market_ticker]
    
    daily_stock_returns = stock_prices.pct_change().dropna(how='all')
    daily_market_returns = market_prices.pct_change().dropna()
    return daily_stock_returns, daily_market_returns


# 2. ANALYTICAL CLASS: Kelly-Jiang Tail Risk
class TailRiskAnalyzer:
    """
    Implements construction of lambda_t (tail risk) and beta_i (tail sensitivity).
    Reference: Kelly and Jiang (2014), 'Tail Risk and Asset Prices'.
    """

    def __init__(self, stock_returns, market_returns):
        self.stock_returns = stock_returns
        self.market_returns = market_returns
        self.daily_residuals = None
        self.kj_lambda = None
        self.tail_betas = None

    def calculate_residuals(self):
        """
        Removes common factors from daily returns using OLS (KJ 2014, Sec 1.2).
        This isolates firm-specific tail events from general market volatility.
        """
        print("Residualizing daily returns...")
        # Align indices
        common_idx = self.stock_returns.index.intersection(self.market_returns.index)
        X = self.market_returns.loc[common_idx].values.reshape(-1, 1)

        res_df = pd.DataFrame(index=common_idx, columns=self.stock_returns.columns)
        for ticker in self.stock_returns.columns:
            y = self.stock_returns.loc[common_idx, ticker].values.reshape(-1, 1)
            # Mask NaNs for specific ticker availability
            mask = ~np.isnan(y).flatten()
            if mask.any():
                model = LinearRegression().fit(X[mask], y[mask])
                res_df.loc[common_idx[mask], ticker] = (y[mask] - model.predict(X[mask])).flatten()

        self.daily_residuals = res_df.astype(float)
        return self

    def estimate_lambda(self, quantile=0.05):
        """
        Applies Hill's power law estimator to pooled cross-sectional daily residuals.
        Estimated at a monthly frequency (KJ 2014, Sec 1.1).
        """
        if self.daily_residuals is None:
            self.calculate_residuals()

        lambda_results = {}
        # Pool all firm-level daily returns within each month (KJ 2014, Sec 2.1)
        for month, group in self.daily_residuals.groupby(pd.Grouper(freq='ME')):
            pooled = group.values.flatten()
            pooled = pooled[~np.isnan(pooled)]

            if len(pooled) < 20: continue  # Ensure sufficient cross-section

            # Threshold u_t is the 5th percentile (KJ 2014, Sec 1.1)
            u_t = np.percentile(pooled, quantile * 100)

            # Exceedences: values below the threshold (absolute value used for Hill ratio)
            exceedences = pooled[pooled < u_t]

            if len(exceedences) > 0:
                # Equation (2): Lambda_t is the average log-ratio
                # higher lambda = fatter tails
                lambda_val = np.mean(np.log(np.abs(exceedences) / np.abs(u_t)))
                lambda_results[month] = lambda_val

        self.kj_lambda = pd.Series(lambda_results)
        return self.kj_lambda

    def calculate_tail_betas(self, lookback_months=36):
        """
        Estimates the sensitivity of each stock to the aggregate tail risk factor.
        Regresses monthly returns on lagged lambda (KJ 2014, Sec 2.3).
        """
        if self.kj_lambda is None:
            self.estimate_lambda()

        print("Estimating cross-sectional tail betas...")
        betas = {}
        # Lag lambda to test predictive power (KJ 2014, Sec 2.3)
        lagged_lambda = self.kj_lambda.shift(1).dropna()

        for ticker in self.stock_returns.columns:
            # Resample stock returns to monthly frequency for beta calculation
            monthly_stock_rets = self.stock_returns[ticker].resample('ME').apply(lambda x: (1 + x).prod() - 1)
            common = monthly_stock_rets.index.intersection(lagged_lambda.index)

            if len(common) >= lookback_months:
                X = lagged_lambda.loc[common].values.reshape(-1, 1)
                y = monthly_stock_rets.loc[common].values
                model = LinearRegression().fit(X, y)
                betas[ticker] = model.coef_[0]

        self.tail_betas = pd.Series(betas).sort_values()
        return self.tail_betas

    def plot_analysis(self):
        """Generates visualizations for the measure and asset sensitivities."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Plot Lambda Time Series
        ax1.plot(self.kj_lambda.index, self.kj_lambda.values, color='darkred', lw=2)
        ax1.set_title("Estimated Common Tail Risk (lambda_t)", fontsize=14)
        ax1.set_ylabel("Tail Exponent Value")
        ax1.grid(alpha=0.3)

        # Plot Tail Betas
        colors = ['blue' if x < 0 else 'red' for x in self.tail_betas.values]
        self.tail_betas.plot(kind='bar', color=colors, ax=ax2)
        ax2.set_title("Predictive Tail Risk Exposure (beta_i)", fontsize=14)
        ax2.set_ylabel("Beta Loading on lambda_t")
        ax2.axhline(0, color='black', lw=1)

        plt.tight_layout()
        plt.show()


# 3. EXECUTION FLOW
if __name__ == "__main__":
    from config import MARKET_UNIVERSES
    tickers = MARKET_UNIVERSES['^GSPC']['tickers']

    # Step 1: Data Fetching
    daily_returns, mkt_returns = get_kj_returns(tickers)

    # Step 2: Analysis Class instantiation
    analyzer = TailRiskAnalyzer(daily_returns, mkt_returns)

    # Step 3: Run full pipeline
    analyzer.estimate_lambda()  # This will auto-trigger residuals
    analyzer.calculate_tail_betas()

    # Step 4: Visualize results
    analyzer.plot_analysis()