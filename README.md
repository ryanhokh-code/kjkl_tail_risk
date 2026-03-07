# KJ & KL Tail Risk Monitor

A **production-grade, self-improving tail risk monitoring framework** for global equity markets, built on two academic risk measures — Kelly-Jiang (KJ, 2014) and Law-Li-Yu KL MEES (2021). The system automatically optimizes parameters per market, backtests statistical significance, and generates daily monitoring dashboards for equity hedge fund risk management.

---

## Academic Background

| Measure | Reference | Key Idea |
|---|---|---|
| **KJ Lambda (λ)** | Kelly & Jiang (2014), *Tail Risk and Asset Prices*, RFS | Hill's power-law estimator applied to the cross-section of firm residuals to measure the collective fatness of the left tail |
| **KL MEES** | Law, Li & Yu (2021), *An alternative nonparametric tail risk measure*, Quantitative Finance | Minimum Excess Expected Shortfall: sequentially extracts orthogonal portfolios that concentrate the cross-sectional tail downside |

---

## System Architecture

```
self_optimizer.py          ← Grid-searches best parameters per market
        │
        ▼
optimized_params.json      ← Persistent parameter store
        │
        ▼
multi_market_runner.py     ← Runs full 7-market backtest pipeline
        │
        ├── backtest_tail_risk_daily.py   ← Core engine (signals, regressions, hit rates)
        │         ├── compute_daily_kj_lambda()     → KJ rolling Lambda signal
        │         ├── compute_daily_kl_mees()       → KL MEES signal + PCA loadings
        │         ├── prepare_forward_returns()     → Return, Vol Ratio, Max Drawdown targets
        │         ├── run_regressions()             → HAC Newey-West OLS (Level + Velocity)
        │         └── compute_hit_rates()           → Empirical hit rate analysis
        │
        └── multi_market_report.html  ← Full backtest report with interpretation
        └── multi_market_report.md    ← Markdown version

daily_monitor.py           ← Daily live risk dashboard (run every day)
        └── daily_risk_summary.html   ← Today's severity readings for all markets
```

---

## Market Coverage

| Market | Index Proxy | Universe Size |
|---|---|---|
| 🇺🇸 US (S&P 500) | `^GSPC` | 44 stocks |
| 🇨🇳 China (CSI 300) | `000300.SS` | 40 stocks |
| 🇭🇰 Hong Kong (Hang Seng) | `^HSI` | 40 stocks |
| 🇹🇼 Taiwan (TAIEX) | `^TWII` | 40 stocks |
| 🇯🇵 Japan (Nikkei 225) | `^N225` | 40 stocks |
| 🇰🇷 Korea (KOSPI) | `^KS11` | 40 stocks |
| 🇪🇺 Europe (Euro Stoxx 50) | `^STOXX50E` | 40 stocks |

---

## Script Reference

### `kj_tail_risk_measure.py`
Original implementation of the Kelly-Jiang (2014) measure.
- **`fetch_financial_data()`** — Downloads daily price data via `yfinance`
- **`calculate_residuals()`** — CAPM regression to extract firm-specific residuals
- **`estimate_lambda()`** — Pools monthly cross-section residuals, applies Hill's estimator at the 5th-percentile threshold to produce `λ_t`
- **`calculate_tail_betas()`** — Stock-level sensitivity to `λ_t`
- **`plot_analysis()`** — λ time series and cross-sectional β bar chart

### `kl_tail_risk_measure.py`
Implementation of the Law-Li-Yu (2021) MEES measure.
- **`historical_var()`** — Historical VaR at the `alpha` level as tail threshold
- **`objective_excess_shortfall()`** — Minimization target: expected shortfall beyond VaR
- **`zero_covariance_constraint()`** — Enforces orthogonality between extracted MEES portfolios
- **`calculate_mees_core_weights()`** — SLSQP optimization loop extracting `P` orthogonal tail-minimizing portfolios
- **`map_pca_weights_to_assets()`** — Maps PCA-reduced space weights back to physical asset weights
- **`calculate_single_day_mees()`** — Computes MEES for a single day over a trailing window; returns PCA loadings for factor attribution
- **`compute_mees()`** — Rolls `calculate_single_day_mees` across the full time series; optionally returns first-PC loadings per day
- **`run_multi_horizon_regression()`** — Regresses future market returns at 1–12 month horizons against lagged MEES
- **`run_pipeline()`** — End-to-end standalone pipeline with visualization

### `backtest_tail_risk_daily.py`
Core backtesting engine — the central workhorse of the framework.
- **`compute_daily_kj_lambda()`** — Rolling CAPM residual pooling and Hill estimator to produce daily KJ lambda signal
- **`compute_daily_kl_mees()`** — Daily rolling MEES with PCA; stores per-day first-PC loadings for factor attribution
- **`prepare_forward_returns()`** — Builds three forward-looking targets per horizon:
  - `Return_{h}d` — Simple h-day forward return
  - `VolRatio_{h}d` — Future realized volatility / current realized volatility
  - `MaxDD_{h}d` — Worst intra-period trough: `min(price[t+1:t+h]) / price[t] - 1`
- **`generate_signals()`** — Computes KJ + KL signals; aligns with forward targets
- **`run_regressions()`** — Newey-West HAC OLS regressions (Level + 5-day Velocity) predicting returns, vol ratios, and max drawdown. Returns 3-tuple of DataFrames
- **`compute_hit_rates()`** — For days where the signal exceeds the 90th percentile historical threshold, computes:
  - % with negative future return (hit rate)
  - % with max drawdown < -1%, -2%, -3%
  - Mean return in high-signal vs. normal-signal regimes
