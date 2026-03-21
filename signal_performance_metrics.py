import pandas as pd
import numpy as np
import os
import argparse
from datetime import datetime
from config import MARKET_UNIVERSES, PARAM_FILE
from utils import (
    load_parquet_cache, 
    load_optimized_params, 
    calculate_efficiency_ratio, 
    calculate_signal_stability,
    fetch_financial_data,
    calculate_lead_time_index,
    calculate_accuracy_metrics
)

def run_performance_analysis(market, window=21, threshold_pct=90):
    print(f"\n" + "="*80)
    print(f"SIGNAL PERFORMANCE SCORECARD: {MARKET_UNIVERSES[market]['name']} ({market})")
    print("="*80)
    
    # 1. Load Parameters and Signals
    params = load_optimized_params(market)
    if not params:
        print(f"Error: No optimized parameters found for {market}. Run multi_market_engine first.")
        return

    # Load Signal Data
    kj_p = params.get('KJ_Lambda', {}).copy()
    kj_p.pop('last_updated', None)
    kj_series = load_parquet_cache(market, "KJ_Lambda", kj_p)
    
    kl_p = params.get('KL_MEES', {}).copy()
    kl_p.pop('last_updated', None)
    kl_series = load_parquet_cache(market, "KL_MEES", kl_p)
    
    if kj_series.empty and kl_series.empty:
        print(f"Error: No cached signals found for {market}.")
        return

    # Fetch Price Data for LTI and Accuracy
    # Use wide enough range to cover the signals
    all_dates = pd.concat([kj_series, kl_series]).index
    start_str = all_dates.min().strftime('%Y-%m-%d')
    end_str = all_dates.max().strftime('%Y-%m-%d')
    price_df = fetch_financial_data(market, start_str, end_str)
    
    if price_df is None or price_df.empty:
        print(f"Error: Could not fetch price data for {market}.")
        return
    price_series = price_df[market]

    # 2. Performance Calculations
    results = {}
    for name, series in [("KJ_Lambda", kj_series), ("KL_MEES", kl_series)]:
        if series.empty: continue
        
        # SNR
        er = calculate_efficiency_ratio(series, window=window)
        stability = calculate_signal_stability(series, window=window)
        
        # LTI
        lti = calculate_lead_time_index(series, price_series, threshold_pct=threshold_pct)
        
        # Accuracy
        acc = calculate_accuracy_metrics(series, price_series, threshold_pct=threshold_pct)
        
        results[name] = {
            'avg_er': er.mean(),
            'avg_stab': stability.mean(),
            'lti': lti,
            'acc': acc
        }
        
    # 3. Print Performance Tables
    print(f"\n[SECTION 1: SIGNAL-TO-NOISE & STABILITY]")
    print(f"{'Measure':<15} | {'Avg Efficiency (ER)':<20} | {'Stability (S-Score)':<20}")
    print("-" * 60)
    for name, res in results.items():
        print(f"{name:<15} | {res['avg_er']:.4f} {'(Healthy)' if res['avg_er'] > 0.3 else '(Noisy)':<9} | {res['avg_stab']:.4f}")

    print(f"\n[SECTION 2: LEAD-TIME & ACCURACY (Threshold: {threshold_pct}th Pct)]")
    print(f"{'Measure':<15} | {'Avg Lead Time':<15} | {'Precision':<10} | {'Recall':<10} | {'F1 Score':<10}")
    print("-" * 70)
    for name, res in results.items():
        acc = res['acc']
        print(f"{name:<15} | {res['lti']:.1f} Days      | {acc['precision']:<10} | {acc['recall']:<10} | {acc['f1']:<10}")

    print("\n" + "="*80)
    print("INTERPRETATION & STRATEGIC GUIDE")
    print("="*80)
    print(f"""
1. LEAD-TIME INDEX (LTI):
   - Definition: Avg days between a {threshold_pct}th percentile alert and a -5% drawdown.
   - Strategic Use: 
     * LTI > 10 Days: A "Structural Warmer". Plenty of time to de-risk or hedge.
     * LTI < 5 Days: A "Tactical Trigger". High urgency; immediate protection required.

2. HISTORICAL ACCURACY (PRECISION & RECALL):
   - PRECISION (Hit Rate): % of alerts followed by a -3% move in 21 days.
     * > 0.60: Highly Reliable. Trust the alerts blindly.
     * < 0.40: High False Positive rate. Requires secondary confirmation (e.g. Volatility).
   - RECALL (Capture Ratio): % of crashes that were predicted by an alert.
     * > 0.80: Excellent sensitivity. The model misses very few crashes.
   - F1 SCORE: The geometric balance. Values > 0.50 are considered strong for tail risk.

3. SNR & STABILITY:
   - EFFICIENCY RATIO (ER): > 0.3 means the signal is trending purposefully.
   - STABILITY: High stability means the risk level is sticking, not just flashing.

SCORECARD SUMMARY:
- High Accuracy + High Lead Time = Ideal Macro Hedge Signal.
- High Accuracy + Low Lead Time = Ideal Tactical Protection Signal.
- Low Accuracy + High SNR = "Early Warning" but prone to false alarms.
    """)

def main():
    parser = argparse.ArgumentParser(description="Signal Performance Scorecard (SNR, LTI, Accuracy)")
    parser.add_argument('--market', type=str, default='^GSPC', help='Market ticker (default: ^GSPC)')
    parser.add_argument('--window', type=int, default=21, help='Lookback window for SNR (default: 21)')
    parser.add_argument('--threshold', type=int, default=90, help='Percentile threshold for alerts (default: 90)')
    args = parser.parse_args()
    
    run_performance_analysis(args.market, args.window, args.threshold)

if __name__ == "__main__":
    main()
