
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
        # User inputs for cryptocurrency pair
        symbol = st.text_input("Enter Cryptocurrency Pair (e.g., XBTUSD)", "XBTUSD")

        # Assuming strategy_params contains the timeframes
        selected_timeframe_key = st.selectbox("Select Timeframe", list(strategy_params.keys()))

        return symbol, selected_timeframe_key

    def pull_strategy_data(self, symbol, strategy_key):
        params = strategy_params[strategy_key]
        data = self.kraken_client.get_ohlc_data(symbol, params["interval"], params["since"])
        print(data)
        return data



    def run(self):
        symbol, selected_strategy_key = self.setup_page()
        if st.button("Analyze Strategy With Optimized Params"):
            data = self.pull_strategy_data(symbol, selected_strategy_key)
            if data is not None:
                st.title("Optimize Momentum Trading Strategy")

                iterations = st.number_input('Number of iterations for optimization:', min_value=10, max_value=1000000,value=100, step=10)

                strategy = MomentumBasedTradingStrategy(data)

                # Retrieve weight list from strategy parameters
                metric_weights = strategy_params[selected_strategy_key]['weight_list']

                # Pass the update_progress function directly
                best_params = strategy.optimize(data, iterations, metric_weights)

                st.write("Optimization Completed.")
                st.write("Best Parameters Found:", best_params)

                #Update Strategy Params
                strategy.update_parameters(best_params)

                # Run strategy with optimized parameters
                metrics, optimized_signals = strategy.evaluate_strategy()
                print(optimized_signals)

                st.write('Metrics of Optimized Strategy:')
                st.write(metrics)
                optimized_plot = plot_rsi_ema_strategy(optimized_signals)
                st.plotly_chart(optimized_plot, use_container_width=True)



#-----------------------------------------------------------------------------------------------------------------------
# Strategy Parameters
strategy_params = {
    "intraday_15m": {
        "interval": 15,
        "since": get_since_timestamp(days=1),
        "weight_list": {
            'total_return': .5,
            'win_rate': .4,
            'max_drawdown': .1,  # Less emphasis on drawdown for shorter strategies
        }
    },
    "intraday_1h": {
        "interval": 60,
        "since": get_since_timestamp(weeks=1),
        "weight_list": {
            'total_return': .5,
            'win_rate': 0.4,
            'max_drawdown': 0.1,
        }
    },
    "intraday_4h": {
        "interval": 240,
        "since": get_since_timestamp(weeks=2),
        "weight_list": {
            'total_return': 0.5,
            'win_rate': 0.4,
            'max_drawdown': 0.1,
        }
    },
    "short_term": {
        "interval": 240,
        "since": get_since_timestamp(months=1),
        "weight_list": {
            'total_return': 0.25,
            'win_rate': 0.25,
            'max_drawdown': 0.25,
        }
    },
    "medium_term": {
        "interval": 1440,
        "since": get_since_timestamp(months=4),
        "weight_list": {
            'total_return': 0.2,
            'win_rate': 0.2,
            'max_drawdown': 0.3,  # Increasing emphasis on drawdown
        }
    },
    "long_term": {
        "interval": 1440,
        "since": get_since_timestamp(years=1),
        "weight_list": {
            'total_return': 0.15,
            'win_rate': 0.15,
            'max_drawdown': 0.35,
        }
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



