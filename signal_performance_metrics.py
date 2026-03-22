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
    calculate_accuracy_metrics,
    calculate_roc_auc
)

def run_performance_analysis(market, window=21, threshold_pct=90):
    print(f"\n" + "="*90)
    print(f"SIGNAL PERFORMANCE SCORECARD: {MARKET_UNIVERSES[market]['name']} ({market})")
    print("="*90)
    
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

    # Fetch Price Data for LTI, Accuracy and AUC
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

        # ROC-AUC
        auc = calculate_roc_auc(series, price_series)
        
        results[name] = {
            'avg_er': er.mean(),
            'avg_stab': stability.mean(),
            'lti': lti,
            'acc': acc,
            'auc': auc
        }
        
    # 3. Print Performance Tables
    print(f"\n[SECTION 1: SIGNAL-TO-NOISE & STABILITY]")
    print(f"{'Measure':<15} | {'Avg Efficiency (ER)':<20} | {'Stability (S-Score)':<20}")
    print("-" * 65)
    for name, res in results.items():
        print(f"{name:<15} | {res['avg_er']:.4f} {'(Healthy)' if res['avg_er'] > 0.3 else '(Noisy)':<9} | {res['avg_stab']:.4f}")

    print(f"\n[SECTION 2: ACCURACY & LEAD-TIME (Threshold: {threshold_pct}th Pct)]")
    print(f"{'Measure':<15} | {'ROC-AUC':<10} | {'Avg Lead Time':<15} | {'Precision':<10} | {'Recall':<10} | {'F1 Score':<10}")
    print("-" * 85)
    for name, res in results.items():
        acc = res['acc']
        auc_str = f"{res['auc']:.4f}" if not np.isnan(res['auc']) else "N/A"
        print(f"{name:<15} | {auc_str:<10} | {res['lti']:.1f} Days      | {acc['precision']:<10} | {acc['recall']:<10} | {acc['f1']:<10}")

    print("\n" + "="*90)
    print("INTERPRETATION & STRATEGIC GUIDE")
    print("="*90)
    print(f"""
1. ROC-AUC (THRESHOLD-INDEPENDENT QUALITY):
   - Definition: The probability the signal ranks a 'crash' day higher than a 'normal' day.
   - Strategic Use: 
     * AUC > 0.70: Excellent. The signal is inherently predictive at almost any threshold.
     * AUC 0.60 - 0.70: Good. Reliable for tail risk but requires a careful threshold choice.
     * AUC < 0.55: Weak. The signal is nearly random; do not trade without heavy filtering.

2. LEAD-TIME INDEX (LTI):
   - Definition: Avg days between a {threshold_pct}th percentile alert and a -5% drawdown.
   - Strategic Use: 
     * LTI > 10 Days: A "Structural Warmer". Plenty of time to de-risk or hedge.
     * LTI < 5 Days: A "Tactical Trigger". High urgency; immediate protection required.

3. HISTORICAL ACCURACY (PRECISION & RECALL):
   - PRECISION (Hit Rate): % of alerts followed by a -3% move in 21 days.
     * > 0.60: Highly Reliable. Trust the alerts blindly.
     * < 0.40: High False Positive rate. Requires secondary confirmation (e.g. Volatility).
   - RECALL (Capture Ratio): % of crashes that were predicted by an alert.

4. SNR & STABILITY:
   - EFFICIENCY RATIO (ER): > 0.3 means the signal is trending purposefully.
   - STABILITY: High stability means the risk level is sticking, not just flashing.

SCORECARD SUMMARY:
- High AUC + High Lead Time = Ideal Macro Hedge Signal.
- High AUC + Low Lead Time = Ideal Tactical Protection Signal.
- Low AUC + Moderate SNR = Pure Noise or Overfitting; handle with caution.
    """)

def main():
    parser = argparse.ArgumentParser(description="Signal Performance Scorecard (SNR, LTI, Accuracy, AUC)")
    parser.add_argument('--market', type=str, default='^GSPC', help='Market ticker (default: ^GSPC)')
    parser.add_argument('--window', type=int, default=21, help='Lookback window for SNR (default: 21)')
    parser.add_argument('--threshold', type=int, default=90, help='Percentile threshold for alerts (default: 90)')
    args = parser.parse_args()
    
    run_performance_analysis(args.market, args.window, args.threshold)

if __name__ == "__main__":
    main()
