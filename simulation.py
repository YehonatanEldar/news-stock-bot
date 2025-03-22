import datetime
import os
from datetime import timedelta
from enum import Enum

import numpy as np
import pandas as pd
import yfinance as yf

from AI_analysis import get_signal
from constants import TradeAction


class Simulation:
    def __init__(self, initial_balance, company_list):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.company_list = company_list
        print('Loading company history data...')
        self.company_history_list = {company: yf.Ticker(company).history(period="1y") for company in company_list}
        print('Company history data loaded.')
        self.date = datetime.datetime.now()
        self.portfolio = {}

    def get_price(self, company: str) -> float | None:

        try:
            return self.company_history_list[company].loc[self.date.strftime('%Y-%m-%d')]['Close']
        except KeyError:
            print(f"Data not found for {company} on {self.date.strftime('%Y-%m-%d')}")
            return None

    def trade(self, action, company, quantity):
        price = self.get_price(company)
        if price is None:
            return

        cost = price * quantity

        if action == TradeAction.BUY:
            if self.balance >= cost:
                self.balance -= cost
                if company in self.portfolio:
                    self.portfolio[company] += quantity
                else:
                    self.portfolio[company] = quantity
                print(f"Bought {quantity} shares of {company} at ${price:.2f} each.")
            else:
                print("Insufficient funds to buy shares.")
        
        elif action == TradeAction.SELL:
            if company in self.portfolio and self.portfolio[company] >= quantity:
                self.balance += cost
                self.portfolio[company] -= quantity
                print(f"Sold {quantity} shares of {company} at ${price:.2f} each.")
            else:
                print("Insufficient shares to sell.")

        elif action == TradeAction.NOTHING:
            print("No action taken.")

    def date_increment(self):
        self.date += timedelta(days=1)

    def get_SMA(self, company, days):
        """
        Calculate the Simple Moving Average (SMA) for a given company and number of days.
        """
        history = self.company_history_list[company]
        return history['Close'].rolling(window=days).mean()
    
    def get_EMA(self, company, days):
        """
        Calculate the Exponential Moving Average (EMA) for a given company and number of days.
        """
        history = self.company_history_list[company]
        
        # Drop NaN values to avoid issues with empty slots
        clean_close = history['Close'].dropna()
        ema_series = clean_close.ewm(span=days, adjust=False).mean()
        
        # Check if the date exists in the index
        if self.date.strftime('%Y-%m-%d') in ema_series.index:
            return ema_series[self.date.strftime('%Y-%m-%d')]
        else:
            # Find the most recent previous date that exists in the index
            available_dates = ema_series.index[ema_series.index < self.date.strftime('%Y-%m-%d')]
            if not available_dates.empty:
                previous_date = available_dates[-1]
                print(f"No EMA data available for {company} on {self.date.strftime('%Y-%m-%d')}. Using data from {previous_date}.")
                return ema_series[previous_date]
            else:
                print(f"No EMA data available for {company} on {self.date.strftime('%Y-%m-%d')} or any previous date. Skipping.")
                return None
    
    def run(self, days, days_back=None):
        """
        Run the simulation for the specified number of days.

        Args:
            days (int): The number of days to simulate.
            days_back (int, optional): Start the simulation from this many days back.
        """
        if days_back:
            self.date = datetime.datetime.now() - datetime.timedelta(days=days_back)
        else:
            self.date = datetime.datetime.now() - datetime.timedelta(days=days)

        for day in range(days):
            print(f"\033[1m\nDay {day + 1}: {self.date.strftime('%Y-%m-%d')}\033[0m")
            for company in self.company_list:
                AI_signal, AI_quantity = get_signal(company, self.date)
                
                # Get EMAs and handle missing data
                short_EMA = self.get_EMA(company, 50)
                long_EMA = self.get_EMA(company, 200)
                
                if short_EMA is None or long_EMA is None:
                    print(f"Skipping {company} on {self.date.strftime('%Y-%m-%d')} due to missing EMA data.")
                    continue
                

                calc_signal = TradeAction.BUY if short_EMA > long_EMA else TradeAction.SELL
                signal = AI_signal if AI_signal == calc_signal else TradeAction.NOTHING
                self.trade(signal, company, AI_quantity)
            
            self.date_increment()

    def get_results(self):
        """
        Calculate and return the simulation results.
        """
        total_stock_value = sum(
            self.portfolio[company] * self.get_price(company)
            for company in self.portfolio
            if self.get_price(company) is not None
        )
        total_value = self.balance + total_stock_value
        gain = total_value - self.initial_balance

        # Format gain/loss with color
        if gain >= 0:
            gain_str = f"\033[92m${gain:.2f}\033[0m"  # Green for gain
        else:
            gain_str = f"\033[91m${gain:.2f}\033[0m"  # Red for loss

        return f"""
        Simulation Results:
        Initial Balance: ${self.initial_balance:.2f}
        Final Balance: ${self.balance:.2f}
        Total Stock Value: ${total_stock_value:.2f}
        Total Portfolio Value: ${total_value:.2f}
        Net Gain/Loss: {gain_str}
        Portfolio: {self.portfolio}
        """

