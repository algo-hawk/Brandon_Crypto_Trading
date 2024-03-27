import datetime
import time
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def get_since_timestamp(days=0, weeks=0, months=0, years=0):
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=days, weeks=weeks) + datetime.timedelta(days=30*months) + datetime.timedelta(days=365*years)
    since_time = now - delta
    since_timestamp = int(time.mktime(since_time.timetuple()))
    return since_timestamp


#Need to fix this fucking plot on rsi thing
def plot_rsi_ema_strategy(data, rsi_buy_threshold, rsi_sell_threshold):
    """
    1. Strategy Plot (RSI and EMA Strategy)
    """
    # Replace infinite values with NaN and drop rows where RSI is NaN
    data = data.replace([np.inf, -np.inf, 0], np.nan).dropna(subset=["RSI"])
    print(data)

    # Create a subplot with 2 rows
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02, subplot_titles=('Price and Trade Signals', 'RSI Indicator'),
                        row_heights=[0.7, 0.3])

    # Add price and EMA data to the first row
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['open'],
                                 high=data['high'],
                                 low=data['low'],
                                 close=data['close'],
                                 name='Price'), row=1, col=1)

    fig.add_trace(go.Scatter(x=data.index, y=data['short_ema'],
                             line=dict(color='orange', width=2), name='Short EMA'), row=1, col=1)

    fig.add_trace(go.Scatter(x=data.index, y=data['long_ema'],
                             line=dict(color='purple', width=2), name='Long EMA'), row=1, col=1)

    # Add buy and sell signals
    fig.add_trace(go.Scatter(x=data[data['signal'] == 1].index,
                             y=data[data['signal'] == 1]['close'],
                             mode='markers', marker=dict(symbol='triangle-up', color='green', size=10), name='Buy'), row=1, col=1)

    fig.add_trace(go.Scatter(x=data[data['signal'] == -1].index,
                             y=data[data['signal'] == -1]['close'],
                             mode='markers', marker=dict(symbol='triangle-down', color='red', size=10), name='Sell'), row=1, col=1)

    # Add RSI to the second row
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'],
                             line=dict(color='blue', width=2), name='RSI'), row=2, col=1)

    # Add overbought and oversold lines on RSI subplot
    fig.add_hline(y=rsi_sell_threshold, line_dash="dot", line_color="red", annotation_text="Overbought", row=2, col=1)
    fig.add_hline(y=rsi_buy_threshold, line_dash="dot", line_color="green", annotation_text="Oversold", row=2, col=1)

    # Update layout for the entire figure
    fig.update_layout(height=800, title='Price Action and RSI Indicator', xaxis_title='Date', yaxis_title='Price',
                      xaxis_rangeslider_visible=False)

    # Specify the range for the RSI subplot's y-axis
    fig.update_yaxes(range=[0, 100], row=2, col=1)

    return fig