import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from sklearn.decomposition import PCA
import statsmodels.api as sm
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import warnings

# Suppress warnings for cleaner console output
warnings.filterwarnings("ignore")


# =====================================================================
# PART 1: MEES Core Math, PCA, and Weight Mapping
# =====================================================================

def historical_var(returns, alpha=0.10):
    """Calculates the historical Value-at-Risk at the alpha level."""
    return np.percentile(returns, alpha * 100)


def objective_excess_shortfall(weights, returns, alpha=0.10):
    """Objective function: Minimum Excess Expected Shortfall."""
    J = len(returns)
    port_returns = returns @ weights
    var_alpha = historical_var(port_returns, alpha)

    breaches = port_returns[port_returns <= var_alpha]
    if len(breaches) == 0:
        return 0.0

    return np.sum(np.abs(breaches - var_alpha)) / (alpha * J)


def zero_covariance_constraint(weights, returns, prev_weights_list):
    """Ensures the current portfolio has zero covariance with all previously extracted portfolios."""
    if not prev_weights_list:
        return 0.0

    port_returns = returns @ weights
    covariances = []

    for prev_weights in prev_weights_list:
        prev_returns = returns @ prev_weights
        cov = np.cov(port_returns, prev_returns)[0, 1]
        covariances.append(cov)

    return np.sum(np.square(covariances))


def calculate_mees_core_weights(returns_matrix, P=5, alpha=0.10):
    """Core mathematical optimization for MEES using SLSQP."""
    J, n = returns_matrix.shape
    extracted_weights = []
    portfolio_shortfalls = []

    init_guess = np.ones(n) / n
    bounds = tuple((0.0, 1.0) for _ in range(n))

    for p in range(1, P + 1):
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]

        if p > 1:
            constraints.append({
                'type': 'eq',
                'fun': lambda w, pwl=extracted_weights: zero_covariance_constraint(w, returns_matrix, pwl)
            })

        result = minimize(
            objective_excess_shortfall,
            init_guess,
            args=(returns_matrix, alpha),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'disp': False, 'ftol': 1e-6, 'maxiter': 1000}
        )

        if result.success:
            optimal_weights = result.x
            extracted_weights.append(optimal_weights)
            min_shortfall = objective_excess_shortfall(optimal_weights, returns_matrix, alpha)
            portfolio_shortfalls.append(min_shortfall)
        else:
            return np.nan, []

    return np.mean(portfolio_shortfalls), extracted_weights


def map_pca_weights_to_assets(w_pca, pca_model):
    """Maps the optimized PCA weights back to the original asset space."""
    w_asset = np.dot(w_pca, pca_model.components_)

    # Normalize weights so the absolute gross exposure equals 1
    total_exposure = np.sum(np.abs(w_asset))
    if total_exposure > 0:
        w_asset = w_asset / total_exposure

    return w_asset


def calculate_single_day_mees(target_date, returns_df, window=30, P=4, alpha=0.10, use_pca=False, pca_variance=0.90):
    """Calculates MEES measure for a single day, handling PCA if toggled."""
    if target_date not in returns_df.index:
        return np.nan, []

    idx = returns_df.index.get_loc(target_date)

    if idx < window - 1:
        return np.nan, []

    window_returns = returns_df.iloc[idx - window + 1: idx + 1].values

    pca = None
    if use_pca:
        pca = PCA(n_components=pca_variance)
        optimization_returns = pca.fit_transform(window_returns)
    else:
        optimization_returns = window_returns

    # Optimize the portfolios (either on physical stocks or PCA components)
    mees_val, extracted_opt_weights = calculate_mees_core_weights(optimization_returns, P=P, alpha=alpha)

    # Map weights back to assets
    final_asset_weights = []
    if use_pca and extracted_opt_weights:
        for w_pca in extracted_opt_weights:
            w_asset = map_pca_weights_to_assets(w_pca, pca)
            final_asset_weights.append(w_asset)
    else:
        final_asset_weights = extracted_opt_weights

    return mees_val, final_asset_weights


# =====================================================================
# PART 2: Predictive Regression Testing
# =====================================================================

