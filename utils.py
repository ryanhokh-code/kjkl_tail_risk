import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from config import PARAM_FILE, CACHE_DIR, DB_CONNECTION_STRING

try:
    from sqlalchemy import create_engine
except ImportError:
    create_engine = None

# =============================================================================
# DATA FETCHING
# =============================================================================
def fetch_financial_data(tickers, start_date, end_date):
    """
    Fetches daily closing prices. First attempts PostgreSQL DB read.
    If DB is not configured, connection fails, or data is missing, falls back to yfinance.
    Returns a standardized DataFrame indexed by timezone-naive dates.
    """
    df_db = None
    tickers_list = list(tickers) if isinstance(tickers, (list, tuple, pd.Index)) else [tickers]
    
    if DB_CONNECTION_STRING and create_engine:
        try:
            print(f"Attempting to fetch {len(tickers_list)} tickers from PostgreSQL database...")
            engine = create_engine(DB_CONNECTION_STRING)
            
            # Note for user: Replace this query with your exact table schema.
            # Assuming table `daily_bars` with columns `date`, `ticker`, `close`
            placeholders = ', '.join([f"'{t}'" for t in tickers_list])
            query = f"""
                SELECT date, ticker, close 
                FROM daily_bars 
                WHERE ticker IN ({placeholders})
                AND date >= '{start_date}' AND date <= '{end_date}'
            """
            
            raw_db = pd.read_sql(query, engine)
            if not raw_db.empty:
                raw_db['date'] = pd.to_datetime(raw_db['date'])
                df_db = raw_db.pivot(index='date', columns='ticker', values='close')
                # Remove timezone if any
                if df_db.index.tz is not None:
                    df_db.index = df_db.index.tz_localize(None)
                print(f"Successfully loaded {df_db.shape[0]} dates from database.")
            else:
                print("  -> Database returned no records for this query.")
        except Exception as e:
            print(f"  -> Database fetch failed: {e}. Falling back to yfinance.")
            df_db = None

    # Check if we need to fallback
    missing_tickers = []
    if df_db is None:
        missing_tickers = tickers_list
    else:
        missing_tickers = [t for t in tickers_list if t not in df_db.columns or df_db[t].isna().all()]
        
    if missing_tickers:
        print(f"Fetching {len(missing_tickers)} missing tickers via yfinance fallback...")
        try:
            df_yf = yf.download(missing_tickers, start=start_date, end=end_date, progress=False)['Close']
            
            # If a single ticker was passed to yf.download, it returns a Series
            if isinstance(df_yf, pd.Series):
                df_yf = df_yf.to_frame(name=missing_tickers[0])
                
            if df_yf.index.tz is not None:
                df_yf.index = df_yf.index.tz_localize(None)
                
            if df_db is None:
                df_db = df_yf
            else:
                # Merge the fallback data into the main DB dataframe
                df_db = pd.concat([df_db, df_yf], axis=1)
                
        except Exception as e:
            print(f"  -> Failed to fetch data from yfinance: {e}")
            
    # Clean up empty columns and sort index
    if df_db is not None:
        df_db = df_db.dropna(axis=1, how='all')
        df_db = df_db.sort_index()
        
    return df_db


# =============================================================================
# CACHING LOGIC
# =============================================================================
def get_cache_path(market_ticker, signal_name, params_dict=None):
    safe_ticker = market_ticker.replace('^', '')
    market_dir = os.path.join(CACHE_DIR, safe_ticker)
    os.makedirs(market_dir, exist_ok=True)
    
    if not params_dict:
        return os.path.join(market_dir, f"{signal_name.lower()}.parquet")
        
    param_strs = []
    for k, v in params_dict.items():
        if isinstance(v, float):
            param_strs.append(f"{k[0]}{v:.2f}")
        elif isinstance(v, int):
            param_strs.append(f"{k[0]}{v}")
        else:
            param_strs.append(f"{k[0]}{v}")
            
    p_string = "_".join(param_strs)
    fname = f"{signal_name.lower()}_{p_string}.parquet"
    return os.path.join(market_dir, fname)

def load_parquet_cache(market_ticker, signal_name, params_dict=None):
    path = get_cache_path(market_ticker, signal_name, params_dict)
    if os.path.exists(path):
        try:
            df = pd.read_parquet(path)
            if signal_name in df.columns:
                return df[signal_name].dropna()
        except Exception:
            pass
    return pd.Series(dtype=float)

def save_parquet_cache(market_ticker, signal_name, series, params_dict=None):
    path = get_cache_path(market_ticker, signal_name, params_dict)
    df = pd.DataFrame({signal_name: series})
    df.to_parquet(path, engine='fastparquet')


# =============================================================================
# PARAMETER MANAGEMENT
# =============================================================================
def load_optimized_params(market_ticker):
    if not os.path.exists(PARAM_FILE):
        return {}
        
    with open(PARAM_FILE, 'r') as f:
        try:
            all_params = json.load(f)
            return all_params.get(market_ticker, {})
        except json.JSONDecodeError:
            return {}

