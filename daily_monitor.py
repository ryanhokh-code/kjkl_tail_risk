import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import yfinance as yf
from self_optimizer import MARKET_UNIVERSES, generate_default_market_tickers
from backtest_tail_risk_daily import TailRiskBacktester
import warnings
warnings.filterwarnings("ignore")

PARAM_FILE = 'optimized_params.json'

def get_severity_rating(percentile):
    if percentile > 99:
        return {'level': 'Extreme', 'color': '#d32f2f'} # Red
    elif percentile > 95:
        return {'level': 'High', 'color': '#f57c00'} # Orange
    elif percentile > 90:
        return {'level': 'Elevated', 'color': '#fbc02d'} # Yellow
    else:
        return {'level': 'Normal', 'color': '#388e3c'} # Green

def main():
    print(f"Running Daily Tail Risk Monitor for {datetime.now().strftime('%Y-%m-%d')}...")
    
    if not os.path.exists(PARAM_FILE):
        print(f"Error: {PARAM_FILE} not found. Please run the optimizer first.")
        return
        
    with open(PARAM_FILE, 'r') as f:
        all_params = json.load(f)

    # We fetch ~3 years of data to establish a solid historical distribution
    # This ensures percentiles are robust.
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3 * 365)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    html_lines = []
    html_lines.append("<html><head><title>Daily Global Tail Risk Summary</title>")
    html_lines.append("<style>")
    html_lines.append("body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }")
    html_lines.append(".header { text-align: center; margin-bottom: 40px; }")
    html_lines.append(".market-card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }")
    html_lines.append(".market-title { font-size: 1.5em; font-weight: bold; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }")
    html_lines.append(".metric-row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 1.1em; }")
    html_lines.append(".severity-badge { color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; }")
    html_lines.append("</style></head><body>")
    
    html_lines.append("<div class='header'>")
    html_lines.append("<h1>Daily Global Tail Risk Dashboard</h1>")
    html_lines.append(f"<p><strong>Date:</strong> {end_str}</p>")
    html_lines.append("<p>Tracking cross-sectional tail crash probability across major equity indices.</p>")
    html_lines.append("</div>")

    markets = list(MARKET_UNIVERSES.keys())

    for market in markets:
        market_name = MARKET_UNIVERSES[market]['name']
        print(f"\nEvaluating: {market_name}")
        
        if market not in all_params:
            print(f"  -> No optimized parameters found for {market}. Skipping.")
            continue
            
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
        
        latest_kj = None
        pct_kj = None
        sev_kj = None
        latest_kl = None
        pct_kl = None
        sev_kl = None
        kl_attribution_html = ""
        
        if 'KJ_Lambda' in all_params[market]:
            try:
                lambdas = bt.compute_daily_kj_lambda()
                if not lambdas.empty:
                    latest_kj = np.round(lambdas.iloc[-1], 4)
                    # Compute historical percentile (0 to 100)
                    pct_kj = np.round((lambdas <= latest_kj).mean() * 100, 2)
                    sev_kj = get_severity_rating(pct_kj)
                    print(f"  -> KJ Lambda: {latest_kj} (Percentile: {pct_kj}%) - {sev_kj['level']}")
            except Exception as e:
                print(f"  -> Failed to compute KJ: {e}")

        if 'KL_MEES' in all_params[market]:
            try:
                mees_vals = bt.compute_daily_kl_mees()
                if not mees_vals.empty:
                    latest_kl = np.round(mees_vals.iloc[-1], 4)
                    pct_kl = np.round((mees_vals <= latest_kl).mean() * 100, 2)
                    sev_kl = get_severity_rating(pct_kl)
                    print(f"  -> KL MEES: {latest_kl} (Percentile: {pct_kl}%) - {sev_kl['level']}")
                    
                    # Process Factor Attribution (Top 5 Tickers)
                    if hasattr(bt, 'latest_kl_loadings') and bt.latest_kl_loadings is not None:
                        # Ensure we get loadings from the most recent day processed
                        last_eval_day = list(bt.latest_kl_loadings.keys())[-1]
                        loadings_vector = bt.latest_kl_loadings[last_eval_day]
                        
                        if len(loadings_vector) == len(bt.tickers):
                            abs_loadings = np.abs(loadings_vector)
                            top_5_indices = np.argsort(abs_loadings)[-5:][::-1]
                            
                            attribution_strs = []
                            for idx in top_5_indices:
                                attribution_strs.append(f"{bt.tickers[idx]} ({abs_loadings[idx]:.2f})")
                                
                            kl_attribution_html = f"<div style='font-size: 0.95em; color: #555; margin-top: 8px;'><strong>Top Risk Drivers:</strong> {', '.join(attribution_strs)}</div>"

            except Exception as e:
                print(f"  -> Failed to compute KL: {e}")

        html_lines.append("<div class='market-card'>")
        html_lines.append(f"<div class='market-title'>{market_name} ({market})</div>")
        
        if latest_kj is not None:
            html_lines.append("<div class='metric-row'>")
            html_lines.append("<span><strong>KJ Lambda Risk Level:</strong></span>")
            html_lines.append(f"<span>Raw Metric: <strong>{latest_kj}</strong> | Historical Percentile: <strong>{pct_kj}%</strong></span>")
            html_lines.append(f"<span class='severity-badge' style='background-color: {sev_kj['color']}'>{sev_kj['level']}</span>")
            html_lines.append("</div>")
            
        if latest_kl is not None:
            html_lines.append("<div class='metric-row' style='margin-top: 15px;'>")
            html_lines.append("<span><strong>KL MEES Risk Level:</strong></span>")
            html_lines.append(f"<span>Raw Metric: <strong>{latest_kl}</strong> | Historical Percentile: <strong>{pct_kl}%</strong></span>")
            html_lines.append(f"<span class='severity-badge' style='background-color: {sev_kl['color']}'>{sev_kl['level']}</span>")
            html_lines.append("</div>")
            if kl_attribution_html:
                html_lines.append(kl_attribution_html)
            
        if latest_kj is None and latest_kl is None:
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