def run_multi_horizon_regression(monthly_tail_risk, target_prices, horizons=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]):
    """Runs the predictive regression over multiple horizons."""
    results = []
    monthly_prices = target_prices.resample('M').last()

    for k in horizons:
        past_returns = monthly_prices.pct_change(periods=k)
        future_returns = past_returns.shift(-k)

        df = pd.concat([future_returns, monthly_tail_risk, past_returns], axis=1).dropna()
        df.columns = ['Future_Return', 'Tail_Risk', 'Past_Return']

        if df.empty:
            continue

        Y = df['Future_Return']
        X = sm.add_constant(df[['Tail_Risk', 'Past_Return']])

        model = sm.OLS(Y, X).fit(cov_type='HAC', cov_kwds={'maxlags': k})

        results.append({
            'k (Months)': k,
            'Beta': model.params['Tail_Risk'],
            't-stat': model.tvalues['Tail_Risk']
        })

    return pd.DataFrame(results).set_index('k (Months)')


# =====================================================================
# PART 3: Beta Persistence Testing
# =====================================================================

def calculate_rolling_betas(monthly_stock_returns, factor_returns, window=24):
    """Calculates rolling betas of individual stocks against the MEES factor."""
    betas = pd.DataFrame(index=monthly_stock_returns.index, columns=monthly_stock_returns.columns)
    aligned_data = pd.concat([monthly_stock_returns, factor_returns], axis=1).dropna()

    factor = aligned_data.iloc[:, -1]
    stocks = aligned_data.iloc[:, :-1]

    for i in range(window, len(aligned_data)):
        start_idx = i - window
        end_idx = i

        X = sm.add_constant(factor.iloc[start_idx:end_idx])

        for col in stocks.columns:
            Y = stocks[col].iloc[start_idx:end_idx]
            if Y.var() > 0:
                model = sm.OLS(Y, X).fit()
                betas.loc[aligned_data.index[end_idx - 1], col] = model.params.iloc[1]

    return betas.dropna(how='all')


def test_beta_persistence(betas_df):
    """Tests if high/low tail risk stocks maintain their decile status."""
    betas_t1 = betas_df.shift(-1)

    avg_beta_diffs = []
    prop_low_stayed = []
    prop_high_stayed = []

    for i in range(len(betas_df) - 1):
        current_date = betas_df.index[i]
        current_betas = betas_df.iloc[i].dropna()

        if len(current_betas) < 10:
            continue

        try:
            deciles_t = pd.qcut(current_betas, 10, labels=False, duplicates='drop') + 1
        except ValueError:
            continue

        low_portfolio_t = current_betas[deciles_t == 1].index
        high_portfolio_t = current_betas[deciles_t == deciles_t.max()].index

        future_betas_low = betas_t1.loc[current_date, low_portfolio_t].dropna()
        future_betas_high = betas_t1.loc[current_date, high_portfolio_t].dropna()

        if len(future_betas_low) > 0 and len(future_betas_high) > 0:
            avg_beta_diffs.append(future_betas_high.mean() - future_betas_low.mean())

        next_betas = betas_df.iloc[i + 1].dropna()
        try:
            deciles_t1 = pd.qcut(next_betas, 10, labels=False, duplicates='drop') + 1
        except ValueError:
            continue

        low_in_t1 = deciles_t1.reindex(low_portfolio_t).dropna()
        if len(low_in_t1) > 0:
            prop_low_stayed.append((low_in_t1 <= 3).sum() / len(low_in_t1))

        high_in_t1 = deciles_t1.reindex(high_portfolio_t).dropna()
        if len(high_in_t1) > 0:
            max_decile_t1 = deciles_t1.max()
            prop_high_stayed.append((high_in_t1 >= (max_decile_t1 - 2)).sum() / len(high_in_t1))

    if not avg_beta_diffs:
        return {"Error": "Not enough data to run beta persistence. Increase timeframe."}

    t_stat, _ = ttest_ind([x for x in avg_beta_diffs if pd.notna(x)], np.zeros(len(avg_beta_diffs)))

    return {
        'Beta persistence t-statistics': t_stat,
        'Proportion of low hedging at t+1': np.mean(prop_low_stayed),
        'Proportion of high hedging at t+1': np.mean(prop_high_stayed)
    }


