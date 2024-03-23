import krakenex
from pykrakenapi import KrakenAPI
import streamlit as st
class KrakenAPIWrapper:
    """
    Handles interaction with the Kraken API.
    For now, it just pulls data.
    """
    def __init__(self, api_key, api_secret):
        self.kraken = krakenex.API(key=api_key, secret=api_secret)
        self.kapi = KrakenAPI(self.kraken)

    #@st.cache_data
    def get_ohlc_data(self, pair, interval, since=None):
        """Fetch OHLC data for a specified currency pair and interval."""
        ohlc, last = self.kapi.get_ohlc_data(pair, interval=interval, since=since)
        return ohlc