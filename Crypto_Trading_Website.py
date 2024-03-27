
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
        #print(data)
        return data

    def run(self):
        symbol, selected_strategy_key = self.setup_page()

        # Initialize 'iterations' in session state if it's not already set
        if 'iterations' not in st.session_state:
            st.session_state['iterations'] = 100

        # Declare the number_input with session state variable as the default value
        # The value in the widget will be automatically stored in 'st.session_state.iterations'
        iterations = st.number_input(
            'Number of iterations for optimization:',
            min_value=10,
            max_value=1000000,
            value=st.session_state['iterations'],
            step=10,
            key='iterations'  # Unique key for the widget to maintain its state
        )

        if st.button("Analyze Strategy With Optimized Params"):
            data = self.pull_strategy_data(symbol, selected_strategy_key)
            if data is not None:
                st.title("Optimize Momentum Trading Strategy")

                # Retrieve weight list from strategy parameters
                metric_weights = strategy_params[selected_strategy_key]['weight_list']

                # Initialize the strategy with data
                strategy = MomentumBasedTradingStrategy(data)

                # Run the optimization process
                best_params = strategy.optimize(st.session_state['iterations'], metric_weights)

                st.write("Optimization Completed.")
                st.write("Best Parameters Found:", best_params)

                # Update Strategy Params
                strategy.update_parameters(best_params)

                # Run strategy with optimized parameters
                metrics, optimized_signals = strategy.evaluate_strategy()
                st.write('Metrics of Optimized Strategy:')
                st.json(metrics)  # Using st.json for better formatting of dictionary

                # Plot the strategy signals
                optimized_plot = plot_rsi_ema_strategy(optimized_signals, strategy.rsi_buy_threshold, strategy.rsi_sell_threshold)
                st.plotly_chart(optimized_plot, use_container_width=True)



#-----------------------------------------------------------------------------------------------------------------------
# Strategy Parameters
strategy_params = {
    "intraday_15m": {
        "interval": 15,
        "since": get_since_timestamp(weeks=1),
        "weight_list": {
            'total_return': 1,
            'win_rate': 0,
            'max_drawdown': 0,
        }
    },

    "intraday_4h": {
        "interval": 240,
        "since": get_since_timestamp(weeks=3),
        "weight_list": {
            'total_return': 1,
            'win_rate': 0,
            'max_drawdown': 0,
        }
    },
    "short_term": {
        "interval": 240,
        "since": get_since_timestamp(months=2),
        "weight_list": {
            'total_return': 1,
            'win_rate': 0,
            'max_drawdown': 0,
        }
    },
    "medium_term": {
        "interval": 1440,
        "since": get_since_timestamp(months=6),
        "weight_list": {
            'total_return': 1,
            'win_rate': 0,
            'max_drawdown': 0,  # Increasing emphasis on drawdown
        }
    },
    "long_term": {
        "interval": 1440,
        "since": get_since_timestamp(years=1),
        "weight_list": {
            'total_return': 1,
            'win_rate': 0,
            'max_drawdown': 0,
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



