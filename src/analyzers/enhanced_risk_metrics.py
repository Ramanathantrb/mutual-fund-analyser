import numpy as np
import pandas as pd
from scipy import stats
import yfinance as yf

class EnhancedRiskMetrics:
    """Advanced risk and performance metrics for mutual funds"""
    
    def __init__(self, risk_free_rate=0.06):
        self.risk_free_rate = risk_free_rate
    
    def calculate_var(self, returns, confidence_level=0.95):
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def calculate_cvar(self, returns, confidence_level=0.95):
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()
    
    def calculate_sortino_ratio(self, returns):
        """Calculate Sortino Ratio (focuses on downside deviation)"""
        excess_returns = returns.mean() * 252 - self.risk_free_rate
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        return excess_returns / downside_std if downside_std != 0 else 0
    
    def calculate_calmar_ratio(self, returns, max_drawdown):
        """Calculate Calmar Ratio (Annual Return / Max Drawdown)"""
        annual_return = returns.mean() * 252
        return annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
    
    def calculate_beta_alpha(self, fund_returns, market_returns):
        """Calculate Beta and Alpha against market benchmark"""
        # Remove NaN values and align dates
        aligned_data = pd.concat([fund_returns, market_returns], axis=1).dropna()
        if len(aligned_data) < 30:  # Need sufficient data
            return None, None
        
        fund_ret = aligned_data.iloc[:, 0]
        market_ret = aligned_data.iloc[:, 1]
        
        # Calculate beta using regression
        beta, alpha, r_value, p_value, std_err = stats.linregress(market_ret, fund_ret)
        
        # Annualize alpha
        alpha_annual = alpha * 252
        
        return beta, alpha_annual
    
    def calculate_information_ratio(self, fund_returns, benchmark_returns):
        """Calculate Information Ratio"""
        excess_returns = fund_returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(252)
        excess_return_annual = excess_returns.mean() * 252
        
        return excess_return_annual / tracking_error if tracking_error != 0 else 0
    
    def calculate_capture_ratios(self, fund_returns, market_returns):
        """Calculate Upside and Downside Capture Ratios"""
        aligned_data = pd.concat([fund_returns, market_returns], axis=1).dropna()
        fund_ret = aligned_data.iloc[:, 0]
        market_ret = aligned_data.iloc[:, 1]
        
        # Upside capture
        up_market = market_ret > 0
        upside_capture = (fund_ret[up_market].mean() / market_ret[up_market].mean()) * 100
        
        # Downside capture  
        down_market = market_ret < 0
        downside_capture = (fund_ret[down_market].mean() / market_ret[down_market].mean()) * 100
        
        return upside_capture, downside_capture
    
    def rolling_metrics(self, returns, window_days=252):
        """Calculate rolling metrics over specified window"""
        rolling_returns = returns.rolling(window=window_days)
        
        rolling_sharpe = (rolling_returns.mean() * 252 - self.risk_free_rate) / (rolling_returns.std() * np.sqrt(252))
        rolling_volatility = rolling_returns.std() * np.sqrt(252) * 100
        
        return {
            'rolling_sharpe': rolling_sharpe,
            'rolling_volatility': rolling_volatility
        }
    
    def get_market_data(self, symbol="^NSEI", start_date=None, end_date=None):
        """Fetch market benchmark data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            hist['returns'] = hist['Close'].pct_change()
            return hist['returns'].dropna()
        except:
            return None
