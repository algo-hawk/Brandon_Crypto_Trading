
import streamlit as st
from kraken_api import KrakenAPIWrapper
from strategies import MomentumBasedTradingStrategy
from utils import get_since_timestamp, plot_rsi_ema_strategy


#-----------------------------------------------------------------------------------------------------------------------
# Website Portion
class KrakenWebsiteTrader:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.kraken_client = KrakenAPIWrapper(api_key, api_secret)

    def setup_page(self):
        st.title("Crypto Trading Strategy Analysis")
        # User inputs for cryptocurrency pair and strategy selection
        symbol = st.text_input("Enter Cryptocurrency Pair (e.g., XBTUSD)", "XBTUSD")
        selected_strategy_key = st.selectbox("Select Strategy", list(strategy_params.keys()))
        return symbol, selected_strategy_key

    def fetch_and_analyze_strategy(self, symbol, strategy_key):
        # Fetching data for the selected strategy and cryptocurrency pair
        params = strategy_params[strategy_key]
        data = self.kraken_client.get_ohlc_data(symbol, params["interval"], params["since"])


        # Initialize the selected strategy
        if strategy_key in ['intraday_15m', 'intraday_1h', 'intraday_4h', 'short_term', 'medium_term', 'long_term']:
            strategy_instance = MomentumBasedTradingStrategy(data)
            signals = strategy_instance.generate_signals(data)
            metrics = strategy_instance.evaluate_strategy()

            # Display the results
            st.write(f"Strategy Metrics for {strategy_key}:")
            st.json(metrics)

            # Placeholder for displaying a chart for the strategy
            # st.plotly_chart(create_strategy_chart(signals))
            return signals

    def run(self):
        symbol, selected_strategy_key = self.setup_page()
        if st.button("Analyze Strategy"):
            rsi_ema_signals = self.fetch_and_analyze_strategy(symbol, selected_strategy_key)
            rsi_ema_strategy_figure = plot_rsi_ema_strategy(rsi_ema_signals)
            st.plotly_chart(rsi_ema_strategy_figure, use_container_width=True)































#-----------------------------------------------------------------------------------------------------------------------
 # Fixed Parameter Settings And Timeframes
# Strategy Parameters
strategy_params = {
    "intraday_15m": {
        "interval": 15,
        "since": get_since_timestamp(days=1),
    },
    "intraday_1h": {
        "interval": 60,
        "since": get_since_timestamp(weeks=1),
    },
    "intraday_4h": {
        "interval": 240,
        "since": get_since_timestamp(weeks=2),
    },

    "short_term": {
        "interval": 240,
        "since": get_since_timestamp(months=1),
    },
    "medium_term": {
        "interval": 1440,
        "since": get_since_timestamp(months=4),
    },
    "long_term": {
        "interval": 1440,
        "since": get_since_timestamp(years=1),
    },
}

# Timeframes for 'since' variable
timeframes = {
    "day": get_since_timestamp(days=1),
    "week": get_since_timestamp(weeks=1),
    "month": get_since_timestamp(months=1),
    "3_months": get_since_timestamp(months=3),
    "1_year": get_since_timestamp(years=1),
    "2_years": get_since_timestamp(years=2),
    "5_years": get_since_timestamp(years=5),
    "max": get_since_timestamp(years=10)  # Example, adjust based on how far back your 'max' should go
}

if __name__ == '__main__':
    api_key = ''
    api_secret = ''
    kraken_site = KrakenWebsiteTrader(api_key, api_secret)
    kraken_site.run()



