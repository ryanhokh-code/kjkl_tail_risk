import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from sklearn.decomposition import PCA

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
        
    excess_shortfall = np.sum(np.abs(breaches - var_alpha)) / (alpha * J)
    return excess_shortfall

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

def calculate_mees_core(returns_matrix, P=5, alpha=0.10, is_pca=False):
    """Core mathematical optimization for MEES."""
    J, n = returns_matrix.shape
    extracted_weights = []
    portfolio_shortfalls = []
    
    init_guess = np.ones(n) / n
    
    # Note on bounds: If we are optimizing over abstract PCA factors instead of physical 
    # stocks, the strict long-only bound (0 to 1) might constrain the model artificially, 
    # but we keep it here to ensure stability and match the paper's original math constraints.
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
            return np.nan
            
    return np.mean(portfolio_shortfalls)

def calculate_single_day_mees(target_date, returns_df, window=30, P=4, alpha=0.10, use_pca=False, pca_variance=0.90):
    """Calculates the MEES measure for a single day, with an option to reduce dimensions via PCA."""
    if target_date not in returns_df.index:
        raise ValueError(f"Date {target_date} not found in returns DataFrame index.")
        
    idx = returns_df.index.get_loc(target_date)
    
    if idx < window - 1:
        return np.nan 
        
    window_returns = returns_df.iloc[idx - window + 1 : idx + 1].values
    
    # --- PCA Dimension Reduction Logic ---
    if use_pca:
        # We specify pca_variance (e.g., 0.90) to let scikit-learn automatically 
        # select the number of components needed to explain 90% of the variance.
        pca = PCA(n_components=pca_variance)
        window_returns = pca.fit_transform(window_returns)
        
    mees_val = calculate_mees_core(window_returns, P=P, alpha=alpha, is_pca=use_pca)
    
    return mees_val

def rolling_mees_daily(tickers, start_date, end_date, window=30, P=4, alpha=0.10, use_pca=False, pca_variance=0.90):
    """Main function: Iterates through trading days and aggregates MEES results."""
    print(f"Fetching data for {len(tickers)} tickers...")
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Close']
    returns_df = data.pct_change().dropna(how='all').fillna(0)
    
    eval_dates = returns_df.index[window - 1:]
    mees_results = pd.Series(index=eval_dates, dtype=float, name="MEES")
    
    print(f"Calculating daily rolling MEES (PCA={use_pca})...")
    
    for current_date in eval_dates:
        mees_val = calculate_single_day_mees(
            target_date=current_date, 
            returns_df=returns_df, 
            window=window, 
            P=P, 
            alpha=alpha,
            use_pca=use_pca,
            pca_variance=pca_variance
        )
        mees_results.loc[current_date] = mees_val
        
    print("Calculation complete.")
    return mees_results.dropna()


# --- Example Usage ---
if __name__ == "__main__":
    # Custom ticker list
    custom_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA']

    # Run the daily rolling function
    daily_mees_series = rolling_mees_daily(
        tickers=custom_tickers,
        start_date="2025-01-01",
        end_date="2025-12-31",
        window=30,  # 30-day lookback window
        P=4  # Target portfolios to extract
    )

    print("\nDaily MEES Results:")
    print(daily_mees_series.tail(10))  # Print the last 10 days