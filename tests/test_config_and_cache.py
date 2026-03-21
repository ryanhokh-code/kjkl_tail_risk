import os
import shutil
import pytest
import pandas as pd
from datetime import datetime

# Tests must run from the project root.
from config import MARKET_UNIVERSES, generate_default_market_tickers, PARAM_FILE, CACHE_DIR
from backtest_tail_risk_daily import TailRiskBacktester

def test_config_imports():
    """Verify that configuration constants and functions are correctly exported."""
    assert isinstance(MARKET_UNIVERSES, dict)
    assert '^GSPC' in MARKET_UNIVERSES
    
    tickers = generate_default_market_tickers('^GSPC')
    assert isinstance(tickers, list)
    assert len(tickers) > 10
    
    assert isinstance(PARAM_FILE, str)
    assert isinstance(CACHE_DIR, str)

def test_signal_caching_roundtrip():
    """Verify that Parquet caching works in full vs incremental mode."""
    # We use a very short date range on a tiny universe to keep the test fast.
    test_market = '^IXIC' # We will spoof this for speed
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    test_start = '2024-01-01'
    test_end = '2024-04-01'
    test_cache_dir = os.path.join(CACHE_DIR, 'IXIC')
    
    # 1. Clean up any existing cache for this test market
    if os.path.exists(test_cache_dir):
        shutil.rmtree(test_cache_dir)
        
    bt = TailRiskBacktester(
        tickers=test_tickers,
        market_ticker=test_market,
        start_date=test_start,
        end_date=test_end,
        horizons=[1],
        load_optimized_params=False
    )
    
    # Force tiny windows for fast computation
    bt.params['KJ_Lambda']['window'] = 20
    bt.params['KL_MEES']['window'] = 20
    bt.params['KL_MEES']['n_pca'] = 2
    
    bt.fetch_data()
    
    # 2. Run full compute
    full_kj = bt.compute_daily_kj_lambda(mode='full')
    
    # Verify cache file was created
    cache_file = os.path.join(test_cache_dir, 'kj_lambda.parquet')
    assert os.path.exists(cache_file), f"Cache file not created at {cache_file}"
    
    # 3. Read raw Parquet to verify struct
    df_cache = pd.read_parquet(cache_file)
    assert 'kj_lambda' in df_cache.columns
    assert len(df_cache) == len(full_kj)
    
    # 4. Run incremental compute
    inc_kj = bt.compute_daily_kj_lambda(mode='incremental')
    
    # Verify the results match structurally and numerically
    assert len(inc_kj) == len(full_kj)
    pd.testing.assert_series_equal(full_kj, inc_kj)
    
    # Clean up
    if os.path.exists(test_cache_dir):
        shutil.rmtree(test_cache_dir)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
