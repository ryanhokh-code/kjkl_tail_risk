import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression


class TailRiskMeasure:
    """
    Implementation of the Kelly and Jiang (2014) Dynamic Tail Risk Measure.
    Estimates common tail risk (lambda) from a cross-section of returns.
    """

    def __init__(self, tickers, market_ticker='SPY', period='5y'):
        self.tickers = tickers
        self.market_ticker = market_ticker
        self.period = period
        self.returns = None
        self.market_returns = None
        self.residuals = None
        self.kj_lambda = None

    def fetch_data(self):
        """Downloads historical price data and calculates daily returns."""
        print(f"Downloading data for {len(self.tickers)} tickers...")
        data = yf.download(self.tickers, period=self.period)['Close']
        self.market_returns = yf.download(self.market_ticker, period=self.period)['Close'].pct_change().dropna()
        self.returns = data.pct_change().dropna()
        return self

    def residualize_returns(self):
        """
        Removes common factors to isolate firm-level shocks[cite: 173, 174].
        Uses a simple market-beta residualization as a proxy for Fama-French.
        """
        if self.returns is None:
            raise ValueError("Data not fetched. Run fetch_data() first.")

        print("Residualizing returns to isolate idiosyncratic tail events...")
        self.residuals = pd.DataFrame(index=self.returns.index, columns=self.returns.columns)

        # Align market and stock indices
        common_idx = self.returns.index.intersection(self.market_returns.index)
        X = self.market_returns.loc[common_idx].values.reshape(-1, 1)

        for ticker in self.tickers:
            y = self.returns.loc[common_idx, ticker].values.reshape(-1, 1)
            model = LinearRegression().fit(X, y)
            self.residuals.loc[common_idx, ticker] = (y - model.predict(X)).flatten()
        return self

    def calculate_lambda(self, threshold_quantile=0.05):
        """
        Calculates the monthly tail risk measure lambda using the Hill estimator[cite: 138, 143].
        Pooled cross-sectional returns below the 5th percentile are used[cite: 146, 158].
        """
        print(f"Calculating lambda using {threshold_quantile * 100}% threshold...")
        lambda_results = {}

        # Group by month (KJ 2014, Section 1.1) [cite: 138]
        for month, group in self.residuals.groupby(pd.Grouper(freq='ME')):
            pooled = group.values.flatten().astype(float)
            pooled = pooled[~np.isnan(pooled)]

            # Define threshold u_t as the specified percentile [cite: 146]
            u_t = np.percentile(pooled, threshold_quantile * 100)

            # Identify u-exceedences [cite: 147]
            exceedences = pooled[pooled < u_t]

            if len(exceedences) > 0:
                # Hill Estimator Formula [cite: 141, 143]
                # lambda_t = (1/K) * sum(ln(R_k / u_t))
                hill_val = np.mean(np.log(np.abs(exceedences) / np.abs(u_t)))
                lambda_results[month] = hill_val

        self.kj_lambda = pd.Series(lambda_results)
        return self.kj_lambda

    def get_tail_betas(self):
        """
        Estimates the sensitivity (beta) of each stock to the aggregate tail risk[cite: 367, 368].
        """
        betas = {}
        # Use lagged lambda to predict returns (Section 2.3) [cite: 367, 384]
        lagged_lambda = self.kj_lambda.shift(1).dropna()

        for ticker in self.tickers:
            monthly_rets = self.returns[ticker].resample('ME').mean().loc[lagged_lambda.index]
            common = monthly_rets.index.intersection(lagged_lambda.index)

            if len(common) > 12:
                X = lagged_lambda.loc[common].values.reshape(-1, 1)
                y = monthly_rets.loc[common].values
                model = LinearRegression().fit(X, y)
                betas[ticker] = model.coef_[0]

        return pd.Series(betas).sort_values()

    def plot_results(self):
        """Visualizes the aggregate tail risk and cross-sectional sensitivities."""
        plt.figure(figsize=(12, 10))

        # Plot 1: Common Tail Risk (Lambda) [cite: 224]
        plt.subplot(2, 1, 1)
        plt.plot(self.kj_lambda.index, self.kj_lambda.values, color='firebrick', lw=2)
        plt.title("Aggregate Tail Risk lambda over Time", fontsize=14)
        plt.ylabel("Tail Exponent Value")
        plt.grid(True, linestyle='--', alpha=0.6)

        # Plot 2: Tail Betas [cite: 390]
        plt.subplot(2, 1, 2)
        betas = self.get_tail_betas()
        colors = ['navy' if x < 0 else 'darkred' for x in betas.values]
        betas.plot(kind='bar', color=colors)
        plt.title("Asset Sensitivity to Tail Risk beta_i)", fontsize=14)
        plt.ylabel("Tail Beta Loading")
        plt.axhline(0, color='black', linewidth=0.8)

        plt.tight_layout()
        plt.show()


# --- EXECUTION ---
if __name__ == "__main__":
    tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
        'JPM', 'V', 'MA', 'BAC', 'GS', 'LLY', 'JNJ', 'PFE', 'WMT',
        'PG', 'KO', 'DIS', 'NFLX', 'XOM', 'CVX', 'AVGO', 'AMD',
        'ORCL', 'CRM', 'INTC', 'BRK-B', 'HD', 'MCD', 'CAT', 'GE',
        'BA', 'T', 'VZ', 'CSCO', 'ABT', 'PEP', 'COST', 'MRK'
    ]

    measure = TailRiskMeasure(tickers=tickers, market_ticker='SPY', period='5y')
    measure.fetch_data().residualize_returns().calculate_lambda()
    measure.plot_results()