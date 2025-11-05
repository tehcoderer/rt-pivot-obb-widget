#!/usr/bin/env python3
"""
Portfolio Data Generator
Generates large-scale portfolio data with 35,000 positions and 200+ metrics
"""

import random
import string
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import time
import uuid

class PortfolioDataGenerator:
    def __init__(self):
        self.funds = ["GlobalEq", "FixedIncome", "Alternatives", "EmergingMkt", "SmallCap"]
        self.strategies = ["L/S Equity", "Market Neutral", "Event Driven", "Credit", "Quantitative"]
        self.pms = ["Jane Doe", "John Smith", "Alice Johnson", "Bob Wilson", "Carol Brown"]
        self.portfolios = ["Alpha Growth", "Beta Value", "Gamma Income", "Delta Momentum", "Epsilon Defensive"]
        self.sectors = ["Technology", "Healthcare", "Financial", "Energy", "Consumer", "Industrial", "Real Estate"]
        self.regions = ["North America", "Europe", "Asia Pacific", "Emerging Markets", "Global"]
        self.currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"]
        self.liquidity_flags = ["OK", "Watch", "Restricted", "Blocked"]
        
        # Generate base ticker pool
        self.tickers = self._generate_tickers(50000)
        
        # Real-time update tracking
        self.data_lock = threading.Lock()
        self.current_data = None
        self.update_thread = None
        self.running = False
        
    def _generate_tickers(self, count: int) -> List[str]:
        """Generate realistic ticker symbols"""
        tickers = []
        
        # Add some well-known tickers
        known_tickers = [
            "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "META", "NVDA", "JPM", "BAC", "WMT",
            "V", "MA", "PG", "JNJ", "UNH", "HD", "DIS", "VZ", "ADBE", "NFLX", "CRM",
            "ORCL", "INTC", "CSCO", "PFE", "KO", "PEP", "TMO", "ABT", "CVX", "XOM"
        ]
        tickers.extend(known_tickers)
        
        # Generate additional random tickers
        while len(tickers) < count:
            length = random.choice([3, 4, 5])
            ticker = ''.join(random.choices(string.ascii_uppercase, k=length))
            if ticker not in tickers:
                tickers.append(ticker)
                
        return tickers
    
    def _generate_base_metrics(self, row_count: int) -> pd.DataFrame:
        """Generate base portfolio metrics"""
        np.random.seed(42)  # For reproducible results
        
        data = []
        for i in range(row_count):
            fund = random.choice(self.funds)
            strategy = random.choice(self.strategies)
            pm = random.choice(self.pms)
            portfolio = random.choice(self.portfolios)
            ticker = random.choice(self.tickers)
            
            # Base position data
            quantity = random.randint(1000, 100000)
            price = random.uniform(10, 500)
            market_value = quantity * price
            
            row = {
                # Identifiers
                "Fund": fund,
                "Strategy": strategy,
                "PM": pm,
                "Portfolio": portfolio,
                "Ticker": ticker,
                "Quantity": quantity,
                "Price": round(price, 2),
                "MarketValue": round(market_value, 2),
                
                # P&L Metrics
                "PnL_Day": round(random.uniform(-50000, 150000), 2),
                "PnL_MTD": round(random.uniform(-200000, 800000), 2),
                "PnL_QTD": round(random.uniform(-500000, 2000000), 2),
                "PnL_YTD": round(random.uniform(-1000000, 5000000), 2),
                "PnL_1Y": round(random.uniform(-2000000, 8000000), 2),
                
                # Risk Metrics
                "VaR_95": round(random.uniform(100000, 1000000), 2),
                "VaR_99": round(random.uniform(200000, 1500000), 2),
                "Beta": round(random.uniform(0.5, 2.0), 3),
                "Volatility": round(random.uniform(0.1, 0.8), 3),
                "Sharpe": round(random.uniform(-2.0, 3.0), 3),
                "Sortino": round(random.uniform(-1.5, 4.0), 3),
                
                # Exposure Metrics
                "ADV%": round(random.uniform(0.1, 15.0), 1),
                "DaysToLiquidate": random.randint(1, 30),
                "LiquidityFlag": random.choice(self.liquidity_flags),
                
                # Sector/Region
                "Sector": random.choice(self.sectors),
                "Region": random.choice(self.regions),
                "Currency": random.choice(self.currencies),
                
                # Additional Identifiers
                "CUSIP": f"{random.randint(100000000, 999999999)}",
                "ISIN": f"US{random.randint(1000000000, 9999999999)}",
                "SEDOL": f"{random.randint(1000000, 9999999)}",
            }
            data.append(row)
            
        return pd.DataFrame(data)
    
    def _generate_extended_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add extended metrics to reach 200+ columns"""
        
        # Performance Attribution
        for period in ["1D", "1W", "1M", "3M", "6M", "1Y"]:
            df[f"Return_{period}"] = np.random.uniform(-0.1, 0.15, len(df))
            df[f"Alpha_{period}"] = np.random.uniform(-0.05, 0.08, len(df))
            df[f"TrackingError_{period}"] = np.random.uniform(0.01, 0.2, len(df))
        
        # Risk Decomposition
        for factor in ["Market", "Size", "Value", "Momentum", "Quality", "MinVol"]:
            df[f"Exposure_{factor}"] = np.random.uniform(-2.0, 2.0, len(df))
            df[f"Attribution_{factor}"] = np.random.uniform(-0.02, 0.02, len(df))
        
        # Trading Metrics
        df["AvgDailyVolume"] = np.random.uniform(10000, 10000000, len(df))
        df["BidSpread"] = np.random.uniform(0.001, 0.05, len(df))
        df["AskSpread"] = np.random.uniform(0.001, 0.05, len(df))
        df["LastTradeTime"] = pd.Timestamp.now()
        
        # ESG Metrics
        df["ESG_Score"] = np.random.uniform(1, 100, len(df))
        df["Carbon_Intensity"] = np.random.uniform(0, 1000, len(df))
        df["ESG_Rating"] = np.random.choice(["A", "B", "C", "D"], len(df))
        
        # Stress Test Results
        for scenario in ["2008_Crisis", "COVID_Crash", "Rate_Shock", "Credit_Spread"]:
            df[f"Stress_{scenario}"] = np.random.uniform(-0.4, 0.2, len(df))
        
        # Liquidity Metrics
        df["MarketImpact"] = np.random.uniform(0, 0.1, len(df))
        df["LiquidityScore"] = np.random.uniform(1, 10, len(df))
        df["TradingCost"] = np.random.uniform(0.001, 0.02, len(df))
        
        # Concentration Metrics
        df["PortfolioWeight"] = np.random.uniform(0.001, 0.05, len(df))
        df["FundWeight"] = np.random.uniform(0.001, 0.1, len(df))
        df["StrategyWeight"] = np.random.uniform(0.001, 0.2, len(df))
        
        # Technical Indicators
        for indicator in ["RSI", "MACD", "BB_Upper", "BB_Lower", "SMA_20", "SMA_50", "SMA_200"]:
            df[indicator] = np.random.uniform(0, 100, len(df))
        
        # Additional Financial Metrics
        df["MarketCap"] = np.random.uniform(1e9, 1e12, len(df))
        df["BookValue"] = np.random.uniform(5, 200, len(df))
        df["PE_Ratio"] = np.random.uniform(5, 50, len(df))
        df["PB_Ratio"] = np.random.uniform(0.5, 10, len(df))
        df["Dividend_Yield"] = np.random.uniform(0, 0.08, len(df))
        
        # Options Metrics
        df["ImpliedVol"] = np.random.uniform(0.1, 1.0, len(df))
        df["Delta"] = np.random.uniform(-1, 1, len(df))
        df["Gamma"] = np.random.uniform(0, 1, len(df))
        df["Theta"] = np.random.uniform(-1, 0, len(df))
        df["Vega"] = np.random.uniform(0, 1, len(df))
        
        # Macro Sensitivity
        for factor in ["IR_1Y", "IR_10Y", "FX_EUR", "FX_GBP", "Oil", "Gold", "VIX"]:
            df[f"Sensitivity_{factor}"] = np.random.uniform(-1, 1, len(df))
        
        # Additional P&L breakdowns
        for component in ["Carry", "Funding", "Dividends", "FX", "Tax"]:
            df[f"PnL_{component}"] = np.random.uniform(-10000, 50000, len(df))
        
        # Compliance Metrics
        df["InvestmentLimit"] = np.random.uniform(0.01, 0.1, len(df))
        df["RiskLimit"] = np.random.uniform(0.005, 0.05, len(df))
        df["ConcentrationLimit"] = np.random.uniform(0.02, 0.15, len(df))
        df["ComplianceStatus"] = np.random.choice(["Green", "Yellow", "Red"], len(df))
        
        return df
    
    def generate_portfolio_data(self, row_count: int = 35000) -> pd.DataFrame:
        """Generate complete portfolio dataset"""
        print(f"Generating {row_count} rows of portfolio data...")
        
        # Generate base metrics
        df = self._generate_base_metrics(row_count)
        
        # Add extended metrics to reach 200+ columns
        df = self._generate_extended_metrics(df)
        
        # Round numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].round(4)
        
        print(f"Generated dataset with {len(df)} rows and {len(df.columns)} columns")
        return df
    
    def create_hierarchical_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert flat data to hierarchical structure for tree mode"""
        
        # Group by Fund -> Strategy -> PM -> Portfolio
        hierarchy = {}
        
        for _, row in df.iterrows():
            fund = row["Fund"]
            strategy = row["Strategy"] 
            pm = row["PM"]
            portfolio = row["Portfolio"]
            
            # Initialize hierarchy levels
            if fund not in hierarchy:
                hierarchy[fund] = {
                    "Fund": fund,
                    "children": {},
                    "aggregates": {"MarketValue": 0, "PnL_Day": 0, "PnL_MTD": 0, "VaR_95": 0}
                }
            
            if strategy not in hierarchy[fund]["children"]:
                hierarchy[fund]["children"][strategy] = {
                    "Fund": fund,
                    "Strategy": strategy,
                    "children": {},
                    "aggregates": {"MarketValue": 0, "PnL_Day": 0, "PnL_MTD": 0, "VaR_95": 0}
                }
            
            if pm not in hierarchy[fund]["children"][strategy]["children"]:
                hierarchy[fund]["children"][strategy]["children"][pm] = {
                    "Fund": fund,
                    "Strategy": strategy,
                    "PM": pm,
                    "children": {},
                    "aggregates": {"MarketValue": 0, "PnL_Day": 0, "PnL_MTD": 0, "VaR_95": 0}
                }
            
            if portfolio not in hierarchy[fund]["children"][strategy]["children"][pm]["children"]:
                hierarchy[fund]["children"][strategy]["children"][pm]["children"][portfolio] = {
                    "Fund": fund,
                    "Strategy": strategy,
                    "PM": pm,
                    "Portfolio": portfolio,
                    "positions": [],
                    "aggregates": {"MarketValue": 0, "PnL_Day": 0, "PnL_MTD": 0, "VaR_95": 0}
                }
            
            # Add position and update aggregates
            position_data = row.to_dict()
            hierarchy[fund]["children"][strategy]["children"][pm]["children"][portfolio]["positions"].append(position_data)
            
            # Update aggregates at all levels
            for metric in ["MarketValue", "PnL_Day", "PnL_MTD", "VaR_95"]:
                hierarchy[fund]["aggregates"][metric] += row[metric]
                hierarchy[fund]["children"][strategy]["aggregates"][metric] += row[metric]
                hierarchy[fund]["children"][strategy]["children"][pm]["aggregates"][metric] += row[metric]
                hierarchy[fund]["children"][strategy]["children"][pm]["children"][portfolio]["aggregates"][metric] += row[metric]
        
        return hierarchy
    
    def start_real_time_updates(self, update_interval: float = 1.0):
        """Start real-time data updates"""
        if self.running:
            return
            
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, args=(update_interval,))
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def stop_real_time_updates(self):
        """Stop real-time data updates"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
    
    def _update_loop(self, interval: float):
        """Main update loop for real-time data"""
        while self.running:
            if self.current_data is not None:
                with self.data_lock:
                    self._apply_random_updates(self.current_data)
            time.sleep(interval)
    
    def _apply_random_updates(self, df: pd.DataFrame):
        """Apply random updates to simulate real-time market data"""
        # Update approximately 5% of positions each cycle
        update_count = max(1, len(df) // 20)
        update_indices = np.random.choice(len(df), update_count, replace=False)
        
        for idx in update_indices:
            # Price changes
            current_price = df.loc[idx, "Price"]
            price_change = np.random.normal(0, current_price * 0.002)  # 0.2% volatility
            new_price = max(0.01, current_price + price_change)
            
            # Update related fields
            quantity = df.loc[idx, "Quantity"]
            old_market_value = df.loc[idx, "MarketValue"]
            new_market_value = quantity * new_price
            
            df.loc[idx, "Price"] = round(new_price, 2)
            df.loc[idx, "MarketValue"] = round(new_market_value, 2)
            df.loc[idx, "PnL_Day"] += round(new_market_value - old_market_value, 2)
            
            # Update risk metrics with some correlation to price moves
            df.loc[idx, "VaR_95"] *= (1 + np.random.normal(0, 0.01))
            df.loc[idx, "Beta"] += np.random.normal(0, 0.005)
            df.loc[idx, "Volatility"] += np.random.normal(0, 0.001)
    
    def get_current_data(self) -> pd.DataFrame:
        """Get current data with thread safety"""
        with self.data_lock:
            return self.current_data.copy() if self.current_data is not None else None
    
    def set_current_data(self, df: pd.DataFrame):
        """Set current data with thread safety"""
        with self.data_lock:
            self.current_data = df.copy()

# Singleton instance
portfolio_generator = PortfolioDataGenerator()