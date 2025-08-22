#!/usr/bin/env python3
"""
AMFI Mutual Fund Analyzer Pro - Enhanced Version (Fixed)
Complete application with all advanced features integrated and robust data loading
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import urllib3
import yfinance as yf
from src.data.amfi_fund_fetcher import AMFIFundFetcher
from datetime import datetime, timedelta
import math
import re
from typing import Dict, List, Tuple, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="AMFI Mutual Fund Analyzer Pro",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    color: #1f77b4;
    margin-bottom: 2rem;
    background: linear-gradient(90deg, #1f77b4, #ff7f0e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.feature-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 1rem;
    margin: 1rem 0;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-left: 4px solid #1f77b4;
    margin: 0.5rem 0;
}

.grade-a { color: #28a745; font-weight: bold; font-size: 1.2rem; }
.grade-b { color: #ffc107; font-weight: bold; font-size: 1.2rem; }
.grade-c { color: #fd7e14; font-weight: bold; font-size: 1.2rem; }
.grade-d { color: #dc3545; font-weight: bold; font-size: 1.2rem; }

.highlight-box {
    background: linear-gradient(90deg, #e8f4fd, #fff3e0);
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
    margin: 1rem 0;
}

.nav-card {
    background: white;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
    cursor: pointer;
    transition: all 0.3s;
}

.nav-card:hover {
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_amfi_data():
    """Load AMFI schemes data with robust error handling"""
    try:
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        schemes = []
        current_amc = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip header lines
            if line.startswith('Scheme Code;') or 'Open Ended Schemes' in line or 'Close Ended Schemes' in line:
                continue
                
            # Check if this is an AMC name line (no semicolons, has "Mutual Fund")
            if ';' not in line and 'Mutual Fund' in line:
                current_amc = line
                continue
                
            # Parse scheme data lines
            if ';' in line:
                parts = [part.strip() for part in line.split(';')]
                if len(parts) >= 6 and parts[0].isdigit():  # Valid scheme code
                    try:
                        # Validate NAV is a number
                        float(parts[4])
                        schemes.append({
                            'scheme_code': parts[0],
                            'scheme_name': parts[3],
                            'nav': parts[4],
                            'date': parts[5],
                            'scheme_type': parts[1] if len(parts) > 1 else '',
                            'amc_name': current_amc
                        })
                    except ValueError:
                        continue  # Skip if NAV is not a valid number
        
        return schemes
        
    except Exception as e:
        st.error(f"❌ Error loading AMFI data: {str(e)}")
        return []

def get_nav_data(scheme_code: str, days: int = 365) -> pd.DataFrame:
    """Get historical NAV data for a scheme with multiple data sources"""
    
    # Disable SSL warnings for problematic sites
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Method 1: Try MF API (Primary) - with SSL verification disabled
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url, timeout=15, verify=False, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                nav_data = []
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                for item in data['data'][:days]:
                    try:
                        date = datetime.strptime(item['date'], '%d-%m-%Y')
                        if start_date <= date <= end_date:
                            nav_data.append({
                                'date': date,
                                'nav': float(item['nav'])
                            })
                    except (ValueError, KeyError):
                        continue
                
                if len(nav_data) > 10:  # Ensure we have meaningful data
                    df = pd.DataFrame(nav_data)
                    st.success(f"✅ Loaded {len(nav_data)} days of real historical data from MF API")
                    return df.sort_values('date')
    except Exception as e:
        st.info(f"MF API failed: {str(e)}")
    
    # Method 2: Try AMFI Portal with improved parsing
    try:
        from_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
        to_date = datetime.now().strftime('%d-%b-%Y')
        
        # Try different AMFI endpoints
        amfi_urls = [
            "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx",
            "https://www.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"
        ]
        
        for amfi_url in amfi_urls:
            try:
                # Try both GET and POST methods
                methods = [
                    ('GET', {'frmdt': from_date, 'todt': to_date, 'tp': 1, 'sc': scheme_code}),
                    ('POST', {'frmdt': from_date, 'todt': to_date, 'sccode': scheme_code})
                ]
                
                for method, params in methods:
                    try:
                        session = requests.Session()
                        session.verify = False
                        
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'Connection': 'keep-alive',
                        }
                        
                        if method == 'GET':
                            response = session.get(amfi_url, params=params, headers=headers, timeout=20)
                        else:
                            headers['Content-Type'] = 'application/x-www-form-urlencoded'
                            response = session.post(amfi_url, data=params, headers=headers, timeout=20)
                        
                        if response.status_code == 200 and response.text.strip():
                            content = response.text.strip()
                            
                            # Skip if it's HTML (error page)
                            if content.startswith('<html') or content.startswith('<!DOCTYPE'):
                                continue
                            
                            lines = content.split('\n')
                            nav_data = []
                            
                            for line in lines:
                                line = line.strip()
                                if not line or line.startswith('Date') or line.startswith('NAV'):
                                    continue
                                    
                                # Try different separators
                                for sep in [';', ',', '\t']:
                                    parts = line.split(sep)
                                    if len(parts) >= 2:
                                        try:
                                            date_str = parts[0].strip()
                                            nav_str = parts[1].strip()
                                            
                                            # Try different date formats
                                            date = None
                                            for fmt in ['%d-%b-%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y']:
                                                try:
                                                    date = datetime.strptime(date_str, fmt)
                                                    break
                                                except ValueError:
                                                    continue
                                            
                                            if date and nav_str.replace('.', '').replace('-', '').isdigit():
                                                nav = float(nav_str)
                                                nav_data.append({
                                                    'date': date,
                                                    'nav': nav
                                                })
                                                break
                                        except (ValueError, IndexError):
                                            continue
                            
                            if len(nav_data) > 10:
                                df = pd.DataFrame(nav_data)
                                df = df.sort_values('date').reset_index(drop=True)
                                st.success(f"✅ Loaded {len(nav_data)} days of real AMFI historical data")
                                return df
                                
                    except Exception as inner_e:
                        continue
                        
            except Exception as url_e:
                continue
        
    except Exception as e:
        st.info(f"AMFI Portal failed: {str(e)}")
    
    # Method 3: Try YFinance for ETFs/Index funds
    try:
        # Some mutual funds have ticker symbols
        import yfinance as yf
        
        # Try common ticker patterns
        ticker_patterns = [
            f"{scheme_code}.BO",  # Bombay Stock Exchange
            f"{scheme_code}.NS",  # National Stock Exchange
            f"0P{scheme_code:08d}.BO"  # Zero-padded format
        ]
        
        for ticker in ticker_patterns:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f"{days}d")
                
                if not hist.empty and len(hist) > 10:
                    nav_data = []
                    for date, row in hist.iterrows():
                        nav_data.append({
                            'date': date.to_pydatetime(),
                            'nav': float(row['Close'])
                        })
                    
                    df = pd.DataFrame(nav_data)
                    st.success(f"✅ Loaded {len(nav_data)} days of real market data from Yahoo Finance")
                    return df.sort_values('date')
                    
            except Exception:
                continue
                
    except Exception as e:
        st.info(f"Yahoo Finance failed: {str(e)}")
    
    # Final fallback: Try to get at least current NAV from AMFI
    try:
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        response = requests.get(url, timeout=15, verify=False)
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            current_nav = None
            
            for line in lines:
                if ';' in line:
                    parts = line.split(';')
                    if len(parts) >= 6 and parts[0].strip() == str(scheme_code):
                        current_nav = float(parts[4].strip())
                        break
            
            if current_nav:
                st.error("⚠️ Only current NAV available - historical data required for analysis")
                return None
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
    
    # No fallback to demo data
    st.error("❌ Unable to fetch historical data from any source")
    st.error("� Please try a different fund or check your internet connection")
    return None

def calculate_returns(nav_data: pd.DataFrame) -> Dict:
    """Calculate comprehensive return metrics"""
    if nav_data.empty or len(nav_data) < 2:
        return {}
    
    nav_data = nav_data.sort_values('date')
    
    # Basic returns
    start_nav = nav_data.iloc[0]['nav']
    end_nav = nav_data.iloc[-1]['nav']
    total_return = (end_nav - start_nav) / start_nav * 100
    
    # Time period in years
    days_diff = (nav_data.iloc[-1]['date'] - nav_data.iloc[0]['date']).days
    years = max(days_diff / 365.25, 1/12)  # Minimum 1 month
    
    # CAGR
    cagr = (pow(end_nav / start_nav, 1/years) - 1) * 100
    
    # Daily returns for risk metrics
    nav_data['daily_return'] = nav_data['nav'].pct_change()
    daily_returns = nav_data['daily_return'].dropna()
    
    if len(daily_returns) > 1:
        # Volatility (annualized)
        volatility = daily_returns.std() * np.sqrt(252) * 100
        
        # Sharpe ratio (assuming 6% risk-free rate)
        risk_free_rate = 6
        sharpe_ratio = (cagr - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        nav_data['cumulative'] = (1 + nav_data['daily_return'].fillna(0)).cumprod()
        nav_data['peak'] = nav_data['cumulative'].expanding().max()
        nav_data['drawdown'] = (nav_data['cumulative'] - nav_data['peak']) / nav_data['peak'] * 100
        max_drawdown = nav_data['drawdown'].min()
        
        # Win rate
        win_rate = (daily_returns > 0).sum() / len(daily_returns) * 100
        
    else:
        volatility = sharpe_ratio = max_drawdown = win_rate = 0
    
    return {
        'total_return': total_return,
        'cagr': cagr,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'years': years
    }

def categorize_fund(fund_name: str) -> str:
    """Categorize fund based on name"""
    fund_name_lower = fund_name.lower()
    
    if any(term in fund_name_lower for term in ['large cap', 'large-cap', 'bluechip', 'blue chip']):
        return 'Large Cap'
    elif any(term in fund_name_lower for term in ['mid cap', 'mid-cap', 'midcap']):
        return 'Mid Cap'
    elif any(term in fund_name_lower for term in ['small cap', 'small-cap', 'smallcap']):
        return 'Small Cap'
    elif any(term in fund_name_lower for term in ['multi cap', 'multi-cap', 'multicap', 'flexi cap']):
        return 'Multi Cap'
    elif any(term in fund_name_lower for term in ['elss', 'tax', 'equity linked']):
        return 'ELSS'
    elif any(term in fund_name_lower for term in ['index', 'etf', 'nifty', 'sensex']):
        return 'Index'
    elif any(term in fund_name_lower for term in ['debt', 'bond', 'gilt', 'liquid', 'ultra short']):
        return 'Debt'
    elif any(term in fund_name_lower for term in ['hybrid', 'balanced']):
        return 'Hybrid'
    else:
        return 'Other'

def get_actual_expense_ratio(scheme_code: str, fund_name: str) -> float:
    """Fetch actual expense ratio from multiple sources"""
    
    # Try AMFI API for scheme details
    try:
        response = requests.get(
            f"https://www.amfiindia.com/modules/SchemeDetailsPopup.aspx?SchemeCode={scheme_code}",
            timeout=10,
            verify=False
        )
        if response.status_code == 200:
            content = response.text
            # Look for expense ratio patterns in the HTML
            import re
            expense_patterns = [
                r'expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                r'total\s*expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                r'ter[:\s]*(\d+\.?\d*)%?'
            ]
            
            for pattern in expense_patterns:
                matches = re.findall(pattern, content.lower())
                if matches:
                    try:
                        return float(matches[0])
                    except:
                        continue
    except:
        pass
    
    # Try alternative data sources
    try:
        # ValueResearch or other financial data APIs could be added here
        pass
    except:
        pass
    
    # Fallback to estimation with better accuracy
    return estimate_expense_ratio_improved(fund_name)

def estimate_expense_ratio_improved(fund_name: str) -> float:
    """Improved expense ratio estimation with more accurate data"""
    category = categorize_fund(fund_name)
    is_direct = "direct" in fund_name.lower()
    
    # Updated expense ranges based on 2024-25 data
    expense_ranges = {
        'Large Cap': {'regular': 1.8, 'direct': 1.05},
        'Mid Cap': {'regular': 2.2, 'direct': 1.45}, 
        'Small Cap': {'regular': 2.5, 'direct': 1.75},
        'Multi Cap': {'regular': 2.0, 'direct': 1.25},
        'ELSS': {'regular': 1.8, 'direct': 1.05},
        'Index': {'regular': 0.8, 'direct': 0.25},
        'Debt': {'regular': 1.2, 'direct': 0.45},
        'Hybrid': {'regular': 1.6, 'direct': 0.85},
        'Other': {'regular': 2.0, 'direct': 1.25}
    }
    
    plan_type = 'direct' if is_direct else 'regular'
    base_expense = expense_ranges.get(category, {'regular': 2.0, 'direct': 1.25})[plan_type]
    
    return base_expense

def estimate_expense_ratio(fund_name: str, is_direct: bool = True) -> float:
    """Legacy function - kept for compatibility"""
    return estimate_expense_ratio_improved(fund_name)

def calculate_expense_impact(amount: float, expense_ratio: float, years: int, return_rate: float = 12) -> Dict:
    """Calculate impact of expense ratio on returns"""
    # Returns without expense
    gross_return = return_rate / 100
    final_amount_gross = amount * (1 + gross_return) ** years
    
    # Returns with expense
    net_return = (return_rate - expense_ratio) / 100
    final_amount_net = amount * (1 + net_return) ** years
    
    # Impact
    cost_impact = final_amount_gross - final_amount_net
    cost_percentage = (cost_impact / final_amount_gross) * 100
    
    return {
        'gross_amount': final_amount_gross,
        'net_amount': final_amount_net,
        'cost_impact': cost_impact,
        'cost_percentage': cost_percentage
    }

def calculate_sip_with_goals(monthly_amount: float, years: int, target_amount: float = None, 
                           return_rate: float = 12, inflation_rate: float = 6) -> Dict:
    """Enhanced SIP calculator with goal planning"""
    monthly_rate = return_rate / 12 / 100
    months = years * 12
    
    # Future value of SIP
    if monthly_rate > 0:
        future_value = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    else:
        future_value = monthly_amount * months
    
    # Inflation adjusted value
    inflation_adjusted_value = future_value / ((1 + inflation_rate/100) ** years)
    
    # If target amount is specified, calculate required SIP
    required_sip = None
    if target_amount:
        if monthly_rate > 0:
            required_sip = target_amount / ((((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate))
        else:
            required_sip = target_amount / months
    
    return {
        'future_value': future_value,
        'inflation_adjusted_value': inflation_adjusted_value,
        'total_invested': monthly_amount * months,
        'gains': future_value - (monthly_amount * months),
        'required_sip': required_sip
    }

def grade_fund_performance(metrics: Dict) -> str:
    """Grade fund based on performance metrics"""
    if not metrics:
        return "N/A"
    
    score = 0
    
    # CAGR score (40% weight)
    cagr = metrics.get('cagr', 0)
    if cagr >= 15: score += 40
    elif cagr >= 12: score += 30
    elif cagr >= 8: score += 20
    elif cagr >= 5: score += 10
    
    # Sharpe ratio score (30% weight)
    sharpe = metrics.get('sharpe_ratio', 0)
    if sharpe >= 1.5: score += 30
    elif sharpe >= 1.0: score += 25
    elif sharpe >= 0.5: score += 15
    elif sharpe >= 0: score += 5
    
    # Max drawdown score (20% weight)
    drawdown = abs(metrics.get('max_drawdown', 0))
    if drawdown <= 10: score += 20
    elif drawdown <= 20: score += 15
    elif drawdown <= 30: score += 10
    elif drawdown <= 40: score += 5
    
    # Win rate score (10% weight)
    win_rate = metrics.get('win_rate', 0)
    if win_rate >= 60: score += 10
    elif win_rate >= 55: score += 8
    elif win_rate >= 50: score += 5
    
    # Grade assignment
    if score >= 80: return "A+"
    elif score >= 70: return "A"
    elif score >= 60: return "B+"
    elif score >= 50: return "B"
    elif score >= 40: return "C+"
    elif score >= 30: return "C"
    else: return "D"

def main():
    """Main application function"""
    
    # Header
    st.markdown('<p class="main-header">🏛️ AMFI Mutual Fund Analyzer Pro</p>', unsafe_allow_html=True)
    
    # Feature highlight
    st.markdown("""
    <div class="highlight-box">
    🎉 <strong>Enhanced Features:</strong> Real-time AMFI data • Expense Analysis • Performance Grading • 
    Advanced SIP Calculator • Fund Analysis • Risk Metrics • Interactive Charts
    </div>
    """, unsafe_allow_html=True)
    
    # Load AMFI data
    with st.spinner("🔄 Loading AMFI data..."):
        schemes_data = load_amfi_data()
    
    if not schemes_data:
        st.error("❌ Could not load AMFI data. Please check your internet connection and try again.")
        st.stop()
    
    st.success(f"✅ Loaded {len(schemes_data)} mutual fund schemes from AMFI")
    
    # Sidebar navigation
    st.sidebar.title("🔧 Navigation")
    
    # Navigation options with descriptions
    nav_options = {
        "🔍 Fund Analysis": "Complete performance analysis of individual funds",
        "💰 SIP Calculator": "Goal-based SIP planning with inflation adjustment", 
        "💡 Expense Analysis": "Analyze impact of expense ratios on returns",
        "🎯 Fund Screener": "Filter funds based on performance criteria",
        "📊 Comparison Tool": "Compare multiple funds side-by-side"
    }
    
    selected_nav = st.sidebar.radio("Choose Analysis Type:", list(nav_options.keys()))
    st.sidebar.info(nav_options[selected_nav])
    
    # Route to different analysis functions
    if selected_nav == "🔍 Fund Analysis":
        show_fund_analysis(schemes_data)
    elif selected_nav == "💰 SIP Calculator":
        show_sip_calculator()
    elif selected_nav == "💡 Expense Analysis":
        show_expense_analysis()
    elif selected_nav == "🎯 Fund Screener":
        show_fund_screener(schemes_data)
    elif selected_nav == "📊 Comparison Tool":
        show_fund_comparison()

def show_fund_analysis(schemes_data):
    """Show individual fund analysis"""
    st.header("🔍 Individual Fund Analysis")
    
    # Fund search
    search_term = st.text_input("🔍 Search for funds:", placeholder="Enter fund name, AMC, or category...")
    
    if search_term:
        # Filter schemes
        filtered_schemes = [
            scheme for scheme in schemes_data
            if search_term.lower() in scheme['scheme_name'].lower() or
               search_term.lower() in scheme['amc_name'].lower()
        ]
        
        if filtered_schemes:
            st.success(f"Found {len(filtered_schemes)} matching funds")
            
            # Fund selection
            fund_options = [f"{scheme['scheme_name']} ({scheme['amc_name']})" 
                          for scheme in filtered_schemes[:50]]  # Limit to 50 for performance
            
            selected_fund = st.selectbox("Select a fund:", fund_options)
            
            if selected_fund:
                # Find selected scheme
                selected_scheme = None
                for scheme in filtered_schemes:
                    if f"{scheme['scheme_name']} ({scheme['amc_name']})" == selected_fund:
                        selected_scheme = scheme
                        break
                
                if selected_scheme:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader(f"📈 {selected_scheme['scheme_name']}")
                        st.write(f"**AMC:** {selected_scheme['amc_name']}")
                        st.write(f"**Current NAV:** ₹{selected_scheme['nav']}")
                        st.write(f"**Date:** {selected_scheme['date']}")
                    
                    with col2:
                        # Analysis period
                        period_options = {
                            "1 Year": 365,
                            "3 Years": 1095,
                            "5 Years": 1825,
                            "All Data": 3650
                        }
                        period_label = st.selectbox("Analysis Period", list(period_options.keys()))
                        period_days = period_options[period_label]
                    
                    # Analyze button
                    if st.button("📊 Analyze Fund", type="primary"):
                        analyze_fund_performance(selected_scheme, period_days)
        else:
            st.warning("No funds found matching your search.")

def analyze_fund_performance(scheme, period_days):
    """Analyze and display fund performance"""
    with st.spinner("🔄 Analyzing fund performance..."):
        # Get NAV data
        nav_data = get_nav_data(scheme['scheme_code'], period_days)
        
        if nav_data is None or nav_data.empty:
            st.error("❌ Unable to fetch historical data for this fund.")
            st.info("💡 **Possible reasons:**")
            st.info("• Fund is newly launched with limited history")
            st.info("• Data source temporarily unavailable") 
            st.info("• Fund code may be incorrect")
            st.info("🔄 **Try:** A different fund or check back later")
            return
        
        # Calculate metrics
        metrics = calculate_returns(nav_data)
        
        if not metrics:
            st.error("❌ Could not calculate performance metrics.")
            return
        
        # Fund category and expense ratio
        fund_category = categorize_fund(scheme['scheme_name'])
        is_direct = 'direct' in scheme['scheme_name'].lower()
        
        # Try to get actual expense ratio
        with st.spinner("🔍 Fetching actual expense ratio..."):
            actual_expense = get_actual_expense_ratio(scheme['scheme_code'], scheme['scheme_name'])
        
        # Check if it's actual or estimated
        is_estimated = actual_expense == estimate_expense_ratio_improved(scheme['scheme_name'])
        
        # Performance grade
        grade = grade_fund_performance(metrics)
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("💹 CAGR", f"{metrics['cagr']:.2f}%")
            st.metric("📊 Total Return", f"{metrics['total_return']:.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📈 Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            st.metric("⚡ Volatility", f"{metrics['volatility']:.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📉 Max Drawdown", f"{metrics['max_drawdown']:.2f}%")
            st.metric("🎯 Win Rate", f"{metrics['win_rate']:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Grade display
        grade_class = f"grade-{grade.lower().replace('+', '')}"
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
        <h3>Overall Grade: <span class="{grade_class}">{grade}</span></h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Additional info
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📂 **Category:** {fund_category}")
            st.info(f"💰 **Plan Type:** {'Direct' if is_direct else 'Regular'}")
        with col2:
            if is_estimated:
                st.info(f"💸 **Est. Expense Ratio:** {actual_expense:.2f}%")
            else:
                st.success(f"💸 **Actual Expense Ratio:** {actual_expense:.2f}%")
            st.info(f"📅 **Analysis Period:** {metrics['years']:.1f} years")
        
        # NAV Chart
        st.subheader("📈 NAV Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=nav_data['date'],
            y=nav_data['nav'],
            mode='lines',
            name='NAV',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Date:</b> %{x}<br><b>NAV:</b> ₹%{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="NAV Performance Over Time",
            xaxis_title="Date",
            yaxis_title="NAV (₹)",
            hovermode='x',
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Expense impact analysis
        st.subheader("💸 Expense Impact Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            investment_amount = st.number_input("Investment Amount (₹)", value=100000, min_value=1000)
        with col2:
            investment_years = st.number_input("Investment Period (Years)", value=10, min_value=1)
        
        expense_impact = calculate_expense_impact(
            investment_amount, actual_expense, investment_years, metrics['cagr']
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Without Expenses", f"₹{expense_impact['gross_amount']:,.0f}")
        with col2:
            st.metric("💸 With Expenses", f"₹{expense_impact['net_amount']:,.0f}")
        with col3:
            st.metric("📉 Cost Impact", f"₹{expense_impact['cost_impact']:,.0f}")

def show_sip_calculator():
    """Show enhanced SIP calculator"""
    st.header("💰 Enhanced SIP Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Investment Parameters")
        monthly_sip = st.number_input("Monthly SIP Amount (₹)", value=5000, min_value=500)
        investment_years = st.number_input("Investment Period (Years)", value=15, min_value=1)
        expected_return = st.slider("Expected Annual Return (%)", 6.0, 20.0, 12.0, 0.5)
        inflation_rate = st.slider("Inflation Rate (%)", 3.0, 8.0, 6.0, 0.5)
    
    with col2:
        st.subheader("🎯 Goal Planning")
        has_goal = st.checkbox("I have a specific financial goal")
        target_amount = None
        if has_goal:
            target_amount = st.number_input("Target Amount (₹)", value=1000000, min_value=10000)
    
    if st.button("📈 Calculate SIP", type="primary"):
        sip_results = calculate_sip_with_goals(
            monthly_sip, investment_years, target_amount, expected_return, inflation_rate
        )
        
        st.subheader("📊 SIP Calculation Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Invested", f"₹{sip_results['total_invested']:,.0f}")
        with col2:
            st.metric("📈 Future Value", f"₹{sip_results['future_value']:,.0f}")
        with col3:
            st.metric("💵 Inflation Adjusted", f"₹{sip_results['inflation_adjusted_value']:,.0f}")
        with col4:
            st.metric("🎯 Total Gains", f"₹{sip_results['gains']:,.0f}")
        
        if target_amount and sip_results['required_sip']:
            st.success(f"🎯 To reach ₹{target_amount:,.0f}, you need SIP of ₹{sip_results['required_sip']:,.0f}/month")
        
        # Growth chart
        months = list(range(1, investment_years * 12 + 1))
        monthly_rate = expected_return / 12 / 100
        values = []
        invested = []
        
        for month in months:
            if monthly_rate > 0:
                fv = monthly_sip * (((1 + monthly_rate) ** month - 1) / monthly_rate) * (1 + monthly_rate)
            else:
                fv = monthly_sip * month
            values.append(fv)
            invested.append(monthly_sip * month)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=values, name="Investment Value", line=dict(color='green')))
        fig.add_trace(go.Scatter(x=months, y=invested, name="Amount Invested", line=dict(color='blue')))
        
        fig.update_layout(
            title="SIP Growth Projection",
            xaxis_title="Months",
            yaxis_title="Amount (₹)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

def show_expense_analysis():
    """Show expense ratio analysis"""
    st.header("💡 Expense Ratio Analysis")
    
    st.write("**Understanding the impact of expense ratios on your investments:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        investment_amount = st.number_input("Investment Amount (₹)", value=500000, min_value=10000)
        investment_period = st.number_input("Investment Period (Years)", value=20, min_value=1)
    
    with col2:
        expected_return = st.slider("Expected Return (%)", 8.0, 18.0, 12.0)
        expense_ratio = st.slider("Expense Ratio (%)", 0.1, 3.0, 1.5)
    
    if st.button("💸 Calculate Expense Impact", type="primary"):
        impact = calculate_expense_impact(investment_amount, expense_ratio, investment_period, expected_return)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💰 Without Expenses", f"₹{impact['gross_amount']:,.0f}")
        with col2:
            st.metric("💸 With Expenses", f"₹{impact['net_amount']:,.0f}")
        with col3:
            st.metric("📉 Total Cost", f"₹{impact['cost_impact']:,.0f}")
        
        st.error(f"💸 Expenses will cost you ₹{impact['cost_impact']:,.0f} over {investment_period} years!")
        
        # Comparison chart
        years = list(range(1, investment_period + 1))
        gross_values = []
        net_values = []
        
        for year in years:
            gross = investment_amount * (1 + expected_return/100) ** year
            net = investment_amount * (1 + (expected_return - expense_ratio)/100) ** year
            gross_values.append(gross)
            net_values.append(net)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=gross_values, name="Without Expenses", line=dict(color='green')))
        fig.add_trace(go.Scatter(x=years, y=net_values, name="With Expenses", line=dict(color='red')))
        
        fig.update_layout(
            title="Impact of Expense Ratio Over Time",
            xaxis_title="Years",
            yaxis_title="Investment Value (₹)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

def show_fund_screener(schemes_data):
    """Show fund screening feature"""
    st.header("🎯 Fund Screener")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Screening Criteria")
        min_cagr = st.slider("Minimum CAGR (%)", 0.0, 25.0, 10.0)
        fund_categories = st.multiselect("Fund Categories", 
                                       ['Large Cap', 'Mid Cap', 'Small Cap', 'Multi Cap', 'ELSS', 'Index', 'Debt', 'Hybrid'])
        amc_filter = st.text_input("AMC Name (optional)", placeholder="e.g., SBI, HDFC")
    
    with col2:
        st.subheader("💰 Investment Filters")
        plan_type = st.selectbox("Plan Type", ["All", "Direct", "Regular"])
        max_expense = st.slider("Max Expense Ratio (%)", 0.0, 3.0, 2.0)
        exclude_nfo = st.checkbox("Exclude NFO/New Funds", value=True)
    
    if st.button("🔍 Screen Funds", type="primary"):
        filtered_funds = []
        
        # Apply filters
        for scheme in schemes_data:
            fund_name = scheme['scheme_name'].lower()
            amc_name = scheme['amc_name'].lower()
            
            # Plan type filter
            if plan_type == "Direct" and "direct" not in fund_name:
                continue
            elif plan_type == "Regular" and "direct" in fund_name:
                continue
            
            # Category filter
            if fund_categories:
                fund_category = categorize_fund(scheme['scheme_name'])
                if fund_category not in fund_categories:
                    continue
            
            # AMC filter
            if amc_filter and amc_filter.lower() not in amc_name:
                continue
            
            # Expense ratio filter (use improved estimation for screening)
            fund_expense = estimate_expense_ratio_improved(scheme['scheme_name'])
            if fund_expense > max_expense:
                continue
            
            # Exclude NFO
            if exclude_nfo and ("nfo" in fund_name or "new fund" in fund_name):
                continue
            
            filtered_funds.append(scheme)
        
        if filtered_funds:
            st.success(f"✅ Found {len(filtered_funds)} funds matching your criteria")
            
            # Display top 20 results
            display_funds = filtered_funds[:20]
            
            results_data = []
            for fund in display_funds:
                is_direct = "direct" in fund['scheme_name'].lower()
                category = categorize_fund(fund['scheme_name'])
                expense = estimate_expense_ratio(fund['scheme_name'], is_direct)
                
                results_data.append({
                    'Fund Name': fund['scheme_name'][:50] + "..." if len(fund['scheme_name']) > 50 else fund['scheme_name'],
                    'AMC': fund['amc_name'],
                    'Category': category,
                    'NAV': f"₹{fund['nav']}",
                    'Plan': "Direct" if is_direct else "Regular",
                    'Est. Expense': f"{expense:.2f}%"
                })
            
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True)
            
            if len(filtered_funds) > 20:
                st.info(f"📊 Showing top 20 results. Total matching funds: {len(filtered_funds)}")
        else:
            st.warning("❌ No funds found matching your criteria. Try relaxing some filters.")

def show_fund_comparison():
    """Show fund comparison feature"""
    st.header("📊 Fund Comparison Tool")
    
    # Get list of available funds
    with st.spinner("🔄 Loading fund list..."):
        fund_fetcher = AMFIFundFetcher()
        all_schemes = fund_fetcher.fetch_all_schemes()
    
    if not all_schemes:
        st.error("❌ Could not load fund data. Please try again.")
        return
    
    # Create fund options for selection
    fund_options = [f"{scheme['scheme_name']} ({scheme['amc_name']})" for scheme in all_schemes[:1000]]  # Limit for performance
    
    st.subheader("🎯 Select Funds to Compare")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Fund 1**")
        fund1_selection = st.selectbox("Choose first fund", [""] + fund_options, key="fund1")
        
    with col2:
        st.markdown("**Fund 2**")
        fund2_selection = st.selectbox("Choose second fund", [""] + fund_options, key="fund2")
        
    with col3:
        st.markdown("**Fund 3 (Optional)**")
        fund3_selection = st.selectbox("Choose third fund", [""] + fund_options, key="fund3")
    
    # Analysis period
    period_options = {
        "1 Year": 365,
        "2 Years": 730,
        "3 Years": 1095,
        "5 Years": 1825
    }
    period_label = st.selectbox("� Comparison Period", list(period_options.keys()))
    period_days = period_options[period_label]
    
    # Compare funds
    if st.button("📊 Compare Funds", type="primary"):
        selected_funds = [fund1_selection, fund2_selection]
        if fund3_selection:
            selected_funds.append(fund3_selection)
        
        # Filter out empty selections
        selected_funds = [f for f in selected_funds if f]
        
        if len(selected_funds) < 2:
            st.warning("⚠️ Please select at least 2 funds to compare.")
            return
        
        # Find scheme details for selected funds
        schemes_to_compare = []
        for fund_name in selected_funds:
            for scheme in all_schemes:
                if f"{scheme['scheme_name']} ({scheme['amc_name']})" == fund_name:
                    schemes_to_compare.append(scheme)
                    break
        
        if len(schemes_to_compare) != len(selected_funds):
            st.error("❌ Could not find all selected funds. Please try again.")
            return
        
        compare_funds(schemes_to_compare, period_days)

def compare_funds(schemes: list, period_days: int):
    """Compare multiple funds"""
    st.subheader("📊 Fund Comparison Results")
    
    comparison_data = []
    nav_data_all = {}
    
    # Fetch data for all funds
    for i, scheme in enumerate(schemes):
        with st.spinner(f"📈 Analyzing {scheme['scheme_name']}..."):
            nav_data = get_nav_data(scheme['scheme_code'], period_days)
            
            if nav_data is None or nav_data.empty:
                st.error(f"❌ Could not fetch data for {scheme['scheme_name']}")
                continue
            
            metrics = calculate_returns(nav_data)
            if not metrics:
                continue
            
            # Get expense ratio
            actual_expense = get_actual_expense_ratio(scheme['scheme_code'], scheme['scheme_name'])
            is_estimated = actual_expense == estimate_expense_ratio_improved(scheme['scheme_name'])
            
            fund_info = {
                'Fund Name': scheme['scheme_name'][:50] + "..." if len(scheme['scheme_name']) > 50 else scheme['scheme_name'],
                'AMC': scheme['amc_name'],
                'Current NAV': f"₹{nav_data.iloc[-1]['nav']:.4f}",
                'CAGR (%)': f"{metrics['cagr']:.2f}",
                'Volatility (%)': f"{metrics['volatility']:.2f}",
                'Sharpe Ratio': f"{metrics['sharpe_ratio']:.2f}",
                'Max Drawdown (%)': f"{metrics['max_drawdown']:.2f}",
                'Expense Ratio (%)': f"{actual_expense:.2f}{'*' if is_estimated else ''}",
                'Category': categorize_fund(scheme['scheme_name'])
            }
            
            comparison_data.append(fund_info)
            nav_data_all[scheme['scheme_name']] = nav_data
    
    if not comparison_data:
        st.error("❌ Could not analyze any of the selected funds.")
        return
    
    # Display comparison table
    st.subheader("📋 Performance Comparison")
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)
    
    # Add note about estimated expense ratios
    st.caption("* Estimated expense ratio (actual data not available)")
    
    # Performance charts
    if len(nav_data_all) > 1:
        st.subheader("� NAV Performance Comparison")
        
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, (fund_name, nav_data) in enumerate(nav_data_all.items()):
            # Normalize to start from 100 for better comparison
            nav_normalized = (nav_data['nav'] / nav_data['nav'].iloc[0]) * 100
            
            fig.add_trace(go.Scatter(
                x=nav_data['date'],
                y=nav_normalized,
                mode='lines',
                name=fund_name[:30] + "..." if len(fund_name) > 30 else fund_name,
                line=dict(color=colors[i % len(colors)], width=2)
            ))
        
        fig.update_layout(
            title="Normalized NAV Performance (Base = 100)",
            xaxis_title="Date",
            yaxis_title="Normalized NAV",
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk-Return scatter plot
        st.subheader("🎯 Risk vs Return Analysis")
        
        risk_return_data = []
        for fund_info in comparison_data:
            risk_return_data.append({
                'Fund': fund_info['Fund Name'],
                'Return (CAGR %)': float(fund_info['CAGR (%)'].replace('%', '')),
                'Risk (Volatility %)': float(fund_info['Volatility (%)'].replace('%', ''))
            })
        
        df_scatter = pd.DataFrame(risk_return_data)
        
        fig_scatter = go.Figure()
        
        for i, row in df_scatter.iterrows():
            fig_scatter.add_trace(go.Scatter(
                x=[row['Risk (Volatility %)']],
                y=[row['Return (CAGR %)']],
                mode='markers+text',
                name=row['Fund'][:20] + "..." if len(row['Fund']) > 20 else row['Fund'],
                text=[row['Fund'][:15] + "..." if len(row['Fund']) > 15 else row['Fund']],
                textposition="top center",
                marker=dict(size=12, color=colors[i % len(colors)]),
                showlegend=False
            ))
        
        fig_scatter.update_layout(
            title="Risk vs Return Profile",
            xaxis_title="Risk (Volatility %)",
            yaxis_title="Return (CAGR %)",
            showlegend=False
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Best/Worst performers
        st.subheader("🏆 Performance Summary")
        
        col1, col2, col3 = st.columns(3)
        
        df_metrics = pd.DataFrame(comparison_data)
        
        with col1:
            best_return_idx = df_metrics['CAGR (%)'].str.replace('%', '').astype(float).idxmax()
            st.success(f"🚀 **Highest Return**\n{df_metrics.iloc[best_return_idx]['Fund Name']}\n{df_metrics.iloc[best_return_idx]['CAGR (%)']} CAGR")
        
        with col2:
            best_sharpe_idx = df_metrics['Sharpe Ratio'].astype(float).idxmax()
            st.info(f"⚖️ **Best Risk-Adjusted Return**\n{df_metrics.iloc[best_sharpe_idx]['Fund Name']}\nSharpe: {df_metrics.iloc[best_sharpe_idx]['Sharpe Ratio']}")
        
        with col3:
            lowest_expense_idx = df_metrics['Expense Ratio (%)'].str.replace('%', '').str.replace('*', '').astype(float).idxmin()
            st.success(f"💰 **Lowest Cost**\n{df_metrics.iloc[lowest_expense_idx]['Fund Name']}\n{df_metrics.iloc[lowest_expense_idx]['Expense Ratio (%)']} expense ratio")

if __name__ == "__main__":
    main()
