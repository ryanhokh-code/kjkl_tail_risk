import numpy as np
import pandas as pd
import json
import os
import concurrent.futures
from datetime import datetime, timedelta
import yfinance as yf
from config import MARKET_UNIVERSES, generate_default_market_tickers, PARAM_FILE
from backtest_tail_risk_daily import TailRiskBacktester
import warnings
import argparse
warnings.filterwarnings("ignore")

from utils import get_severity_rating

def evaluate_single_market(market, all_params, start_str, end_str):
    """Evaluates a single market for daily risk metrics."""
    market_name = MARKET_UNIVERSES[market]['name']
    results = {
        'market': market,
        'market_name': market_name,
        'latest_kj': None,
        'pct_kj': None,
        'sev_kj': None,
        'latest_kl': None,
        'pct_kl': None,
        'sev_kl': None,
        'kl_attribution_html': ""
    }
    
    print(f"Evaluating: {market_name}")
    
    if market not in all_params:
        print(f"  -> No optimized parameters found for {market}. Skipping.")
        return results
        
    try:
        tickers = generate_default_market_tickers(market)
        
        bt = TailRiskBacktester(
            tickers=tickers,
            market_ticker=market,
            start_date=start_str,
            end_date=end_str,
            horizons=[], # Not running regressions
            load_optimized_params=True
        )
        bt.fetch_data()
        
        if 'KJ_Lambda' in all_params.get(market, {}):
            try:
                lambdas = bt.compute_daily_kj_lambda(mode='incremental')
                if not lambdas.empty:
                    results['latest_kj'] = np.round(lambdas.iloc[-1], 4)
                    results['pct_kj'] = np.round((lambdas <= results['latest_kj']).mean() * 100, 2)
                    results['sev_kj'] = get_severity_rating(results['pct_kj'])
                    print(f"  -> {market_name} KJ Lambda: {results['latest_kj']} ({results['pct_kj']}%)")
            except Exception as e:
                print(f"  -> {market_name} Failed KJ: {e}")

        if 'KL_MEES' in all_params.get(market, {}):
            try:
                mees_vals = bt.compute_daily_kl_mees(mode='incremental')
                if not mees_vals.empty:
                    results['latest_kl'] = np.round(mees_vals.iloc[-1], 4)
                    results['pct_kl'] = np.round((mees_vals <= results['latest_kl']).mean() * 100, 2)
                    results['sev_kl'] = get_severity_rating(results['pct_kl'])
                    print(f"  -> {market_name} KL MEES: {results['latest_kl']} ({results['pct_kl']}%)")
                    
                    # Process Factor Attribution (Top 5 Tickers)
                    if hasattr(bt, 'latest_kl_loadings') and bt.latest_kl_loadings:
                        last_eval_day = list(bt.latest_kl_loadings.keys())[-1]
                        loadings_vector = bt.latest_kl_loadings[last_eval_day]
                        
                        if len(loadings_vector) == len(bt.tickers):
                            abs_loadings = np.abs(loadings_vector)
                            top_5_indices = np.argsort(abs_loadings)[-5:][::-1]
                            
                            attribution_strs = []
                            for idx in top_5_indices:
                                attribution_strs.append(f"{bt.tickers[idx]} ({abs_loadings[idx]:.2f})")
                                
                            results['kl_attribution_html'] = f"<div style='font-size: 0.95em; color: #555; margin-top: 8px;'><strong>Top Risk Drivers:</strong> {', '.join(attribution_strs)}</div>"

            except Exception as e:
                print(f"  -> {market_name} Failed KL: {e}")
                
    except Exception as e:
        print(f"Critical error evaluating {market}: {e}")

    return results