- **`visualize_signals()`** — Time-series chart of market price vs. risk signal, with red-shaded high-risk regimes (> 90th percentile) and 50-day MA overlay

### `self_optimizer.py`
Parameter grid search for KJ and KL per market.
- **Objective**: Maximize the sum of absolute Newey-West t-statistics across horizons (1, 5, 10, 21 days) for both return and volatility regressions
- **KJ grid**: window ∈ {30, 60, 90}, quantile ∈ {0.01, 0.05, 0.10}
- **KL grid**: window ∈ {20, 30, 60}, n_pca ∈ {2, 4, 6}, alpha ∈ {0.05, 0.10, 0.15}
- Best params are saved to `optimized_params.json`

### `multi_market_runner.py`
Orchestrates the full 7-market optimization + backtest + reporting pipeline.
- Runs Phase 1 (optimization) and Phase 2 (backtesting) per market
- Generates plots to `export_img/`
- Outputs `multi_market_report.html` and `multi_market_report.md`

### `daily_monitor.py`
Lightweight daily monitoring dashboard.
- Loads optimized parameters from `optimized_params.json`
- Fetches the most recent 3 years of data per market
- Computes today's KJ Lambda and KL MEES
- Maps values to historical percentiles and severity levels
- Displays Top-5 risk contributing tickers (from KL MEES PCA eigenvectors)
- Outputs `daily_risk_summary.html`

---

## Quickstart

### 1. Install dependencies
```bash
pip install numpy pandas yfinance scipy scikit-learn statsmodels matplotlib tabulate
```

### 2. Optimize parameters for all markets
```bash
python multi_market_runner.py
```
This will run parameter optimization, backtesting, and generate `multi_market_report.html`.

### 3. Run daily monitoring (run each morning)
```bash
python daily_monitor.py
```
Opens `daily_risk_summary.html` with today's global risk readings.

### 4. Run standalone optimizer for a single market
```bash
python self_optimizer.py --market ^GSPC --start 2018-01-01 --end 2026-01-01
```

---

## Outputs

| File | Description |
|---|---|
| `optimized_params.json` | Best KJ + KL parameters per market |
| `multi_market_report.html` | Full HTML backtest report with regressions, hit rates, and drawdown analysis |
| `multi_market_report.md` | Markdown version of the backtest report |
| `daily_risk_summary.html` | Daily risk dashboard with severity ratings and factor attribution |
| `export_img/*.png` | Time-series charts per market with red-shaded high-risk zones |

---

## Risk Interpretation Guide

### Severity Levels

| Level | Percentile | Color | What it means |
|---|---|---|---|
| **Normal** | < 90th | 🟢 Green | Cross-sectional tail is within historical norms |
| **Elevated** | 90–95th | 🟡 Yellow | Tail distribution wider than usual; monitor closely |
| **High** | 95–99th | 🟠 Orange | Systemic tail risk elevated; reduce gross exposure |
| **Extreme** | > 99th | 🔴 Red | Crisis-level tail dispersion; defensive positioning warranted |

### How to Read the Regression Tables

| Column | Interpretation |
|---|---|
| `{Measure} Beta` | Directional slope: positive for vol/drawdown (higher risk → bigger drawdown), negative for returns (higher risk → worse returns) |
| `{Measure} t-stat` | Newey-West corrected: `|t| > 1.96` = significant at 95%; `> 2.58` = significant at 99% |
| `{Measure}_Vel Beta` | Incremental predictive power of the 5-day rate-of-change (momentum) of the signal |
| `Adj. R-squared` | Proportion of variation in future market outcomes explained by the model |

### How to Read Hit Rate Tables

| Column | Interpretation |
|---|---|
| `Hit Rate: Ret<0 (%)` | Of all days where signal was elevated, this % saw a negative return over the next N days |
| `Hit Rate: MaxDD<-X%` | Of all high-signal days, this % had a max intra-period drawdown exceeding the threshold |
| `Avg Ret (High Signal)` | Mean N-day return when signal is elevated — useful for sizing context |
| `Ret Spread (High-Normal, %)` | Return difference between high-signal and normal regimes; negative = signal predicts underperformance |

### Key Insight: Why Max Drawdown?

End-of-period N-day returns can look benign even after a severe shock because markets often partially recover. The `MaxDD_{h}d` target captures the **worst intra-period trough** — making it a much more reliable target for tail risk forecastability. A statistically significant negative beta on MaxDD means the signal is genuinely predictive of **actual crash severity**, not just directional bias.

---

## Self-Improvement Mechanism

The framework is designed to be re-run periodically:
1. `optimized_params.json` is updated each time `multi_market_runner.py` or `self_optimizer.py` is run
2. As more market data accumulates, the optimizer can discover better parameters
3. The daily monitor always uses the latest saved parameters

---

## Academic Citations

- Kelly, B., & Jiang, H. (2014). *Tail Risk and Asset Prices*. The Review of Financial Studies, 27(10), 2841–2871. https://doi.org/10.1093/rfs/hhu035
- Law, K.K.F., Li, W.K., & Yu, P.L.H. (2021). *An alternative nonparametric tail risk measure*. Quantitative Finance, 21(4), 685–696. https://doi.org/10.1080/14697688.2020.1787491