# KJ & KL Tail Risk Measures
Cross-sectional tail risk measure for financial market.

## KL Measure (MEES)
Refers to Keith K.F. Law, W.K. Li & Philip L.H. Yu (2021) An alternative nonparametric tail risk measure, Quantitative Finance, 21:4, 685-696, DOI: 10.1080/14697688.2020.1787491

This measure implements the Minimum Excess Expected Shortfall (MEES). It extracts independent factors that best explain the tail risk of a cross-section of assets, and uses these to forecast future market returns.

### KL Measure Flow & Functions (`kl_tail_risk_measure.py`)
The pipeline runs through the following steps:
1. **Data Retrieval**: Fetches daily stock prices and market prices (SPY) via `yfinance`.
2. **MEES Calculation (`calculate_single_day_mees`)**: Computes the daily rolling MEES value based on the previous 30 days of data.
   - `historical_var`: Calculates the historical Value-at-Risk (VaR) for a given portfolio to establish the tail threshold.
   - `objective_excess_shortfall`: This is the target minimization function, defining the excess shortfall beyond the VaR threshold.
   - `zero_covariance_constraint`: Ensures that each subsequent extracted MEES portfolio has zero covariance with all previously extracted portfolios.
   - `calculate_mees_core_weights`: Executes the SLSQP optimization loop to extract $P$ orthogonal portfolios that minimize excess expected shortfall.
   - `map_pca_weights_to_assets`: If PCA is enabled to reduce dimensionality before optimization, this function maps the resulting PCA-space weights back to physical asset weights.
3. **Multi-Horizon Regression (`run_multi_horizon_regression`)**: A predictive test that regresses future market returns across multiple horizons (1 to 12 months) against the lagged monthly MEES factor.
4. **Beta Persistence Testing (`test_beta_persistence`)**: Checks whether the cross-sectional exposure (beta) to the MEES factor is persistent over time. 
   - `calculate_rolling_betas`: Computes rolling betas for each individual stock against the MEES factor using a predefined window (e.g., 24 or 12 months).
5. **Visualizations**: 
   - `plot_mees_timeseries`: Plots the monthly aggregated MEES factor over time.
   - `plot_rolling_betas`: Plots the rolling betas for selected stocks to visualize changes in tail risk sensitivity.

## KJ Measure
Refers to Kelly, B., & Jiang, H. (2014). Tail Risk and Asset Prices. The Review of Financial Studies, 27(10), 2841–2871. https://doi.org/10.1093/rfs/hhu035

This measure applies Hill’s power-law estimator to the cross-section of firm-specific daily returns to construct a monthly aggregate tail risk factor ($\lambda_t$).

### KJ Measure Flow & Functions (`kj_tail_risk_measure.py`)
The pipeline follows a direct sequential process, heavily utilizing the `TailRiskAnalyzer` class:
1. **Data Retrieval (`fetch_financial_data`)**: An independent function fetching daily price data and calculating daily returns for both the stocks and a market proxy (e.g., SPY). 
2. **Residual Calculation (`calculate_residuals`)**: Regresses daily asset returns against market returns to extract the firm-specific residuals, isolating firm-level tail events from broad market movements.
3. **Lambda Estimation (`estimate_lambda`)**: Pools the cross-section of residuals month-by-month, identifies values below the 5th percentile threshold ($u_t$), and applies Hill's power-law index to produce a monthly common tail risk factor ($\lambda_t$).
4. **Tail Beta Calculation (`calculate_tail_betas`)**: Estimates the sensitivity (beta) of each individual stock to the aggregate tail factor. Regresses the monthly stock returns against the lagged $\lambda_t$.
5. **Analysis & Plotting (`plot_analysis`)**: Generates two charts: 
   - the time series of the estimated $\lambda_t$
   - a bar chart showing the predictive cross-sectional tail exposure ($\beta_i$) for each stock.