def main():
    parser = argparse.ArgumentParser(description="Daily Tail Risk Monitor")
    parser.add_argument('--date', type=str, default=datetime.now().strftime('%Y-%m-%d'), help='Date to evaluate (YYYY-MM-DD)')
    parser.add_argument('--workers', type=int, default=None, help='Number of parallel workers')
    args = parser.parse_args()
    
    print(f"Running Daily Tail Risk Monitor for {args.date} (PARALLEL)...")
    
    if not os.path.exists(PARAM_FILE):
        print(f"Error: {PARAM_FILE} not found. Please run the optimizer first.")
        return
        
    with open(PARAM_FILE, 'r') as f:
        all_params = json.load(f)

    # We fetch ~3 years of data to establish a solid historical distribution
    # This ensures percentiles are robust.
    eval_date = datetime.strptime(args.date, '%Y-%m-%d')
    start_date = eval_date - timedelta(days=3 * 365)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = args.date

    markets = list(MARKET_UNIVERSES.keys())

    # Parallel Execution
    market_results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers if 'args' in locals() else None) as executor:
        futures = [executor.submit(evaluate_single_market, m, all_params, start_str, end_str) for m in markets]
        for future in concurrent.futures.as_completed(futures):
            market_results.append(future.result())

    # Build HTML Report
    html_lines = []
    html_lines.append("<html><head><title>Daily Global Tail Risk Summary</title>")
    html_lines.append("<style>")
    html_lines.append("body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }")
    html_lines.append(".header { text-align: center; margin-bottom: 40px; }")
    html_lines.append(".market-card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }")
    html_lines.append(".market-title { font-size: 1.5em; font-weight: bold; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }")
    html_lines.append(".metric-row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 1.1em; }")
    html_lines.append(".severity-badge { color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; min-width: 100px; text-align: center; }")
    html_lines.append("</style></head><body>")
    
    html_lines.append("<div class='header'>")
    html_lines.append("<h1>Daily Global Tail Risk Dashboard</h1>")
    html_lines.append(f"<p><strong>Date:</strong> {end_str}</p>")
    html_lines.append("<p>Tracking cross-sectional tail crash probability across major equity indices (Parallel Engine).</p>")
    html_lines.append("</div>")

    # Sort results to maintain a consistent order in the report
    market_results.sort(key=lambda x: markets.index(x['market']))

    for res in market_results:
        html_lines.append("<div class='market-card'>")
        html_lines.append(f"<div class='market-title'>{res['market_name']} ({res['market']})</div>")
        
        if res['latest_kj'] is not None:
            html_lines.append("<div class='metric-row'>")
            html_lines.append("<span><strong>KJ Lambda Risk Level:</strong></span>")
            html_lines.append(f"<span>Raw Metric: <strong>{res['latest_kj']}</strong> | Historical Percentile: <strong>{res['pct_kj']}%</strong></span>")
            html_lines.append(f"<span class='severity-badge' style='background-color: {res['sev_kj']['color']}'>{res['sev_kj']['level']}</span>")
            html_lines.append("</div>")
            
        if res['latest_kl'] is not None:
            html_lines.append("<div class='metric-row' style='margin-top: 15px;'>")
            html_lines.append("<span><strong>KL MEES Risk Level:</strong></span>")
            html_lines.append(f"<span>Raw Metric: <strong>{res['latest_kl']}</strong> | Historical Percentile: <strong>{res['pct_kl']}%</strong></span>")
            html_lines.append(f"<span class='severity-badge' style='background-color: {res['sev_kl']['color']}'>{res['sev_kl']['level']}</span>")
            html_lines.append("</div>")
            if res['kl_attribution_html']:
                html_lines.append(res['kl_attribution_html'])
            
        if res['latest_kj'] is None and res['latest_kl'] is None:
            html_lines.append("<p><em>Data unavailable for this market today.</em></p>")
            
        html_lines.append("</div>")

    html_lines.append("</body></html>")
    
    out_file = "daily_risk_summary.html"
    with open(out_file, 'w') as f:
        f.write("\n".join(html_lines))
        
    print(f"\n==============================================")
    print(f"Daily monitoring complete.")
    print(f"Dashboard exported to: {os.path.abspath(out_file)}")

if __name__ == "__main__":
    main()