# =====================================================================
# PART 4: Visualizations
# =====================================================================

def plot_mees_timeseries(mees_series, title="MEES Over Time"):
    plt.figure(figsize=(12, 6))
    plt.plot(mees_series.index, mees_series.values, label='MEES', color='firebrick', linewidth=1.5)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('MEES Value', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()


def plot_rolling_betas(rolling_betas_df, tickers_to_plot=None):
    plt.figure(figsize=(12, 6))
    if tickers_to_plot is None:
        tickers_to_plot = rolling_betas_df.columns[:3]

    for ticker in tickers_to_plot:
        if ticker in rolling_betas_df.columns:
            plt.plot(rolling_betas_df.index, rolling_betas_df[ticker], label=f'{ticker} Beta', linewidth=1.5)

    plt.axhline(0, color='black', linestyle='--', alpha=0.6)
    plt.title('Rolling Betas to MEES Factor', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Beta Coefficient', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()


# =====================================================================
# PART 5: Main Execution Pipeline
# =====================================================================

if __name__ == "__main__":

    # 1. Define parameters
    tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
        'JPM', 'V', 'MA', 'BAC', 'GS', 'LLY', 'JNJ', 'PFE', 'WMT',
        'PG', 'KO', 'DIS', 'NFLX', 'XOM', 'CVX', 'AVGO', 'AMD',
        'ORCL', 'CRM', 'INTC', 'BRK-B', 'HD', 'MCD', 'CAT', 'GE',
        'BA', 'T', 'VZ', 'CSCO', 'ABT', 'PEP', 'COST', 'MRK'
    ]
    target_index = 'SPY'
    start_date = "2020-01-01"
    end_date = "2024-01-01"

    # SET TOGGLES HERE
    ENABLE_PCA = True
    PCA_VARIANCE_EXPLAINED = 0.90  # Extract components explaining 90% of variation
    TARGET_PORTFOLIOS_P = 4  # Optimal number found for S&P 500

    print(f"1. Fetching data for {len(tickers)} stocks and {target_index}...")
    data = yf.download(tickers + [target_index], start=start_date, end=end_date, progress=False)['Close']

    stock_prices = data[tickers]
    target_prices = data[target_index]

    daily_returns = stock_prices.pct_change().dropna(how='all').fillna(0)
    monthly_stock_returns = stock_prices.resample('M').last().pct_change().dropna()

    print(f"2. Calculating daily rolling MEES (PCA Enabled: {ENABLE_PCA})...")
    eval_dates = daily_returns.index[29:]
    mees_daily = pd.Series(index=eval_dates, dtype=float, name="MEES")

    for date in eval_dates:
        mees_val, _ = calculate_single_day_mees(
            target_date=date,
            returns_df=daily_returns,
            window=30,
            P=TARGET_PORTFOLIOS_P,
            alpha=0.10,
            use_pca=ENABLE_PCA,
            pca_variance=PCA_VARIANCE_EXPLAINED
        )
        mees_daily.loc[date] = mees_val

    mees_daily = mees_daily.dropna()
    mees_monthly = mees_daily.resample('M').last()  # Resample for asset pricing tests

    print("\n3. Running Predictive Regressions (Predicting SPY)...")
    predictive_results = run_multi_horizon_regression(mees_monthly, target_prices, horizons=[1, 2, 3, 4, 5, 6])
    print(predictive_results)

    print("\n4. Running Beta Persistence Tests...")
    rolling_betas = calculate_rolling_betas(monthly_stock_returns, mees_monthly,
                                            window=12)  # 12-mth window for short sample size
    persistence_results = test_beta_persistence(rolling_betas)
    for key, val in persistence_results.items():
        print(f"{key}: {val:.4f}" if isinstance(val, float) else f"{key}: {val}")

    print("\n5. Generating Visualizations...")
    plot_mees_timeseries(mees_monthly, title=f"Monthly MEES (P={TARGET_PORTFOLIOS_P}, PCA={ENABLE_PCA})")

    stocks_to_visualize = ['AAPL', 'JNJ', 'JPM']
    plot_rolling_betas(rolling_betas, tickers_to_plot=stocks_to_visualize)

    print("\nPipeline Complete.")