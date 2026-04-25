import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="My Stock Tracker", layout="wide")

st.title("📈 :rainbow[Pro Stock Dashboard]")
st.write("Interactive Candlesticks, Moving Averages, and RSI Indicators.")

# Your complete stock dictionary
stocks = {
    # Original
    "Paras Defence & Space Tech": "PARAS.NS", "Data Patterns India": "DATAPATTNS.NS", "PTC Industries": "PTCIL.NS",
    "Servotech Power Systems": "SERVOTECH.NS", "Vedanta Ltd": "VEDL.NS", "Multi Commodity Exchange": "MCX.NS",
    "NMDC Ltd": "NMDC.NS", "IFCI Ltd": "IFCI.NS", "Pro Fin Capital": "511557.BO", "Bartronics India Ltd": "ASMS.NS",
    "Goldstar Power": "GOLDSTAR.NS", "Zee Media": "ZEEMEDIA.NS", "Cella Space Limited": "532701.BO",
    "KPIT Technologies": "KPITTECH.NS", "JBM Auto Ltd": "JBMA.NS", "SPML Infra Ltd": "SPMLINFRA.NS", "KNR Constructions": "KNRCON.NS",
    # Defense & Aviation
    "Hindustan Aeronautics (HAL)": "HAL.NS", "Bharat Electronics (BEL)": "BEL.NS", "Bharat Dynamics (BDL)": "BDL.NS",
    "Mazagon Dock Shipbuilders": "MAZDOCK.NS", "Cochin Shipyard (CSL)": "COCHINSHIP.NS", "Zen Technologies": "ZENTEC.NS",
    "Astra Microwave": "ASTRAMICRO.NS", "MTAR Technologies": "MTARTECH.NS", "Garden Reach Shipbuilders": "GRSE.NS",
    "Mishra Dhatu Nigam": "MIDHANI.NS", "Knowledge Marine & Eng": "KMEW.BO",
    # Banking
    "State Bank of India (SBI)": "SBIN.NS", "Bank of Baroda": "BANKBARODA.NS", "Canara Bank": "CANBK.NS",
    "UCO Bank": "UCOBANK.NS", "Union Bank of India": "UNIONBANK.NS", "Central Bank of India": "CENTRALBK.NS",
    "Bank of Maharashtra": "MAHABANK.NS", "Bank of India": "BANKINDIA.NS", "Punjab & Sind Bank": "PSB.NS",
    "Indian Overseas Bank": "IOB.NS", "Indian Bank": "INDIANB.NS", "Punjab National Bank": "PNB.NS",
    "General Insurance Corp": "GICRE.NS", "Life Insurance Corp (LIC)": "LICI.NS", "The New India Assurance": "NIACL.NS",
    "Power Finance Corp (PFC)": "PFC.NS", "REC Ltd": "RECLTD.NS", "Indian Railway Finance Corp": "IRFC.NS",
    "Housing & Urban Dev (HUDCO)": "HUDCO.NS",
    # Energy
    "Bharat Petroleum (BPCL)": "BPCL.NS", "Hindustan Petroleum (HPCL)": "HINDPETRO.NS", "Indian Oil Corp (IOC)": "IOC.NS",
    "Oil India Ltd": "OIL.NS", "ONGC": "ONGC.NS", "Mangalore Refinery (MRPL)": "MRPL.NS", "NTPC Ltd": "NTPC.NS",
    "Coal India Ltd": "COALINDIA.NS", "SJVN Ltd": "SJVN.NS", "NHPC Ltd": "NHPC.NS", "GAIL (India) Ltd": "GAIL.NS",
    "Gujarat Gas Ltd": "GUJGASLTD.NS", "Power Grid Corp": "POWERGRID.NS",
    # Metals & Heavy Eng
    "MMTC Ltd": "MMTC.NS", "Steel Authority of India (SAIL)": "SAIL.NS", "National Aluminium (NALCO)": "NATIONALUM.NS",
    "Hindustan Copper Ltd": "HINDCOPPER.NS", "NLC India Ltd": "NLCINDIA.NS", "KIOCL Ltd": "KIOCL.NS",
    "Bharat Heavy Electricals (BHEL)": "BHEL.NS", "Engineers India Ltd": "ENGINERSIN.NS", "Larsen & Toubro (L&T)": "LT.NS",
    # Railways & Infra
    "Ircon International Ltd": "IRCON.NS", "Container Corp of India": "CONCOR.NS", "NBCC (India) Ltd": "NBCC.NS",
    "IRCTC": "IRCTC.NS", "Rites Ltd": "RITES.NS", "Rail Vikas Nigam (RVNL)": "RVNL.NS",
    # Others
    "Rashtriya Chemicals & Fertilizers": "RCF.NS", "ITI Ltd": "ITI.NS"
}

