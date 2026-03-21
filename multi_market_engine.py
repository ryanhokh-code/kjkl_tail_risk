import argparse
from datetime import datetime
from config import MARKET_UNIVERSES, generate_default_market_tickers
from self_optimizer import optimize_kj_measure, optimize_kl_measure, save_optimized_params
from backtest_tail_risk_daily import TailRiskBacktester
import warnings
warnings.filterwarnings("ignore")

def main():
    parser = argparse.ArgumentParser(description="Multi-Market Tail Risk Optimization and Backtesting Engine")
    parser.add_argument('--start', type=str, default='2018-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2026-03-21', help='End date (YYYY-MM-DD)')
    parser.add_argument('--skip-kl', action='store_true', help='Skip KL optimization (it can be slow)')
    parser.add_argument('--full-recompute', action='store_true', help='Force full recomputation of signals (skip cache)')
    
    args = parser.parse_args()
    
    mode_str = 'full' if args.full_recompute else 'incremental'

    # Define a slightly smaller grid for multi-market runs to save time
    kj_grid = {
        'window': [30, 60, 90],
        'quantile': [0.05, 0.10]
    }
    
    kl_grid = {
        'window': [30],
        'n_pca': [4],
        'alpha': [0.10]
    }

    markets = list(MARKET_UNIVERSES.keys())

    print(f"Starting Multi-Market Compute Engine")
    print(f"Mode: {mode_str.upper()}")
    print(f"Period: {args.start} to {args.end}\n")

    for market in markets:
        market_name = MARKET_UNIVERSES[market]['name']
        print(f"\n==========================================================")
        print(f"Processing Market: {market_name} ({market})")
        print(f"==========================================================\n")
        
        tickers = generate_default_market_tickers(market)
        
        # 1. OPTIMIZATION PHASE
        print(f"--- Phase 1: Optimization for {market} ---")
        bt_opt = TailRiskBacktester(
            tickers=tickers,
            market_ticker=market,
            start_date=args.start,
            end_date=args.end,
            horizons=[1, 5, 10, 21],
            load_optimized_params=False
        )
        bt_opt.fetch_data()
        bt_opt.prepare_forward_returns()
        
        best_kj = optimize_kj_measure(bt_opt, kj_grid)
        best_kl = None
        if not args.skip_kl:
            best_kl = optimize_kl_measure(bt_opt, kl_grid)
        else:
            print("Skipping KL optimization.")
            
        save_optimized_params(market, best_kj, best_kl)
        
        # 2. SIGNAL GENERATION PHASE (Caching)
        print(f"\n--- Phase 2: Signal Generation (Caching) for {market} ---")
        bt_eval = TailRiskBacktester(
            tickers=tickers,
            market_ticker=market,
            start_date=args.start,
            end_date=args.end,
            horizons=[1, 5, 10, 21],
            load_optimized_params=True
        )
        bt_eval.fetch_data()
        
        bt_eval.generate_signals(mode=mode_str)
        
    print("\n---------------------------------------------------------")
    print("Engine complete. Signals are cached in the cache/ directory.")
    print("Run `python multi_market_analytics.py` to generate the risk reports.")
    print("---------------------------------------------------------")

if __name__ == "__main__":
    main()
