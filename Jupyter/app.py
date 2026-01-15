import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import shap
import matplotlib.pyplot as plt
import yfinance as yf
import requests
import xgboost as xgb
import lightgbm as lgb

# --- Page Configuration ---
st.set_page_config(
    page_title="Signal BTC | AI-Powered Bitcoin Forecast",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Professional Styling & Theming ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background */
    .stApp {
        background-color: #0F172A;
        color: #E2E8F0;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }

    /* Metric styling */
    .stMetric {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 0.5rem;
        padding: 1rem;
    }

    .stMetric .css-1xarl3l {
        color: #94A3B8; /* Metric label */
    }

    /* Button styling */
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.75rem 1.5rem;
    }
    .stButton>button:hover {
        background-color: #2563EB;
    }

    /* Expander styling */
    .stExpander {
        border: 1px solid #334155;
        border-radius: 0.5rem;
    }

    /* Live Ticker Styling */
    @keyframes scroll {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background-color: #1E293B;
        padding: 0.5rem 0;
        border-bottom: 1px solid #334155;
    }
    .ticker {
        display: inline-block;
        white-space: nowrap;
        animation: scroll 40s linear infinite;
    }
    .ticker-item {
        display: inline-block;
        padding: 0 1.5rem;
        font-size: 0.9rem;
        color: #94A3B8;
    }
    .ticker-item span {
        color: #E2E8F0;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .positive { color: #22C55E !important; }
    .negative { color: #EF4444 !important; }

</style>
""", unsafe_allow_html=True)


# --- Data Fetching Functions ---
@st.cache_data(ttl=900) # Cache for 15 minutes
def fetch_ticker_data():
    """Fetches live price data for top cryptocurrencies for the ticker."""
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=15&page=1&sparkline=false"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=3600)
def fetch_price_data(ticker="BTC-USD", period="2y", interval="1d"):
    """Fetches historical OHLCV data from Yahoo Finance."""
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
    if df.empty: return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = df.index.tz_localize(None)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df.index.name = 'timestamp'
    return df

@st.cache_data(ttl=86400)
def fetch_github_commits(repo="bitcoin/bitcoin"):
    """Fetches commit history for a given GitHub repository."""
    all_commits = []
    for page in range(1, 4):
        url = f"https://api.github.com/repos/{repo}/commits"
        response = requests.get(url, params={'per_page': 100, 'page': page})
        if response.status_code == 200:
            all_commits.extend(response.json())
        else:
            break
    if all_commits:
        commit_dates = [c['commit']['author']['date'] for c in all_commits]
        df = pd.DataFrame(commit_dates, columns=['timestamp'])
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None).dt.normalize()
        return df.groupby('timestamp').size().rename('commits')
    return pd.Series(name='commits')

@st.cache_data(ttl=86400)
def fetch_hash_rate():
    """Fetches Bitcoin hash rate data from Blockchain.com."""
    url = "https://api.blockchain.info/charts/hash-rate?timespan=2years&format=json"
    response = requests.get(url)
    if response.status_code == 200 and response.json().get('values'):
        data = response.json()['values']
        df = pd.DataFrame(data)
        df['x'] = pd.to_datetime(df['x'], unit='s')
        return df.rename(columns={'x': 'timestamp', 'y': 'hash_rate'}).set_index('timestamp')['hash_rate']
    return pd.Series(name='hash_rate')

@st.cache_data(ttl=86400)
def fetch_fear_and_greed():
    """Fetches the Fear and Greed Index for the last 2 years."""
    url = "https://api.alternative.me/fng/?limit=730&format=json"
    response = requests.get(url)
    if response.status_code == 200 and response.json().get('data'):
        data = response.json()['data']
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.rename(columns={'value': 'fear_and_greed'}).set_index('timestamp')
        df['fear_and_greed'] = pd.to_numeric(df['fear_and_greed'])
        return df[['fear_and_greed']]
    return pd.DataFrame(columns=['fear_and_greed'])

@st.cache_data(ttl=3600)
def fetch_market_data():
    """Fetches S&P 500, Gold, ETH, and SOL prices for the last 2 years."""
    tickers = ["^GSPC", "GC=F", "ETH-USD", "SOL-USD"]
    full_df = yf.download(tickers=tickers, period="2y", interval="1d", auto_adjust=True)
    if full_df.empty: return pd.DataFrame()

    df = full_df['Close']
    df.index = df.index.tz_localize(None)
    df = df.rename(columns={"^GSPC": "sp500", "GC=F": "gold", "ETH-USD": "eth", "SOL-USD": "sol"})

    df['sp500_returns'] = np.log(df['sp500'] / df['sp500'].shift(1))
    df['gold_returns'] = np.log(df['gold'] / df['gold'].shift(1))
    df['eth_returns'] = np.log(df['eth'] / df['eth'].shift(1))
    df['sol_returns'] = np.log(df['sol'] / df['sol'].shift(1))

    return df[['sp500_returns', 'gold_returns', 'eth_returns', 'sol_returns']]

# --- Feature Engineering & Model Training ---
def prepare_features(price_df, commits, hash_rate, fng, market_data):
    df = price_df.copy()
    df['returns'] = np.log(df['Close'] / df['Close'].shift(1))
    df['ma_20'] = df['Close'].rolling(window=20).mean()
    df['ma_100'] = df['Close'].rolling(window=100).mean()
    df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(20)
    all_daily_data = pd.concat([commits, hash_rate, fng, market_data], axis=1)
    df = df.join(all_daily_data)
    df = df.ffill()
    df['commits_ewma'] = df['commits'].ewm(span=7).mean()
    df['hash_rate_zscore'] = (df['hash_rate'] - df['hash_rate'].rolling(30).mean()) / df['hash_rate'].rolling(30).std()
    return df.dropna()

def train_model(df, prediction_horizon, model_type='XGBoost'):
    df['target'] = df['returns'].shift(-prediction_horizon)
    df_train = df.dropna()
    FEATURES = ['returns', 'ma_20', 'ma_100', 'volatility', 'Volume',
                'commits_ewma', 'hash_rate_zscore',
                'fear_and_greed', 'sp500_returns', 'gold_returns',
                'eth_returns', 'sol_returns']
    TARGET = 'target'
    for feature in FEATURES:
        if feature not in df_train.columns:
            df_train[feature] = 0
    X = df_train[FEATURES]
    y = df_train[TARGET]
    if len(X) < 2: return None, pd.DataFrame(), 0.0

    if model_type == 'XGBoost':
        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=3, seed=42)
    elif model_type == 'LightGBM':
        model = lgb.LGBMRegressor(objective='regression', n_estimators=100, learning_rate=0.1, num_leaves=31, seed=42)

    model.fit(X.iloc[:-1], y.iloc[:-1])
    prediction = model.predict(X.iloc[[-1]])[0]
    return model, X, float(prediction)

# --- Main Pipeline Function ---
def run_full_pipeline(prediction_horizon, model_type):
    """Encapsulates the entire data fetching, processing, and model training pipeline."""
    with st.spinner("⏳ Running forecast... This may take a moment."):
        price_data_raw = fetch_price_data()
        if price_data_raw.empty:
            st.error("Fatal Error: Could not fetch Bitcoin price data. The app cannot continue.")
            st.stop()

        github_data = fetch_github_commits()
        mining_data = fetch_hash_rate()
        fng_data = fetch_fear_and_greed()
        market_data = fetch_market_data()

        features_df = prepare_features(price_data_raw, github_data, mining_data, fng_data, market_data)
        if features_df.empty:
            st.error("Fatal Error: Feature DataFrame is empty after processing. One of the data sources might be down.")
            st.stop()

        model, X_data, prediction = train_model(features_df, prediction_horizon, model_type)

        st.session_state.price_data_raw = price_data_raw
        st.session_state.features_df = features_df
        st.session_state.model = model
        st.session_state.X_data = X_data
        st.session_state.prediction = prediction
        st.session_state.horizon = prediction_horizon
        st.session_state.model_type = model_type

# --- Main App UI ---

# --- Live Ticker ---
ticker_data = fetch_ticker_data()
if ticker_data:
    ticker_html = "".join([
        f"""<div class="ticker-item">{d['symbol'].upper()}<span>${d['current_price']:,.2f}</span> <span class="{'positive' if d['price_change_percentage_24h'] >= 0 else 'negative'}">{d['price_change_percentage_24h']:.2f}%</span></div>"""
        for d in ticker_data
    ])
    st.markdown(f'<div class="ticker-wrap"><div class="ticker">{ticker_html}</div></div>', unsafe_allow_html=True)

# --- Header ---
st.title("📈 Signal BTC")
st.subheader("AI-Powered Bitcoin Price Forecasting")

# --- Sidebar Controls ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png")
    st.title("⚙️ Controls")
    st.write("Adjust the model parameters and re-run the forecast.")

    model_type = st.selectbox("Select Model", ("XGBoost", "LightGBM"))
    prediction_horizon = st.slider("Prediction Horizon (Days)", 1, 30, 7, key="horizon_slider")

    rerun_button = st.button("🚀 Re-run Forecast", use_container_width=True)

# --- Main Pipeline Execution Logic ---
if rerun_button or 'prediction' not in st.session_state or st.session_state.get('horizon') != prediction_horizon or st.session_state.get('model_type') != model_type:
    if rerun_button:
        st.cache_data.clear()
    run_full_pipeline(prediction_horizon, model_type)

# --- Display Results ---
prediction = st.session_state.prediction
features_df = st.session_state.features_df
price_data_raw = st.session_state.price_data_raw
model = st.session_state.model
X_data = st.session_state.X_data
last_price = price_data_raw['Close'].iloc[-1]

st.subheader(f"Forecast for the next {prediction_horizon} days using {model_type}")
col1, col2, col3, col4 = st.columns(4)
col1.metric(f"Predicted Return", f"{prediction * 100:.2f}%")
signal = "STRONG BUY" if prediction > 0.01 else "BUY" if prediction > 0.001 else "STRONG SELL" if prediction < -0.01 else "SELL" if prediction < -0.001 else "NEUTRAL HOLD"
col2.metric("AI Signal", signal)
col3.metric("Market Volatility", f"{features_df['volatility'].iloc[-1]:.3f}")
col4.metric("Last BTC Price (USD)", f"${last_price:,.2f}")

csv = features_df.to_csv().encode('utf-8')
st.sidebar.download_button(
    "📥 Download Feature Dataset (CSV)", csv, f"bitcoin_features_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv"
)

st.markdown("---")

# --- Visualizations ---
st.subheader("Analysis & Visualizations")
tab1, tab2, tab3 = st.tabs(["📈 Price & Technicals", "👻 Market Sentiment", "🔗 Feature Correlations"])

with tab1:
    fig_price = go.Figure(data=[go.Candlestick(x=price_data_raw.index, open=price_data_raw['Open'], high=price_data_raw['High'], low=price_data_raw['Low'], close=price_data_raw['Close'], name='BTC Price')])
    fig_price.add_trace(go.Scatter(x=features_df.index, y=features_df['ma_20'], mode='lines', name='20-Day MA'))
    fig_price.add_trace(go.Scatter(x=features_df.index, y=features_df['ma_100'], mode='lines', name='100-Day MA'))
    fig_price.update_layout(title='Bitcoin Price (Daily OHLC)', template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_price, use_container_width=True)

with tab2:
    fig_fng = go.Figure()
    fig_fng.add_trace(go.Scatter(x=features_df.index, y=features_df['fear_and_greed'], fill='tozeroy', name='F&G Index'))
    fig_fng.add_hrect(y0=0, y1=25, line_width=0, fillcolor="red", opacity=0.2, annotation_text="Extreme Fear")
    fig_fng.add_hrect(y0=75, y1=100, line_width=0, fillcolor="green", opacity=0.2, annotation_text="Extreme Greed")
    fig_fng.update_layout(title="Fear & Greed Index Over Time", template='plotly_dark')
    st.plotly_chart(fig_fng, use_container_width=True)

with tab3:
    corr_cols = ['returns', 'Volume', 'volatility', 'commits_ewma', 'hash_rate_zscore',
                 'fear_and_greed', 'sp500_returns', 'gold_returns', 'eth_returns', 'sol_returns']
    corr_df = features_df[corr_cols].corr()
    fig_corr = px.imshow(corr_df, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r', title="Feature Correlation Matrix")
    st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("---")

# --- Explainability ---
st.header("💡 AI Prediction Breakdown")
if model and not X_data.empty:
    with st.expander("Show Feature Importance (SHAP Analysis)"):
        st.write("This SHAP plot shows the impact of each feature on the model's output for the most recent prediction. Features in **red** push the price prediction **higher**, while features in **blue** push it **lower**.")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer(X_data.iloc[[-1]])

        # --- IMPROVED PLOT STYLING ---
        fig, ax = plt.subplots(facecolor='#0F172A')
        ax.set_facecolor('#0F172A')
        ax.tick_params(colors='#E2E8F0', which='both')
        plt.rcParams['text.color'] = '#E2E8F0'

        shap.waterfall_plot(shap_values[0], max_display=15, show=False)

        fig.set_size_inches(10, 6)
        ax.set_title("SHAP Feature Contribution", color="#E2E8F0", fontsize=16)
        ax.figure.tight_layout()
        st.pyplot(fig, clear_figure=True)
else:
    st.warning("Not enough data to generate SHAP plot.")

