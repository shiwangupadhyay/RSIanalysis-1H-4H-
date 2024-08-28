import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
from ta.momentum import RSIIndicator

if not mt5.initialize():
    st.error("Failed to initialize MetaTrader 5")
    mt5.shutdown()

def get_rsi(symbol, timeframe, periods=14):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 500)
    
    df = pd.DataFrame(rates)
    
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], unit='s')
    
    rsi = RSIIndicator(df['close'], periods)
    df['rsi'] = rsi.rsi()
    return df

forex_pairs = [
    'EURUSD', 'USDJPY', 'GBPUSD', 'AUDUSD', 'USDCAD', 'USDCHF',
    'NZDUSD', 'EURJPY', 'GBPJPY', 'EURGBP', 'AUDJPY', 'EURAUD',
    'EURCHF', 'AUDNZD', 'NZDJPY', 'GBPAUD', 'GBPCAD', 'EURNZD',
    'AUDCAD', 'GBPCHF', 'AUDCHF', 'EURCAD', 'CADJPY', 'GBPNZD',
    'CADCHF', 'CHFJPY', 'NZDCAD', 'NZDCHF'
]

timeframe_1h = st.checkbox("1-Hour Timeframe")
timeframe_4h = st.checkbox("4-Hour Timeframe")

results_1h = []
results_4h = []

if timeframe_1h:
    for symbol in forex_pairs:
        try:
            df = get_rsi(symbol, mt5.TIMEFRAME_H1)
            if 'rsi' in df.columns:
                latest_rsi = df['rsi'].iloc[-1]
                if latest_rsi < 30 or latest_rsi > 70:
                    results_1h.append({'Symbol': symbol, 'RSI (1H)': latest_rsi})
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")

if timeframe_4h:
    for symbol in forex_pairs:
        try:
            df = get_rsi(symbol, mt5.TIMEFRAME_H4)
            if 'rsi' in df.columns:
                latest_rsi = df['rsi'].iloc[-1]
                if latest_rsi < 30 or latest_rsi > 70:
                    results_4h.append({'Symbol': symbol, 'RSI (4H)': latest_rsi})
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")

st.title("Forex Pairs with Extreme RSI")

if timeframe_1h and not timeframe_4h:
    if results_1h:
        st.table(pd.DataFrame(results_1h))
    else:
        st.write("No forex pairs found with RSI < 30 or RSI > 70 for 1-hour timeframe.")

elif timeframe_4h and not timeframe_1h:
    if results_4h:
        st.table(pd.DataFrame(results_4h))
    else:
        st.write("No forex pairs found with RSI < 30 or RSI > 70 for 4-hour timeframe.")


elif timeframe_1h and timeframe_4h:
    
    symbols_1h = set([result['Symbol'] for result in results_1h])
    symbols_4h = set([result['Symbol'] for result in results_4h])
    common_symbols = symbols_1h.intersection(symbols_4h)
    
    if common_symbols:
        common_results = []
        for symbol in common_symbols:
            rsi_1h = next((item['RSI (1H)'] for item in results_1h if item['Symbol'] == symbol), None)
            rsi_4h = next((item['RSI (4H)'] for item in results_4h if item['Symbol'] == symbol), None)
            if rsi_1h is not None and rsi_4h is not None:
                common_results.append({'Symbol': symbol, 'RSI (1H)': rsi_1h, 'RSI (4H)': rsi_4h})
        st.table(pd.DataFrame(common_results))
    else:
        st.write("No common forex pairs found with RSI < 30 or RSI > 70 for both timeframes.")