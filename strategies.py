from abc import ABC, abstractmethod
import numpy as np
import random
import streamlit as st

class Strategy(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def generate_signals(self, params):
        """
        Generate trading signals based on provided parameters.
        This method should be implemented by concrete strategy classes.
        """
        pass

    @abstractmethod
    def evaluate_strategy(self, params):
        """
        Evaluate strategy performance using generated signals and return performance metrics.
        Concrete implementations should use the output of `generate_signals` for this purpose.
        This method must return a dictionary of performance metrics.
        """
        pass

    @abstractmethod
    def get_parameter_ranges(self):
        """
        Return parameter ranges for the strategy.
        This method should be implemented by concrete strategy classes.
        """
        pass

    def optimize(self, iterations=100, weights=None):
        """
        Optimize strategy parameters based on weighted performance metrics.
        """
        if weights is None:
            weights = {'profit_factor': 0.4, 'win_rate': 0.3, 'max_drawdown': -0.2, 'sharpe_ratio': 0.1}

        best_score = None
        best_params = None

        for _ in range(iterations):
            # Generate a random parameter set from defined ranges
            params = {key: random.choice(range(*value)) for key, value in self.get_parameter_ranges().items()}

            # Evaluate strategy performance for the current set of parameters
            metrics = self.evaluate_strategy(params)

            # Calculate the weighted score for the current set of parameters
            score = sum(metrics[metric] * weight for metric, weight in weights.items())

            # Update best parameters if the current score is better
            if best_score is None or score > best_score:
                best_score = score
                best_params = params

        return best_params

class MomentumBasedTradingStrategy(Strategy):
    def __init__(self, data):
        super().__init__(data)
        self.short_ema_window = 4
        self.long_ema_window = 20
        self.rsi_window = 8
        self.rsi_buy_threshold = 30
        self.rsi_sell_threshold = 70

        #SUPER FUCKING IMPORTANT THE DATA IS BACKWARDS FROM EXCHANGE NEED TO REVERSE IT
        self.data.sort_index(ascending=True, inplace=True)

    def get_parameter_ranges(self):
        return {
            'short_ema_window': (5, 35),  # Adjusted as per strategy focus
            'long_ema_window': (12, 80),
            'rsi_window': (5, 60),
            'rsi_buy_threshold': (30, 51),
            'rsi_sell_threshold': (50, 71),
        }

    def generate_signals(self):
        historical_data = self.data.copy()

        # Calculate indicators
        historical_data['short_ema'] = historical_data['close'].ewm(span=self.short_ema_window, adjust=False).mean()
        historical_data['long_ema'] = historical_data['close'].ewm(span=self.long_ema_window, adjust=False).mean()
        delta = historical_data['close'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=self.rsi_window - 1, adjust=False).mean()
        ema_down = down.ewm(com=self.rsi_window - 1, adjust=False).mean()
        rs = ema_up / ema_down
        historical_data['RSI'] = 100 - (100 / (1 + rs))

        historical_data['signal'] = 0  # Initialize signals column

        # Check if the initial condition is a buy
        if historical_data['short_ema'].iloc[0] > historical_data['long_ema'].iloc[0] and historical_data['RSI'].iloc[
            0] > self.rsi_buy_threshold:
            historical_data.at[historical_data.index[0], 'signal'] = 1
            in_position = True
        else:
            in_position = False

        for i in range(1, len(historical_data)):
            # Buy Condition: Not in position, Short EMA > Long EMA, RSI above buy threshold
            if not in_position and historical_data['short_ema'].iloc[i] > historical_data['long_ema'].iloc[i] and \
                    historical_data['RSI'].iloc[i] > self.rsi_buy_threshold:
                #print('made it to buy first')
                historical_data.at[historical_data.index[i], 'signal'] = 1
                in_position = True
            # Sell Condition: In position, Short EMA < Long EMA, RSI below sell threshold
            elif in_position and historical_data['short_ema'].iloc[i] < historical_data['long_ema'].iloc[i] and \
                    historical_data['RSI'].iloc[i] < self.rsi_sell_threshold:
                #print('made it to sell first')
                historical_data.at[historical_data.index[i], 'signal'] = -1
                in_position = False

        return historical_data[['close', 'short_ema', 'long_ema', 'RSI', 'signal', 'open', 'high', 'low']]
    def evaluate_strategy(self, risk_free_rate=0.0):
        # Generate signals
        data = self.generate_signals()

        # Calculate daily returns
        data['returns'] = data['close'].pct_change()

        # Track whether we are holding the asset
        holding = False

        # Track the strategy returns
        data['strategy_returns'] = 0.0

        # Evaluate strategy returns based on holding periods
        for i in range(1, len(data)):
            if data.at[data.index[i], 'signal'] == 1:  # Buy signal
                holding = True
            elif data.at[data.index[i], 'signal'] == -1 and holding:  # Sell signal
                holding = False

            # If we are holding, calculate the strategy's returns
            if holding:
                data.at[data.index[i], 'strategy_returns'] = data.at[data.index[i], 'returns']

        # Total Return of the strategy
        total_return = data['strategy_returns'].sum()

        # Win Rate: percentage of positive returns
        win_rate = (data['strategy_returns'] > 0).mean()

        # Maximum Drawdown
        cumulative_returns = (1 + data['strategy_returns'].cumsum())
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min()

        # Compile metrics into a dictionary
        metrics = {
            'total_return': total_return,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
        }


        return metrics, data

    def optimize(self, iterations, metric_weights):
        if metric_weights is None:
            metric_weights = {
                'total_return': 1.0,
                'win_rate': 0,
                'max_drawdown': 0,  # Negative since we want to minimize drawdown
            }

        best_score = -np.inf
        best_params = {}
        #random.seed(42)  # Setting a random seed for reproducibility

        parameter_ranges = self.get_parameter_ranges()

        for i in range(iterations):
            params = {k: random.choice(range(*v)) for k, v in parameter_ranges.items()}
            self.update_parameters(params)
            metrics, data = self.evaluate_strategy()  # Ensure this method returns the necessary metrics
            score = self.calculate_score(metrics, metric_weights)

            if score > best_score:
                best_score = score
                best_params = params
        return best_params

    def calculate_score(self, metrics, metric_weights):
        # Calculate score
        score = sum(metrics[metric] * weight for metric, weight in metric_weights.items())
        return score

    def update_parameters(self, params):
        for param, value in params.items():
            setattr(self, param, value)



















