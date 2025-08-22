import pandas as pd
import numpy as np
import yfinance as yf
import ta
from datetime import datetime, timedelta

class TechnicalAnalysis:
    """Technical analysis indicators for mutual funds"""
    
    def __init__(self):
        pass
    
    def add_moving_averages(self, df, periods=[20, 50, 200]):
        """Add moving averages to the dataframe"""
        df = df.copy()
        
        for period in periods:
            df[f'MA_{period}'] = df['nav'].rolling(window=period).mean()
            
        return df
    
    def calculate_rsi(self, df, period=14):
        """Calculate Relative Strength Index"""
        df = df.copy()
        df['rsi'] = ta.momentum.RSIIndicator(df['nav'], window=period).rsi()
        return df
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """Calculate MACD indicators"""
        df = df.copy()
        
        macd_indicator = ta.trend.MACD(df['nav'], window_slow=slow, window_fast=fast, window_sign=signal)
        df['macd'] = macd_indicator.macd()
        df['macd_signal'] = macd_indicator.macd_signal()
        df['macd_histogram'] = macd_indicator.macd_diff()
        
        return df
    
    def calculate_bollinger_bands(self, df, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        df = df.copy()
        
        bb_indicator = ta.volatility.BollingerBands(df['nav'], window=period, window_dev=std_dev)
        df['bb_upper'] = bb_indicator.bollinger_hband()
        df['bb_middle'] = bb_indicator.bollinger_mavg()
        df['bb_lower'] = bb_indicator.bollinger_lband()
        
        return df
    
    def generate_signals(self, df):
        """Generate buy/sell signals based on technical indicators"""
        df = df.copy()
        
        # Simple moving average crossover
        df['ma_signal'] = np.where(df['MA_20'] > df['MA_50'], 1, -1)
        
        # RSI signals
        df['rsi_signal'] = np.where(df['rsi'] < 30, 1, np.where(df['rsi'] > 70, -1, 0))
        
        # MACD signals
        df['macd_signal_flag'] = np.where(df['macd'] > df['macd_signal'], 1, -1)
        
        return df

class MarketDataIntegration:
    """Integration with market indices and economic data"""
    
    def __init__(self):
        self.indices = {
            'NIFTY50': '^NSEI',
            'NIFTY500': '^CNXIT',
            'SENSEX': '^BSESN'
        }
    
    def get_market_data(self, symbol, start_date, end_date):
        """Fetch market index data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            data['returns'] = data['Close'].pct_change()
            return data
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None
    
    def calculate_beta_alpha(self, fund_returns, market_returns):
        """Calculate beta and alpha vs market"""
        # Align the data
        combined = pd.concat([fund_returns, market_returns], axis=1).dropna()
        
        if len(combined) < 30:
            return None, None
        
        # Calculate beta using covariance method
        covariance = np.cov(combined.iloc[:, 0], combined.iloc[:, 1])[0][1]
        market_variance = np.var(combined.iloc[:, 1])
        beta = covariance / market_variance
        
        # Calculate alpha (Jensen's alpha)
        fund_mean = combined.iloc[:, 0].mean() * 252
        market_mean = combined.iloc[:, 1].mean() * 252
        risk_free_rate = 0.06  # Assuming 6% risk-free rate
        
        alpha = fund_mean - (risk_free_rate + beta * (market_mean - risk_free_rate))
        
        return beta, alpha

class FundScreener:
    """Advanced fund screening and filtering"""
    
    def __init__(self, amfi_fetcher):
        self.amfi_fetcher = amfi_fetcher
    
    def screen_funds(self, criteria):
        """Screen funds based on multiple criteria"""
        all_funds = self.amfi_fetcher.fetch_all_schemes()
        
        screened_funds = []
        
        for fund in all_funds:
            if self.meets_criteria(fund, criteria):
                screened_funds.append(fund)
        
        return screened_funds
    
    def meets_criteria(self, fund, criteria):
        """Check if fund meets screening criteria"""
        fund_name_lower = fund['scheme_name'].lower()
        
        # Category filter
        if criteria.get('category') != 'All Categories':
            category_keywords = {
                'Equity': ['equity', 'growth', 'value', 'mid cap', 'small cap', 'large cap'],
                'Debt': ['debt', 'bond', 'income', 'gilt', 'liquid'],
                'Hybrid': ['hybrid', 'balanced', 'allocation'],
                'Index': ['index', 'nifty', 'sensex'],
                'ELSS': ['elss', 'tax', 'equity linked'],
                'International': ['international', 'global', 'foreign', 'overseas']
            }
            
            category = criteria.get('category', 'All Categories')
            if category in category_keywords:
                if not any(keyword in fund_name_lower for keyword in category_keywords[category]):
                    return False
        
        # Performance filter (placeholder - would need historical data)
        if criteria.get('performance') == 'Top Performers':
            # This would require additional performance data
            pass
        
        return True

class ReportGenerator:
    """Generate comprehensive fund analysis reports"""
    
    def __init__(self):
        pass
    
    def generate_fund_report(self, fund_data, metrics, technical_data=None):
        """Generate comprehensive fund analysis report"""
        
        report = {
            'executive_summary': self._generate_executive_summary(metrics),
            'performance_analysis': self._analyze_performance(fund_data, metrics),
            'risk_analysis': self._analyze_risk(metrics),
            'technical_analysis': self._analyze_technical(technical_data) if technical_data else None,
            'recommendation': self._generate_recommendation(metrics)
        }
        
        return report
    
    def _generate_executive_summary(self, metrics):
        """Generate executive summary"""
        summary = []
        
        # Performance summary
        if metrics.get('annualized_return', 0) > 15:
            summary.append("✅ Strong performance with above-average returns")
        elif metrics.get('annualized_return', 0) > 10:
            summary.append("✅ Good performance with market-beating returns")
        else:
            summary.append("⚠️ Below-average returns compared to equity markets")
        
        # Risk summary
        if metrics.get('max_drawdown', 0) < 20:
            summary.append("✅ Low downside risk with controlled drawdowns")
        elif metrics.get('max_drawdown', 0) < 35:
            summary.append("⚠️ Moderate risk with acceptable drawdowns")
        else:
            summary.append("❌ High risk with significant drawdowns")
        
        # Sharpe ratio summary
        if metrics.get('sharpe_ratio', 0) > 1:
            summary.append("✅ Excellent risk-adjusted returns")
        elif metrics.get('sharpe_ratio', 0) > 0.5:
            summary.append("✅ Good risk-adjusted returns")
        else:
            summary.append("⚠️ Poor risk-adjusted returns")
        
        return summary
    
    def _analyze_performance(self, fund_data, metrics):
        """Analyze performance characteristics"""
        analysis = {}
        
        # Return analysis
        analysis['return_consistency'] = self._calculate_return_consistency(fund_data)
        analysis['rolling_returns'] = self._calculate_rolling_returns(fund_data)
        
        return analysis
    
    def _analyze_risk(self, metrics):
        """Analyze risk characteristics"""
        risk_analysis = {}
        
        # Risk categorization
        volatility = metrics.get('volatility', 0)
        if volatility < 15:
            risk_analysis['risk_level'] = 'Low'
        elif volatility < 25:
            risk_analysis['risk_level'] = 'Moderate'
        else:
            risk_analysis['risk_level'] = 'High'
        
        return risk_analysis
    
    def _analyze_technical(self, technical_data):
        """Analyze technical indicators"""
        if not technical_data:
            return None
        
        analysis = {}
        
        # Trend analysis
        if 'MA_20' in technical_data.columns and 'MA_50' in technical_data.columns:
            current_ma20 = technical_data['MA_20'].iloc[-1]
            current_ma50 = technical_data['MA_50'].iloc[-1]
            current_nav = technical_data['nav'].iloc[-1]
            
            if current_nav > current_ma20 > current_ma50:
                analysis['trend'] = 'Strong Uptrend'
            elif current_nav > current_ma20:
                analysis['trend'] = 'Uptrend'
            elif current_nav < current_ma20 < current_ma50:
                analysis['trend'] = 'Downtrend'
            else:
                analysis['trend'] = 'Sideways'
        
        return analysis
    
    def _generate_recommendation(self, metrics):
        """Generate investment recommendation"""
        score = 0
        
        # Performance score
        if metrics.get('annualized_return', 0) > 15:
            score += 2
        elif metrics.get('annualized_return', 0) > 10:
            score += 1
        
        # Risk score
        if metrics.get('max_drawdown', 0) < 20:
            score += 2
        elif metrics.get('max_drawdown', 0) < 35:
            score += 1
        
        # Sharpe ratio score
        if metrics.get('sharpe_ratio', 0) > 1:
            score += 2
        elif metrics.get('sharpe_ratio', 0) > 0.5:
            score += 1
        
        # Generate recommendation
        if score >= 5:
            return {
                'rating': 'BUY',
                'confidence': 'High',
                'reason': 'Strong performance with good risk management'
            }
        elif score >= 3:
            return {
                'rating': 'HOLD',
                'confidence': 'Medium',
                'reason': 'Decent performance but monitor closely'
            }
        else:
            return {
                'rating': 'AVOID',
                'confidence': 'High',
                'reason': 'Poor risk-adjusted returns'
            }
    
    def _calculate_return_consistency(self, fund_data):
        """Calculate return consistency metrics"""
        if len(fund_data) < 12:
            return None
        
        monthly_returns = fund_data.set_index('date')['nav'].resample('M').last().pct_change().dropna()
        consistency = (monthly_returns > 0).sum() / len(monthly_returns) * 100
        
        return consistency
    
    def _calculate_rolling_returns(self, fund_data, periods=[252, 756, 1260]):  # 1Y, 3Y, 5Y
        """Calculate rolling returns"""
        rolling_returns = {}
        
        for period in periods:
            if len(fund_data) >= period:
                rolling_ret = fund_data['nav'].rolling(window=period).apply(
                    lambda x: ((x.iloc[-1] / x.iloc[0]) ** (252/period) - 1) * 100
                ).dropna()
                
                rolling_returns[f'{period//252}Y'] = {
                    'mean': rolling_ret.mean(),
                    'std': rolling_ret.std(),
                    'min': rolling_ret.min(),
                    'max': rolling_ret.max()
                }
        
        return rolling_returns
