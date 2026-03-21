import argparse
import warnings
import concurrent.futures
from datetime import datetime
from config import MARKET_UNIVERSES, generate_default_market_tickers
from self_optimizer import optimize_kj_measure, optimize_kl_measure, save_optimized_params
from backtest_tail_risk_daily import TailRiskBacktester

warnings.filterwarnings("ignore")

def process_single_market(market, args, mode_str, kj_grid, kl_grid):
    """Function to process a single market, designed for parallel execution."""
    market_name = MARKET_UNIVERSES[market]['name']
    print(f"\n[START] Processing Market: {market_name} ({market})")
    
    try:
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
        
        # Check if enough data was fetched
        if bt_opt.stock_returns is None or bt_opt.stock_returns.empty:
            print(f"Error: No data available for {market}. Skipping.")
            return f"{market}: Failed (No Data)"

        bt_opt.prepare_forward_returns()
        
        best_kj = optimize_kj_measure(bt_opt, kj_grid)
        best_kl = None
        if not args.skip_kl:
            best_kl = optimize_kl_measure(bt_opt, kl_grid)
        else:
            print(f"Skipping KL optimization for {market}.")
            
        save_optimized_params(market, best_kj, best_kl)
        
        # 2. SIGNAL GENERATION PHASE (Caching)
        print(f"--- Phase 2: Signal Generation (Caching) for {market} ---")
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
        
        print(f"[FINISH] Successfully processed {market_name} ({market})")
        return f"{market}: Success"
    except Exception as e:
        print(f"[ERROR] Failed to process {market}: {e}")
        return f"{market}: Error ({e})"

def main():
    parser = argparse.ArgumentParser(description="Multi-Market Tail Risk Optimization and Backtesting Engine")
    parser.add_argument('--start', type=str, default='2018-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2026-03-21', help='End date (YYYY-MM-DD)')
    parser.add_argument('--skip-kl', action='store_true', help='Skip KL optimization (it can be slow)')
    parser.add_argument('--full-recompute', action='store_true', help='Force full recomputation of signals (skip cache)')
    parser.add_argument('--workers', type=int, default=None, help='Number of parallel workers (default: CPU count)')
    
    args = parser.parse_args()
    mode_str = 'full' if args.full_recompute else 'incremental'

    # Define grids
    kj_grid = {'window': [30, 60, 90], 'quantile': [0.05, 0.10]}
    kl_grid = {'window': [30], 'n_pca': [4], 'alpha': [0.10]}

    markets = list(MARKET_UNIVERSES.keys())

    print(f"Starting Multi-Market Compute Engine (PARALLEL)")
    print(f"Mode: {mode_str.upper()}")
    print(f"Period: {args.start} to {args.end}")
    print(f"Markets: {len(markets)}\n")

    start_time = datetime.now()

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        # Create futures for each market
        future_to_market = {
            executor.submit(process_single_market, m, args, mode_str, kj_grid, kl_grid): m 
            for m in markets
        }
        
        results = []
        for future in concurrent.futures.as_completed(future_to_market):
            market = future_to_market[future]
            try:
                res = future.result()
                results.append(res)
            except Exception as exc:
                print(f"Market {market} generated an exception: {exc}")
                results.append(f"{market}: Exception")

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "="*60)
    print(f"Multi-Market Engine Execution Summary")
    print("="*60)
    print(f"Total Duration: {duration}")
    for r in results:
        print(f" - {r}")
    print("="*60)
    print("\nEngine complete. Run `python multi_market_analytics.py` to generate the risk reports.")

if __name__ == "__main__":
    main()