# Sidebar Index
st.sidebar.header("🔍 Stock Index")
options = ["Overview (All Stocks)"] + sorted(list(stocks.keys()))
selected_option = st.sidebar.selectbox("Choose a view:", options)

if selected_option == "Overview (All Stocks)":
    stocks_to_display = stocks
    st.info("Loading overview of all stocks. This may take a minute.")
else:
    stocks_to_display = {selected_option: stocks[selected_option]}

# Function to fetch data and calculate indicators
@st.cache_data(ttl=3600) 
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    # Fetch 3 months so Moving Averages have enough data to calculate correctly
    hist = stock.history(period="3mo") 
    
    try: news = stock.news[:3]
    except: news = []
    
    if not hist.empty:
        # Calculate Moving Averages
        hist['SMA_10'] = hist['Close'].rolling(window=10).mean()
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        
        # Calculate RSI (14-day)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))

        # Slice the last 30 days for the chart, and 15 days for the table
        chart_data = hist.tail(30).copy()
        chart_data.index = chart_data.index.strftime('%Y-%m-%d')
        
        table_data = hist[['Open', 'High', 'Low', 'Close', 'Volume', 'RSI']].tail(15).copy()
        table_data.index = table_data.index.strftime('%Y-%m-%d')
        table_data[['Open', 'High', 'Low', 'Close', 'RSI']] = table_data[['Open', 'High', 'Low', 'Close', 'RSI']].round(2)
        
        return chart_data, table_data, news
    return pd.DataFrame(), pd.DataFrame(), news

# Layout
num_cols = 2 if len(stocks_to_display) > 1 else 1
cols = st.columns(num_cols)

for index, (company_name, ticker) in enumerate(stocks_to_display.items()):
    col = cols[index % num_cols]
    
    with col:
        st.subheader(f":blue[{company_name}] ({ticker})")
        
        chart_df, table_df, news = get_stock_data(ticker)
        
        if not table_df.empty:
            latest_close = table_df['Close'].iloc[-1]
            previous_close = table_df['Close'].iloc[-2]
            pct_change = ((latest_close - previous_close) / previous_close) * 100
            latest_rsi = table_df['RSI'].iloc[-1]
            
            # --- TOP METRICS ---
            col1, col2 = st.columns(2)
            col1.metric("Latest Close", f"₹{latest_close:.2f}", f"{pct_change:.2f}%")
            
            # Color code RSI (Red if overbought >70, Green if oversold <30, Gray otherwise)
            rsi_color = "normal" if 30 <= latest_rsi <= 70 else ("inverse" if latest_rsi > 70 else "off")
            col2.metric("RSI (14-Day)", f"{latest_rsi:.2f}", 
                        delta="Overbought" if latest_rsi > 70 else ("Oversold" if latest_rsi < 30 else "Neutral"), 
                        delta_color=rsi_color)
            
            # --- INTERACTIVE CANDLESTICK CHART ---
            fig = go.Figure()
            
            # 1. Add Candlestick
            fig.add_trace(go.Candlestick(x=chart_df.index,
                            open=chart_df['Open'], high=chart_df['High'],
                            low=chart_df['Low'], close=chart_df['Close'],
                            name='Price'))
            
            # 2. Add 10-Day Moving Average
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['SMA_10'], 
                                     mode='lines', name='10-Day SMA', line=dict(color='blue', width=1.5)))
            
            # 3. Add 20-Day Moving Average
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['SMA_20'], 
                                     mode='lines', name='20-Day SMA', line=dict(color='orange', width=1.5)))
            
            # Clean up the chart layout
            fig.update_layout(
                xaxis_rangeslider_visible=False, # Hides the bulky bottom slider
                height=350 if num_cols == 1 else 300,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # --- DATA TABLE ---
            st.write("**15-Day Historical Data**")
            styled_df = table_df.style.background_gradient(subset=['Close'], cmap='Blues') \
                                      .background_gradient(subset=['Volume'], cmap='Purples')
            st.dataframe(styled_df, use_container_width=True)
            
            # --- LATEST NEWS ---
            with st.expander("📰 View Latest News"):
                if news:
                    for article in news:
                        title = article.get('title', 'No Title Available')
                        link = article.get('link', '#')
                        publisher = article.get('publisher', 'Unknown')
                        st.markdown(f"- [{title}]({link}) *(Source: {publisher})*")
                else:
                    st.write("No recent news found for this ticker.")
            
        else:
            st.error(f"Could not fetch data for {company_name}")
            
        if num_cols > 1:
            st.divider()

st.caption(f"Data last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data provided by Yahoo Finance")