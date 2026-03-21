import numpy as np
import pandas as pd
import json
import os
import argparse
from datetime import datetime
from backtest_tail_risk_daily import TailRiskBacktester
from config import PARAM_FILE, MARKET_UNIVERSES, generate_default_market_tickers
import warnings

warnings.filterwarnings("ignore")

from utils import save_optimized_params

def optimize_kj_measure(bt, param_grid):
    print("\n--- Optimizing Kelly-Jiang (KJ) Measure ---")
    best_score = -np.inf
    best_params = None
    
    for window in param_grid['window']:
        for quantile in param_grid['quantile']:
            try:
                print(f"Testing KJ params: window={window}, quantile={quantile}...")
                lambdas = bt.compute_daily_kj_lambda(window=window, quantile=quantile)
                if len(lambdas) < 20: 
                    print("  -> Not enough valid signal data generated, skipping.")
                    continue
                    
                bt.signals = pd.DataFrame({'KJ_Lambda': lambdas})
                ret_df, vol_df, _ = bt.run_regressions('KJ_Lambda')
                
                # Objective Score: Sum of absolute Newey-West t-statistics across horizons
                score = ret_df['KJ_Lambda t-stat'].abs().sum() + vol_df['KJ_Lambda t-stat'].abs().sum()
                
                print(f"  -> Score: {score:.2f}")
                
                if score > best_score:
                    best_score = score
                    best_params = {'window': window, 'quantile': quantile, 'score': score}
            except Exception as e:
                print(f"  -> Error evaluating KJ {window}/{quantile}: {e}")
                
    if best_params:
        print(f"\nBest KJ Params: {best_params} (Score: {best_score:.2f})")
    return best_params

def optimize_kl_measure(bt, param_grid):
    print("\n--- Optimizing KL MEES Measure ---")
    best_score = -np.inf
    best_params = None
    
    for window in param_grid['window']:
        for n_pca in param_grid['n_pca']:
            for alpha in param_grid['alpha']:
                try:
                    print(f"Testing KL params: window={window}, n_pca={n_pca}, alpha={alpha}...")
                    mees = bt.compute_daily_kl_mees(window=window, n_pca=n_pca, alpha=alpha)
                    if len(mees) < 20:
                        print("  -> Not enough valid signal data generated, skipping.")
                        continue
                        
                    bt.signals = pd.DataFrame({'KL_MEES': mees})
                    ret_df, vol_df, _ = bt.run_regressions('KL_MEES')
                    
                    score = ret_df['KL_MEES t-stat'].abs().sum() + vol_df['KL_MEES t-stat'].abs().sum()
                    
                    print(f"  -> Score: {score:.2f}")
                    
                    if score > best_score:
                        best_score = score
                        best_params = {'window': window, 'n_pca': n_pca, 'alpha': alpha, 'score': score}
                except Exception as e:
                    print(f"  -> Error evaluating KL {window}/{n_pca}/{alpha}: {e}")
                    
    if best_params:
        print(f"\nBest KL Params: {best_params} (Score: {best_score:.2f})")
    return best_params




def main():
    parser = argparse.ArgumentParser(description="Self-Improving Tail Risk Measure Framework")
    parser.add_argument('--market', type=str, default='^GSPC', help='Market proxy ticker (e.g., ^GSPC, ^NDX)')
    parser.add_argument('--start', type=str, default='2018-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2026-02-27', help='End date (YYYY-MM-DD)')
    parser.add_argument('--skip-kl', action='store_true', help='Skip KL optimization (it can be slow)')
    
    args = parser.parse_args()
    
    tickers = generate_default_market_tickers(args.market)
    
    print(f"Starting optimizer for Market: {args.market}")
    print(f"Period: {args.start} to {args.end}")
    
    bt = TailRiskBacktester(
        tickers=tickers,
        market_ticker=args.market,
        start_date=args.start,
        end_date=args.end,
        horizons=[1, 5, 10, 21],
        load_optimized_params=False # Do not load existing params when optimizing
    )
    
    bt.fetch_data()
    bt.prepare_forward_returns()
    
    kj_grid = {
        'window': [30, 60, 90],
        'quantile': [0.01, 0.05, 0.10]
    }
    
    kl_grid = {
        'window': [20, 30, 60],
        'n_pca': [2, 4, 6],
        'alpha': [0.05, 0.10, 0.15]
    }
    
    best_kj = optimize_kj_measure(bt, kj_grid)
    
    best_kl = None
    if not args.skip_kl:
        best_kl = optimize_kl_measure(bt, kl_grid)
    else:
        print("\nSkipping KL MEES optimization...")
        
    save_optimized_params(args.market, best_kj, best_kl)
    print("\nOptimization Complete.")

if __name__ == "__main__":
    main()
