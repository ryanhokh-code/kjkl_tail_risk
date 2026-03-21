import os
import argparse
import pandas as pd
from datetime import datetime
from config import MARKET_UNIVERSES, generate_default_market_tickers
from backtest_tail_risk_daily import TailRiskBacktester
import warnings
warnings.filterwarnings("ignore")

def main():
    parser = argparse.ArgumentParser(description="Multi-Market Tail Risk Analytics and Reporting")
    parser.add_argument('--start', type=str, default='2018-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2026-03-21', help='End date (YYYY-MM-DD)')
    parser.add_argument('--skip-kl', action='store_true', help='Skip KL evaluation')
    args = parser.parse_args()

    report_lines = []
    report_lines.append("# Global Tail Risk Measures Report")
    report_lines.append(f"Generated on {datetime.now().strftime('%Y-%m-%d')}\n")
    report_lines.append(f"Period: {args.start} to {args.end}\n")

    html_lines = []
    html_lines.append("<html><head><title>Global Tail Risk Report</title>")
    html_lines.append("<style>")
    html_lines.append("body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 20px; color: #333; }")
    html_lines.append("h1, h2, h3 { color: #2c3e50; }")
    html_lines.append("table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }")
    html_lines.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }")
    html_lines.append("th { background-color: #f2f2f2; font-weight: bold; }")
    html_lines.append(".interpretation { background-color: #e8f4f8; padding: 15px; border-left: 5px solid #2980b9; margin-bottom: 20px; }")
    html_lines.append(".warning { background-color: #ffcccb; padding: 10px; border-left: 5px solid #d32f2f; margin-bottom: 20px; font-weight: bold; }")
    html_lines.append(".tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; border-radius: 5px 5px 0 0; display: flex; flex-wrap: wrap; }")
    html_lines.append(".tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; font-size: 15px; font-weight: bold; }")
    html_lines.append(".tab button:hover { background-color: #ddd; }")
    html_lines.append(".tab button.active { background-color: #3498db; color: white; }")
    html_lines.append(".tabcontent { display: none; padding: 20px; border: 1px solid #ccc; border-top: none; border-radius: 0 0 5px 5px; animation: fadeEffect 0.5s; }")
    html_lines.append("@keyframes fadeEffect { from {opacity: 0;} to {opacity: 1;} }")
    html_lines.append("details { margin-bottom: 15px; background: #f9f9f9; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }")
    html_lines.append("summary { font-size: 1.1em; font-weight: bold; cursor: pointer; color: #2980b9; }")
    html_lines.append("</style></head><body>")
    
    html_lines.append("<h1>Global Tail Risk Measures Report</h1>")
    html_lines.append(f"<p><strong>Generated on:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>")
    html_lines.append(f"<p><strong>Period:</strong> {args.start} to {args.end}</p>")
    html_lines.append("<p><em>This report evaluates the predictive power of cross-sectional tail risk measures across global markets based on pre-computed cached signals.</em></p>")

    markets = list(MARKET_UNIVERSES.keys())

    # Build Tab Bar
    html_lines.append("<div class='tab'>")
    for i, market in enumerate(markets):
        m_name = MARKET_UNIVERSES[market]['name']
        safe_id = market.replace('^', '').replace('.', '')
        active_cls = " active" if i == 0 else ""
        html_lines.append(f"<button class='tablinks{active_cls}' onclick=\"openMarket(event, '{safe_id}')\" id='btn_{safe_id}'>{m_name}</button>")
    html_lines.append("</div>")

    print("Generating Analytics Report from Cached Signals...\n")

    for market in markets:
        market_name = MARKET_UNIVERSES[market]['name']
        print(f"Processing Analytics for Market: {market_name} ({market})")
        
        tickers = generate_default_market_tickers(market)
        
        bt_eval = TailRiskBacktester(
            tickers=tickers,
            market_ticker=market,
            start_date=args.start,
            end_date=args.end,
            horizons=[1, 5, 10, 21],
            load_optimized_params=True
        )
        
        # Load signals instantly via incremental mode
        bt_eval.fetch_data()
        bt_eval.generate_signals(mode='incremental')
        
        kj_ret, kj_vol, kj_dd = bt_eval.run_regressions('KJ_Lambda')
        kj_hit = bt_eval.compute_hit_rates('KJ_Lambda')
        kj_dist_stats = bt_eval.compute_alert_distribution_stats('KJ_Lambda')
        kj_dist_plot = bt_eval.generate_alert_distribution_plots('KJ_Lambda')
        
        kl_ret_str, kl_vol_str, kl_dd_str, kl_hit_str = "Skipped", "Skipped", "Skipped", "Skipped"
        kl_dist_stats, kl_dist_plot = {}, None
        kl_ret = pd.DataFrame()
        kl_vol = pd.DataFrame()
        kl_dd = pd.DataFrame()
        kl_hit = pd.DataFrame()

        if not args.skip_kl:
            kl_ret, kl_vol, kl_dd = bt_eval.run_regressions('KL_MEES')
            kl_hit = bt_eval.compute_hit_rates('KL_MEES')
            kl_dist_stats = bt_eval.compute_alert_distribution_stats('KL_MEES')
            kl_dist_plot = bt_eval.generate_alert_distribution_plots('KL_MEES')
            kl_ret_str = kl_ret.to_markdown() if not kl_ret.empty else "N/A"
            kl_vol_str = kl_vol.to_markdown() if not kl_vol.empty else "N/A"
            kl_dd_str = kl_dd.to_markdown() if not kl_dd.empty else "N/A"
            kl_hit_str = kl_hit.to_markdown() if not kl_hit.empty else "N/A"
        
        # Save time-series signal visualisation
        plot_path = f"export_img/daily_tail_risk_{market.replace('^', '')}.png"
        bt_eval.visualize_signals(save_path=plot_path)

        # Generate scatter plots
        kj_scatter_path = bt_eval.generate_scatter_plots(
            measure_col='KJ_Lambda',
            save_path=f"export_img/scatter_KJ_{market.replace('^', '')}.png"
        )
        kl_scatter_path = bt_eval.generate_scatter_plots(
            measure_col='KL_MEES',
            save_path=f"export_img/scatter_KL_{market.replace('^', '')}.png"
        )

        # ---------------- Markdown Output ----------------
        report_lines.append(f"## {market_name} ({market})")
        
        # We need to print parameters used, fetch from bt_eval
        opt_params = getattr(bt_eval, 'optimized_params', {})
        kj_params = opt_params.get("KJ_Lambda", {})
        kl_params = opt_params.get("KL_MEES", {})

        report_lines.append(f"**Optimal Parameters Loaded From Cache:**")
        if kj_params:
            report_lines.append(f"- KJ Measure: window={kj_params.get('window', 'N/A')}, quantile={kj_params.get('quantile', 'N/A')}")
        if not args.skip_kl and kl_params:
            report_lines.append(f"- KL Measure: window={kl_params.get('window', 'N/A')}, n_pca={kl_params.get('n_pca', 'N/A')}, alpha={kl_params.get('alpha', 'N/A')}")
            
        report_lines.append(f"\n### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)")
        report_lines.append("**Predicting Future Market Returns:**")
        report_lines.append(kj_ret.to_markdown() if not kj_ret.empty else "N/A")
        report_lines.append("\n**Predicting Future Market Volatility Ratio:**")
        report_lines.append(kj_vol.to_markdown() if not kj_vol.empty else "N/A")
        report_lines.append("\n**Predicting Future Max Drawdown:**")
        report_lines.append(kj_dd.to_markdown() if not kj_dd.empty else "N/A")
        report_lines.append("\n**Hit Rate Analysis (KJ Lambda > 90th Pct):**")
        report_lines.append(kj_hit.to_markdown() if not kj_hit.empty else "N/A")
        
        report_lines.append("\n**Alert Level Distribution Analysis:**")
        if kj_dist_stats:
            for h in kj_dist_stats:
                report_lines.append(f"\n*Horizon: {h} Days*")
                for target, df in kj_dist_stats[h].items():
                    report_lines.append(f"*{target}*")
                    report_lines.append(df.to_markdown())
        else:
            report_lines.append("N/A")
        
        if not args.skip_kl:
            report_lines.append(f"\n### KL MEES Predictive Significance (Level + Velocity Multivariate Model)")
            report_lines.append("**Predicting Future Market Returns:**")
            report_lines.append(kl_ret_str)
            report_lines.append("\n**Predicting Future Market Volatility Ratio:**")
            report_lines.append(kl_vol_str)
            report_lines.append("\n**Predicting Future Max Drawdown:**")
            report_lines.append(kl_dd_str)
            report_lines.append("\n**Hit Rate Analysis (KL MEES > 90th Pct):**")
            report_lines.append(kl_hit_str)

            report_lines.append("\n**Alert Level Distribution Analysis:**")
            if kl_dist_stats:
                for h in kl_dist_stats:
                    report_lines.append(f"\n*Horizon: {h} Days*")
                    for target, df in kl_dist_stats[h].items():
                        report_lines.append(f"*{target}*")
                        report_lines.append(df.to_markdown())
            else:
                report_lines.append("N/A")

        report_lines.append(f"\n![{market_name} Tail Risk Prediction Plot]({os.path.abspath(plot_path)})\n")
        if kj_scatter_path:
            report_lines.append(f"\n**KJ Lambda — Scatter: Risk Measure vs Forward Outcomes**")
            report_lines.append(f"![KJ Scatter {market_name}]({os.path.abspath(kj_scatter_path)})\n")
        if kl_scatter_path:
            report_lines.append(f"\n**KL MEES — Scatter: Risk Measure vs Forward Outcomes**")
            report_lines.append(f"![KL Scatter {market_name}]({os.path.abspath(kl_scatter_path)})\n")
            
        if kj_dist_plot:
            report_lines.append(f"\n**KJ Lambda — Alert Level Distributions**")
            report_lines.append(f"![KJ Alert Dist {market_name}]({os.path.abspath(kj_dist_plot)})\n")
        if kl_dist_plot:
            report_lines.append(f"\n**KL MEES — Alert Level Distributions**")
            report_lines.append(f"![KL Alert Dist {market_name}]({os.path.abspath(kl_dist_plot)})\n")
            
        report_lines.append("---\n")
        
        # ---------------- HTML Output ----------------
        safe_id = market.replace('^', '').replace('.', '')
        display_style = "block" if market == markets[0] else "none"
        html_lines.append(f"<div id='{safe_id}' class='tabcontent' style='display: {display_style};'>")
        html_lines.append(f"<h2>{market_name} ({market})</h2>")
        
        # Analyze Significance for Interpretation
        vol_sig = False
        ret_sig = False
        
        if not kj_vol.empty and kj_vol['KJ_Lambda t-stat'].max() > 1.96:
            vol_sig = True
        if not args.skip_kl and not kl_vol.empty and kl_vol['KL_MEES t-stat'].max() > 1.96:
            vol_sig = True
            
        if not kj_ret.empty and kj_ret['KJ_Lambda t-stat'].abs().max() > 1.96:
            ret_sig = True
        if not args.skip_kl and not kl_ret.empty and kl_ret['KL_MEES t-stat'].abs().max() > 1.96:
            ret_sig = True

        html_lines.append("<div class='interpretation'>")
        html_lines.append("<strong>Economic Interpretation:</strong><br>")
        html_lines.append("The <em>KJ Lambda</em> measure captures the power-law exponent of the cross-sectional left tail. Higher values imply a fatter left tail (i.e. more extreme firm-specific crashes happening simultaneously).<br>")
        if not args.skip_kl:
            html_lines.append("The <em>KL MEES</em> measure tracks the systematic expected shortfall beyond a 10% VaR threshold. Elevated levels signify concentrated systemic risk exposure.<br>")
        html_lines.append("</div>")

        if vol_sig:
            html_lines.append("<div class='warning'>")
            html_lines.append(f"⚠️ <strong>Downside Implication for {market_name}:</strong> The backtest shows highly significant predictive power for future <em>volatility</em>. When the risk measure enters High/Extreme levels in this market, expect severe turbulence and amplified price swings over the next 5 to 21 days.")
            html_lines.append("</div>")
            
        if ret_sig:
            html_lines.append("<div class='warning'>")
            html_lines.append(f"⚠️ <strong>Downside Implication for {market_name}:</strong> The backtest shows significant predictive power for future <em>returns</em>. Elevated tail risk signals in this region are strongly correlated with sharp directional market corrections.")
            html_lines.append("</div>")

        html_lines.append("<h3>KJ Lambda Predictive Significance</h3>")
        html_lines.append("<details><summary>Predicting Future Market Returns (Joint Level + Momentum Model)</summary>")
        html_lines.append(kj_ret.to_html(classes='dataframe', float_format=lambda x: f"{x:.4f}") if not kj_ret.empty else "<p>N/A</p>")
        html_lines.append("</details>")
        html_lines.append("<details><summary>Predicting Future Market Volatility Ratio (Joint Level + Momentum Model)</summary>")
        html_lines.append(kj_vol.to_html(classes='dataframe', float_format=lambda x: f"{x:.4f}") if not kj_vol.empty else "<p>N/A</p>")
        html_lines.append("</details>")
        html_lines.append("<details><summary>Predicting Future Max Drawdown (Joint Level + Momentum Model)</summary>")
        html_lines.append("<p><em>A negative Beta and significant t-stat indicates that when the KJ signal is high, the subsequent intra-period trough is materially deeper.</em></p>")
        html_lines.append(kj_dd.to_html(classes='dataframe', float_format=lambda x: f"{x:.4f}") if not kj_dd.empty else "<p>N/A</p>")
        html_lines.append("</details>")
        html_lines.append("<details><summary>Hit Rate Analysis: KJ Lambda > 90th Percentile</summary>")
        html_lines.append("<p><em>% of high-signal days where future returns were negative, and where max drawdown exceeded -1%/-2%/-3% thresholds. Compares mean returns between high vs. normal signal regimes.</em></p>")
        html_lines.append(kj_hit.to_html(classes='dataframe', float_format=lambda x: f"{x:.1f}") if not kj_hit.empty else "<p>N/A</p>")
        html_lines.append("</details>")

        html_lines.append("<details open><summary>Alert Level Distribution Analysis (Target distributions per risk regime)</summary>")
        if kj_dist_stats:
            for h in kj_dist_stats:
                html_lines.append(f"<h5>Horizon: {h} Days</h5>")
                for target, df in kj_dist_stats[h].items():
                    html_lines.append(f"<p><strong>{target}</strong></p>")
                    html_lines.append(df.to_html(classes='dataframe'))
        else:
            html_lines.append("<p>N/A</p>")
        html_lines.append("</details>")

        if not args.skip_kl:
            html_lines.append("<h3>KL MEES Predictive Significance</h3>")
            html_lines.append("<details><summary>Predicting Future Market Returns (Joint Level + Momentum Model)</summary>")
            html_lines.append(kl_ret.to_html(classes='dataframe', float_format=lambda x: f"{x:.4f}") if not kl_ret.empty else "<p>N/A</p>")
            html_lines.append("</details>")
            html_lines.append("<details><summary>Predicting Future Market Volatility Ratio (Joint Level + Momentum Model)</summary>")
            html_lines.append(kl_vol.to_html(classes='dataframe', float_format=lambda x: f"{x:.4f}") if not kl_vol.empty else "<p>N/A</p>")
            html_lines.append("</details>")
            html_lines.append("<details><summary>Predicting Future Max Drawdown (Joint Level + Momentum Model)</summary>")
            html_lines.append("<p><em>A negative Beta and significant t-stat indicates that when the KL signal is high, the subsequent intra-period trough is materially deeper.</em></p>")
            html_lines.append(kl_dd.to_html(classes='dataframe', float_format=lambda x: f"{x:.4f}") if not kl_dd.empty else "<p>N/A</p>")
            html_lines.append("</details>")
            html_lines.append("<details><summary>Hit Rate Analysis: KL MEES > 90th Percentile</summary>")
            html_lines.append("<p><em>% of high-signal days where future returns were negative, and where max drawdown exceeded -1%/-2%/-3% thresholds.</em></p>")
            html_lines.append(kl_hit.to_html(classes='dataframe', float_format=lambda x: f"{x:.1f}") if not kl_hit.empty else "<p>N/A</p>")
            html_lines.append("</details>")

            html_lines.append("<details open><summary>Alert Level Distribution Analysis (Target distributions per risk regime)</summary>")
            if kl_dist_stats:
                for h in kl_dist_stats:
                    html_lines.append(f"<h5>Horizon: {h} Days</h5>")
                    for target, df in kl_dist_stats[h].items():
                        html_lines.append(f"<p><strong>{target}</strong></p>")
                        html_lines.append(df.to_html(classes='dataframe'))
            else:
                html_lines.append("<p>N/A</p>")
            html_lines.append("</details>")

        html_lines.append(f"<img src='{os.path.abspath(plot_path)}' alt='{market_name} Plot' style='max-width:100%; height:auto; margin-top:20px;'/>")

        if kj_scatter_path:
            html_lines.append("<h4>KJ Lambda — Scatter: Risk Measure vs Forward Outcomes</h4>")
            html_lines.append("<p><em>Each point is one trading day. <span style='color:#d62728;font-weight:bold;'>Red dots</span> are days where the signal exceeded its 90th percentile. The dashed line is the OLS best fit.</em></p>")
            html_lines.append(f"<img src='{os.path.abspath(kj_scatter_path)}' alt='KJ Scatter {market_name}' style='max-width:100%; height:auto; margin-top:10px;'/>")

        if kl_scatter_path:
            html_lines.append("<h4>KL MEES — Scatter: Risk Measure vs Forward Outcomes</h4>")
            html_lines.append("<p><em>Each point is one trading day. <span style='color:#d62728;font-weight:bold;'>Red dots</span> are days where the signal exceeded its 90th percentile. The dashed line is the OLS best fit.</em></p>")
            html_lines.append(f"<img src='{os.path.abspath(kl_scatter_path)}' alt='KL Scatter {market_name}' style='max-width:100%; height:auto; margin-top:10px;'/>")

        if kj_dist_plot:
            html_lines.append("<h4>KJ Lambda — Alert Level Distributions</h4>")
            html_lines.append("<p><em>Boxplots of target variables categorized by risk regime.</em></p>")
            html_lines.append(f"<img src='{os.path.abspath(kj_dist_plot)}' alt='KJ Alert Dist {market_name}' style='max-width:100%; height:auto; margin-top:10px;'/>")
            
        if kl_dist_plot:
            html_lines.append("<h4>KL MEES — Alert Level Distributions</h4>")
            html_lines.append("<p><em>Boxplots of target variables categorized by risk regime.</em></p>")
            html_lines.append(f"<img src='{os.path.abspath(kl_dist_plot)}' alt='KL Alert Dist {market_name}' style='max-width:100%; height:auto; margin-top:10px;'/>")

        html_lines.append("</div>")

    html_lines.append("<script>")
    html_lines.append("function openMarket(evt, marketName) {")
    html_lines.append("  var i, tabcontent, tablinks;")
    html_lines.append("  tabcontent = document.getElementsByClassName('tabcontent');")
    html_lines.append("  for (i = 0; i < tabcontent.length; i++) { tabcontent[i].style.display = 'none'; }")
    html_lines.append("  tablinks = document.getElementsByClassName('tablinks');")
    html_lines.append("  for (i = 0; i < tablinks.length; i++) { tablinks[i].className = tablinks[i].className.replace(' active', ''); }")
    html_lines.append("  document.getElementById(marketName).style.display = 'block';")
    html_lines.append("  evt.currentTarget.className += ' active';")
    html_lines.append("}")
    html_lines.append("</script>")

    # Write Final Markdown Report
    report_file = "multi_market_report.md"
    with open(report_file, 'w') as f:
        f.write("\n".join(report_lines))
        
    # Write Final HTML Report
    html_lines.append("</body></html>")
    html_file = "multi_market_report.html"
    with open(html_file, 'w') as f:
        f.write("\n".join(html_lines))
        
    print(f"\nSuccessfully generated markdown report: {os.path.abspath(report_file)}")
    print(f"Successfully generated HTML report: {os.path.abspath(html_file)}")

if __name__ == "__main__":
    main()
