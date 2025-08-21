import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import urllib3
from amfi_fund_fetcher import AMFIFundFetcher, display_amfi_fund_selector
from scipy import stats

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

class AMFIIntegratedAnalyzer:
    """Enhanced Mutual Fund Analyzer using AMFI data"""
    
    def __init__(self):
        self.amfi_fetcher = AMFIFundFetcher()
        self.base_url = "https://api.mfapi.in/mf"
        
    def get_fund_data(self, scheme_code, days=None):
        """Fetch NAV data using AMFI scheme code"""
        try:
            print(f"🔄 Fetching data for AMFI scheme: {scheme_code}")
            
            # First validate the scheme code with AMFI
            is_valid, scheme_info = self.amfi_fetcher.validate_scheme_code(scheme_code)
            if not is_valid:
                print(f"❌ Invalid AMFI scheme code: {scheme_code}")
                return None, None
                
            fund_name = scheme_info['scheme_name']
            print(f"✅ Validated: {fund_name}")
            
            # Try to fetch from mfapi.in using the scheme code
            url = f"{self.base_url}/{scheme_code}"
            response = requests.get(url, verify=False, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Error: HTTP {response.status_code}")
                return None, None
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                print("❌ No NAV data available")
                return None, None
            
            # Convert to DataFrame
            df = pd.DataFrame(data['data'])
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            # Filter by days if specified
            if days:
                cutoff_date = datetime.now() - timedelta(days=days)
                df = df[df['date'] >= cutoff_date]
            
            # Remove any rows with invalid NAV
            df = df.dropna(subset=['nav'])
            df = df[df['nav'] > 0]
            
            print(f"✅ Fetched {len(df)} NAV records")
            print(f"📅 Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
            
            return df, fund_name
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None, None
    
    def calculate_returns(self, df):
        """Calculate various return metrics"""
        if df is None or len(df) < 2:
            return {}
        
        df = df.copy()
        df['daily_return'] = df['nav'].pct_change()
        
        # Basic metrics
        current_nav = df['nav'].iloc[-1]
        initial_nav = df['nav'].iloc[0]
        total_return = ((current_nav - initial_nav) / initial_nav) * 100
        
        # Annualized return
        years = (df['date'].iloc[-1] - df['date'].iloc[0]).days / 365.25
        annualized_return = ((current_nav / initial_nav) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # Volatility
        daily_returns = df['daily_return'].dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized
        
        # Risk metrics
        max_drawdown = self.calculate_max_drawdown(df)
        sharpe_ratio = self.calculate_sharpe_ratio(daily_returns)
        
        # Additional metrics
        positive_days = (daily_returns > 0).sum()
        total_days = len(daily_returns)
        win_rate = (positive_days / total_days) * 100 if total_days > 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'current_nav': current_nav,
            'initial_nav': initial_nav,
            'years': years,
            'total_days': total_days
        }
    
    def calculate_max_drawdown(self, df):
        """Calculate maximum drawdown"""
        if df is None or len(df) < 2:
            return 0
        
        cumulative = (1 + df['nav'].pct_change().fillna(0)).cumprod()
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative - peak) / peak
        return abs(drawdown.min() * 100)
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.06):
        """Calculate Sharpe ratio"""
        if len(returns) == 0 or returns.std() == 0:
            return 0
        
        excess_returns = returns.mean() * 252 - risk_free_rate
        return excess_returns / (returns.std() * np.sqrt(252))
    
    def plot_nav_trend(self, df, fund_name):
        """Plot NAV trend over time"""
        plt.figure(figsize=(14, 8))
        
        plt.subplot(2, 2, 1)
        plt.plot(df['date'], df['nav'], linewidth=2, color='#2E86AB')
        plt.title(f'NAV Trend - {fund_name[:50]}...', fontsize=12, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('NAV (₹)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Returns distribution
        plt.subplot(2, 2, 2)
        daily_returns = df['nav'].pct_change().dropna() * 100
        plt.hist(daily_returns, bins=50, alpha=0.7, color='#A23B72', edgecolor='black')
        plt.title('Daily Returns Distribution', fontsize=12, fontweight='bold')
        plt.xlabel('Daily Return (%)')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        
        # Cumulative returns
        plt.subplot(2, 2, 3)
        cumulative_returns = ((df['nav'] / df['nav'].iloc[0]) - 1) * 100
        plt.plot(df['date'], cumulative_returns, linewidth=2, color='#F18F01')
        plt.title('Cumulative Returns', fontsize=12, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return (%)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Rolling volatility
        plt.subplot(2, 2, 4)
        rolling_vol = df['nav'].pct_change().rolling(window=30).std() * np.sqrt(252) * 100
        plt.plot(df['date'], rolling_vol, linewidth=2, color='#C73E1D')
        plt.title('Rolling 30-Day Volatility', fontsize=12, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Volatility (%)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def print_summary(self, metrics, fund_name):
        """Print comprehensive analysis summary"""
        print("\n" + "="*80)
        print(f"📊 COMPREHENSIVE ANALYSIS REPORT")
        print("="*80)
        print(f"🏛️  Fund: {fund_name}")
        print(f"📅 Analysis Period: {metrics['years']:.2f} years ({metrics['total_days']} trading days)")
        print("-"*80)
        
        print(f"💰 Current NAV: ₹{metrics['current_nav']:.2f}")
        print(f"🏁 Initial NAV: ₹{metrics['initial_nav']:.2f}")
        print(f"📈 Total Return: {metrics['total_return']:.2f}%")
        print(f"📊 Annualized Return: {metrics['annualized_return']:.2f}%")
        print(f"⚡ Volatility: {metrics['volatility']:.2f}%")
        print(f"📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"⭐ Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"🎯 Win Rate: {metrics['win_rate']:.1f}%")
        
        # Performance grade
        grade = self.get_performance_grade(metrics)
        print(f"🏆 Performance Grade: {grade}")
        print("="*80)
    
    def get_performance_grade(self, metrics):
        """Assign performance grade based on metrics"""
        score = 0
        
        # Annualized return score (0-40 points)
        if metrics['annualized_return'] >= 15:
            score += 40
        elif metrics['annualized_return'] >= 12:
            score += 30
        elif metrics['annualized_return'] >= 10:
            score += 20
        elif metrics['annualized_return'] >= 8:
            score += 10
        
        # Sharpe ratio score (0-30 points)
        if metrics['sharpe_ratio'] >= 1.5:
            score += 30
        elif metrics['sharpe_ratio'] >= 1.0:
            score += 20
        elif metrics['sharpe_ratio'] >= 0.5:
            score += 10
        
        # Max drawdown score (0-20 points)
        if metrics['max_drawdown'] <= 15:
            score += 20
        elif metrics['max_drawdown'] <= 25:
            score += 15
        elif metrics['max_drawdown'] <= 35:
            score += 10
        elif metrics['max_drawdown'] <= 50:
            score += 5
        
        # Win rate score (0-10 points)
        if metrics['win_rate'] >= 55:
            score += 10
        elif metrics['win_rate'] >= 50:
            score += 5
        
        # Assign grade
        if score >= 85:
            return "A+ (Excellent)"
        elif score >= 75:
            return "A (Very Good)"
        elif score >= 65:
            return "B+ (Good)"
        elif score >= 55:
            return "B (Above Average)"
        elif score >= 45:
            return "C+ (Average)"
        elif score >= 35:
            return "C (Below Average)"
        else:
            return "D (Poor)"

def main():
    """Main function to run AMFI-integrated analysis"""
    print("🚀 Welcome to AMFI-Integrated Mutual Fund Analyzer!")
    print("📊 Now using real AMFI scheme codes for accurate analysis")
    
    # Get fund selection from AMFI
    scheme_code, fund_name = display_amfi_fund_selector()
    
    if not scheme_code:
        print("👋 No fund selected. Exiting...")
        return
    
    # Initialize analyzer
    analyzer = AMFIIntegratedAnalyzer()
    
    # Get time period
    print("\n📅 Select analysis period:")
    print("1. 📊 1 Year")
    print("2. 📊 3 Years") 
    print("3. 📊 5 Years")
    print("4. 📊 All available data")
    
    period_choice = input("Enter choice (1-4): ").strip()
    
    days_map = {'1': 365, '2': 1095, '3': 1825, '4': None}
    days = days_map.get(period_choice, None)
    
    # Fetch and analyze data
    df, validated_fund_name = analyzer.get_fund_data(scheme_code, days)
    
    if df is None:
        print("❌ Could not fetch fund data. Please try another fund.")
        return
    
    # Calculate metrics
    metrics = analyzer.calculate_returns(df)
    
    # Display results
    analyzer.print_summary(metrics, validated_fund_name)
    
    # Ask for visualization
    show_charts = input("\n📊 Show detailed charts? (Y/N): ").strip().lower()
    if show_charts in ['y', 'yes']:
        analyzer.plot_nav_trend(df, validated_fund_name)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
