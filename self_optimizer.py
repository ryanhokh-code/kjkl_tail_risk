import numpy as np
import pandas as pd
import json
import os
import argparse
from datetime import datetime
from backtest_tail_risk_daily import TailRiskBacktester
import warnings

warnings.filterwarnings("ignore")

PARAM_FILE = 'optimized_params.json'

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

MARKET_UNIVERSES = {
    '^GSPC': {
        'name': 'US (S&P 500)',
        'tickers': [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
            'JPM', 'V', 'MA', 'BAC', 'GS', 'MS', 'WFC', 'C',
            'LLY', 'JNJ', 'PFE', 'ABBV', 'MRK', 'TMO', 'UNH',
            'WMT', 'PG', 'KO', 'PEP', 'COST', 'T', 'VZ',
            'DIS', 'NFLX', 'XOM', 'CVX', 'AVGO', 'AMD', 'ORCL', 'CRM',
            'INTC', 'HD', 'BA', 'MCD', 'NKE', 'CSCO', 'IBM'
        ]
    },
    '000300.SS': {
        'name': 'China (CSI 300)',
        'tickers': [
            '600519.SS', '601398.SS', '601288.SS', '601939.SS', '601857.SS', 
            '600036.SS', '601088.SS', '601166.SS', '600900.SS', '601328.SS',
            '601628.SS', '601018.SS', '601318.SS', '600028.SS', '603288.SS',
            '600016.SS', '601818.SS', '601169.SS', '600030.SS', '600000.SS',
            '601688.SS', '601211.SS', '601888.SS', '600104.SS', '600999.SS',
            '601601.SS', '601009.SS', '601988.SS', '601336.SS', '600048.SS',
            '601186.SS', '600050.SS', '600887.SS', '600276.SS', '601998.SS',
            '601800.SS', '601390.SS', '600019.SS', '600585.SS', '601668.SS'
        ]
    },
    '^HSI': {
        'name': 'Hong Kong (Hang Seng)',
        'tickers': [
            '0700.HK', '9988.HK', '3690.HK', '1299.HK', '0939.HK', 
            '0005.HK', '0941.HK', '0883.HK', '1398.HK', '3988.HK',
            '0001.HK', '0011.HK', '0388.HK', '0002.HK', '0016.HK',
            '0027.HK', '0386.HK', '0857.HK', '0003.HK', '0066.HK',
            '0823.HK', '0006.HK', '0101.HK', '0012.HK', '0017.HK',
            '0267.HK', '2382.HK', '0004.HK', '1093.HK', '2318.HK',
            '1044.HK', '2020.HK', '0968.HK', '1928.HK', '1109.HK',
            '1810.HK', '0175.HK', '0288.HK', '0688.HK', '0836.HK'
        ]
    },
    '^TWII': {
        'name': 'Taiwan (TAIEX)',
        'tickers': [
            '2330.TW', '2454.TW', '2317.TW', '2382.TW', '2412.TW', 
            '2881.TW', '2882.TW', '1301.TW', '1303.TW', '2886.TW',
            '2891.TW', '2002.TW', '1216.TW', '2884.TW', '2892.TW',
            '2308.TW', '3231.TW', '2303.TW', '2885.TW', '2379.TW',
            '2883.TW', '2357.TW', '3711.TW', '2324.TW', '1326.TW',
            '2408.TW', '3045.TW', '2353.TW', '2603.TW', '1101.TW',
            '2912.TW', '2890.TW', '2880.TW', '2014.TW', '1402.TW',
            '5871.TW', '5880.TW', '2887.TW', '2207.TW', '6505.TW'
        ]
    },
    '^N225': {
        'name': 'Japan (Nikkei 225)',
        'tickers': [
            '7203.T', '6758.T', '8306.T', '6861.T', '9432.T', 
            '9984.T', '8035.T', '4063.T', '6098.T', '4568.T',
            '8316.T', '8001.T', '8031.T', '7974.T', '6501.T',
            '6954.T', '6857.T', '6902.T', '6702.T', '4502.T',
            '8411.T', '4661.T', '8766.T', '9022.T', '3382.T',
            '8053.T', '7267.T', '8002.T', '6594.T', '4519.T',
            '2914.T', '9433.T', '4452.T', '1925.T', '4901.T',
            '4503.T', '7751.T', '6273.T', '6301.T', '6146.T'
        ]
    },
    '^KS11': {
        'name': 'Korea (KOSPI)',
        'tickers': [
            '005930.KS', '000660.KS', '373220.KS', '207940.KS', '005380.KS', 
            '000270.KS', '068270.KS', '051910.KS', '005490.KS', '105560.KS',
            '035420.KS', '028260.KS', '012330.KS', '066570.KS', '035720.KS',
            '006400.KS', '096770.KS', '005935.KS', '032830.KS', '323410.KS',
            '034730.KS', '015760.KS', '055550.KS', '011200.KS', '033920.KS',
            '316140.KS', '051900.KS', '017670.KS', '090430.KS', '086280.KS',
            '018260.KS', '259960.KS', '034020.KS', '042660.KS', '010950.KS',
            '010140.KS', '034220.KS', '004020.KS', '352820.KS', '011170.KS'
        ]
    },
    '^STOXX50E': {
        'name': 'Europe (Euro Stoxx 50)',
        'tickers': [
            'ASML.AS', 'MC.PA', 'SAP.DE', 'TTE.PA', 'OR.PA', 
            'SAN.PA', 'SIE.DE', 'ALV.DE', 'AIR.PA', 'IBE.MC',
            'SU.PA', 'BNP.PA', 'CS.PA', 'MUV2.DE', 'DTE.DE',
            'ITX.MC', 'ENEL.MI', 'AI.PA', 'ABI.BR', 'INGA.AS',
            'ISP.MI', 'SAF.PA', 'DPW.DE', 'MBG.DE', 'RMS.PA',
            'VOW3.DE', 'BAS.DE', 'BN.PA', 'EL.PA', 'ENI.MI',
            'BBVA.MC', 'MCD.PA', 'BMW.DE', 'KER.PA', 'PRG.AS',
            'FLTR.I', 'AD.AS', 'IFX.DE', 'CRG.I', 'DG.PA'
        ]
    }
}

def generate_default_market_tickers(market_ticker):
    if market_ticker in MARKET_UNIVERSES:
        return MARKET_UNIVERSES[market_ticker]['tickers']
    elif market_ticker == '^NDX' or market_ticker == '^IXIC':
        return ['AMZN', 'AAPL', 'MSFT', 'META', 'GOOGL', 'NVDA', 'TSLA', 'AVGO', 'COST', 'PEP', 
                'CSCO', 'TMUS', 'NFLX', 'AMD', 'INTC', 'CMCSA', 'QCOM', 'TXN', 'HON', 'AMGN']
    else:
        # Default fallback SPX top approx 40
        return MARKET_UNIVERSES['^GSPC']['tickers']

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