def save_optimized_params(market_ticker, best_kj, best_kl):
    if os.path.exists(PARAM_FILE):
        with open(PARAM_FILE, 'r') as f:
            try:
                all_params = json.load(f)
            except json.JSONDecodeError:
                all_params = {}
    else:
        all_params = {}
        
    if market_ticker not in all_params:
        all_params[market_ticker] = {}
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    if best_kj is not None:
        all_params[market_ticker]['KJ_Lambda'] = {
            'window': best_kj['window'],
            'quantile': best_kj['quantile'],
            'last_updated': date_str
        }
        
    if best_kl is not None:
        all_params[market_ticker]['KL_MEES'] = {
            'window': best_kl['window'],
            'n_pca': best_kl['n_pca'],
            'alpha': best_kl['alpha'],
            'last_updated': date_str
        }
        
    with open(PARAM_FILE, 'w') as f:
        json.dump(all_params, f, indent=4)
        
    print(f"\nSaved optimized parameters to {PARAM_FILE}")


# =============================================================================
# MATH & OPTIMIZATION HELPERS (from KL Tail Risk)
# =============================================================================
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

def map_pca_weights_to_assets(w_pca, pca_model):
    """Maps the optimized PCA weights back to the original asset space."""
    w_asset = np.dot(w_pca, pca_model.components_)

    # Normalize weights so the absolute gross exposure equals 1
    total_exposure = np.sum(np.abs(w_asset))
    if total_exposure > 0:
        w_asset = w_asset / total_exposure

    return w_asset


# =============================================================================
# UI HELPERS
# =============================================================================
def get_severity_rating(percentile):
    if percentile > 99:
        return {'level': 'Extreme', 'color': '#d32f2f'} # Red
    elif percentile > 95:
        return {'level': 'High', 'color': '#f57c00'} # Orange
    elif percentile > 90:
        return {'level': 'Elevated', 'color': '#fbc02d'} # Yellow
    else:
        return {'level': 'Normal', 'color': '#388e3c'} # Green

def calculate_efficiency_ratio(series, window=21):
    """
    Kaufman Efficiency Ratio (ER).
    ER = Total Directional Move / Sum of Absolute Daily Changes
    Ranges from 0 (all noise) to 1 (all signal/trend).
    """
    direction = series.diff(window).abs()
    volatility = series.diff().abs().rolling(window=window).sum()
    return (direction / volatility).replace([np.inf, -np.inf], np.nan)

def calculate_signal_stability(series, window=21):
    """
    Signal-to-Noise Stability (Rolling Z-Score equivalent).
    Ratio of moving average to moving standard deviation.
    """
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    return (rolling_mean / rolling_std).replace([np.inf, -np.inf], np.nan)

def calculate_lead_time_index(signal_series, price_series, threshold_pct=90, horizon=21, drawdown_threshold=-0.05):
    """
    Calculates the average lead time (in days) between an alert and a drawdown event.
    Threshold_pct: The percentile of the signal to trigger an 'alert'.
    Horizon: Look-ahead window for the crash.
    """
    if signal_series.empty or price_series.empty:
        return np.nan
        
    # Align and handle timezone/nan
    common_idx = signal_series.index.intersection(price_series.index)
    sig = signal_series.loc[common_idx]
    price = price_series.loc[common_idx]
    
    threshold = np.percentile(sig, threshold_pct)
    alerts = sig[sig >= threshold].index
    
    # Calculate forward max drawdown
    fwd_returns = price.pct_change(horizon).shift(-horizon)
    # Actually we want the max drawdown in the NEXT horizon days
    # Let's simplify: find the minimum return in the next 'horizon' days
    fwd_min_ret = []
    for i in range(len(price)):
        window = price.iloc[i:i+horizon+1]
        if len(window) < 2:
            fwd_min_ret.append(np.nan)
        else:
            ret_from_start = window / window.iloc[0] - 1
            fwd_min_ret.append(ret_from_start.min())
            
    fwd_min_series = pd.Series(fwd_min_ret, index=price.index)
    crashes = fwd_min_series[fwd_min_series <= drawdown_threshold].index
    
    lead_times = []
    for alert_date in alerts:
        # Find the first crash that happens AFTER this alert date
        future_crashes = crashes[crashes >= alert_date]
        if not future_crashes.empty:
            lead_day = (future_crashes[0] - alert_date).days
            lead_times.append(lead_day)
            
    if not lead_times:
        return 0.0
    return np.mean(lead_times)

def calculate_accuracy_metrics(signal_series, price_series, threshold_pct=90, horizon=21, drawdown_threshold=-0.03):
    """
    Calculates Precision, Recall, and F1 score for the tail risk alerts.
    """
    if signal_series.empty or price_series.empty:
        return {'precision': 0, 'recall': 0, 'f1': 0, 'fpr': 0}

    common_idx = signal_series.index.intersection(price_series.index)
    sig = signal_series.loc[common_idx]
    price = price_series.loc[common_idx]
    
    threshold = np.percentile(sig, threshold_pct)
    is_alert = sig >= threshold
    
    # Define a 'True Event' as a drawdown > threshold in the next horizon
    fwd_min_ret = []
    for i in range(len(price)):
        window = price.iloc[i:i+horizon+1]
        if len(window) < 2:
            fwd_min_ret.append(False)
        else:
            ret_from_start = window / window.iloc[0] - 1
            fwd_min_ret.append(ret_from_start.min() <= drawdown_threshold)
    
    is_crash = pd.Series(fwd_min_ret, index=price.index)
    
    tp = (is_alert & is_crash).sum()
    fp = (is_alert & ~is_crash).sum()
    fn = (~is_alert & is_crash).sum()
    tn = (~is_alert & ~is_crash).sum()
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    
    return {
        'precision': np.round(precision, 4),
        'recall': np.round(recall, 4),
        'f1': np.round(f1, 4),
        'fpr': np.round(fpr, 4),
        'tp': int(tp),
        'fp': int(fp),
        'fn': int(fn)
    }
