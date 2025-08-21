import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
import urllib3
from amfi_fund_fetcher import AMFIFundFetcher

# Suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

class StreamlitAMFIAnalyzer:
    """Streamlit-based AMFI-integrated Mutual Fund Analyzer"""
    
    def __init__(self):
        self.amfi_fetcher = AMFIFundFetcher()
        self.base_url = "https://api.mfapi.in/mf"
        
        # Initialize AMFI data cache in session state
        if 'amfi_schemes' not in st.session_state:
            st.session_state.amfi_schemes = None
    
    def load_amfi_schemes(self):
        """Load AMFI schemes with caching"""
        if st.session_state.amfi_schemes is None:
            with st.spinner("🔄 Loading AMFI fund database... (This may take a moment)"):
                schemes = self.amfi_fetcher.fetch_all_schemes()
                st.session_state.amfi_schemes = schemes
        return st.session_state.amfi_schemes
    
    def get_fund_data(self, scheme_code, days=None):
        """Fetch NAV data using AMFI scheme code"""
        try:
            # Validate scheme code with AMFI
            is_valid, scheme_info = self.amfi_fetcher.validate_scheme_code(scheme_code)
            if not is_valid:
                return None, None, f"Invalid AMFI scheme code: {scheme_code}"
                
            fund_name = scheme_info['scheme_name']
            
            # Fetch from mfapi.in
            url = f"{self.base_url}/{scheme_code}"
            response = requests.get(url, verify=False, timeout=30)
            
            if response.status_code != 200:
                return None, None, f"HTTP Error: {response.status_code}"
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                return None, None, "No NAV data available"
            
            # Convert to DataFrame
            df = pd.DataFrame(data['data'])
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
            
            # Sort and clean
            df = df.sort_values('date').reset_index(drop=True)
            df = df.dropna(subset=['nav'])
            df = df[df['nav'] > 0]
            
            # Filter by days
            if days:
                cutoff_date = datetime.now() - timedelta(days=days)
                df = df[df['date'] >= cutoff_date]
            
            return df, fund_name, None
            
        except Exception as e:
            return None, None, f"Error: {str(e)}"
    
    def calculate_metrics(self, df):
        """Calculate comprehensive fund metrics"""
        if df is None or len(df) < 2:
            return {}
        
        df = df.copy()
        df['daily_return'] = df['nav'].pct_change()
        
        # Basic metrics
        current_nav = df['nav'].iloc[-1]
        initial_nav = df['nav'].iloc[0]
        total_return = ((current_nav - initial_nav) / initial_nav) * 100
        
        # Time period
        years = (df['date'].iloc[-1] - df['date'].iloc[0]).days / 365.25
        annualized_return = ((current_nav / initial_nav) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # Risk metrics
        daily_returns = df['daily_return'].dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100
        
        # Max drawdown
        cumulative = (1 + df['daily_return'].fillna(0)).cumprod()
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative - peak) / peak
        max_drawdown = abs(drawdown.min() * 100)
        
        # Sharpe ratio
        excess_returns = daily_returns.mean() * 252 - 0.06  # Assuming 6% risk-free rate
        sharpe_ratio = excess_returns / (daily_returns.std() * np.sqrt(252)) if daily_returns.std() != 0 else 0
        
        # Additional metrics
        positive_days = (daily_returns > 0).sum()
        win_rate = (positive_days / len(daily_returns)) * 100 if len(daily_returns) > 0 else 0
        
        return {
            'current_nav': current_nav,
            'initial_nav': initial_nav,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'years': years,
            'total_days': len(df)
        }
    
    def create_nav_chart(self, df, fund_name):
        """Create interactive NAV trend chart"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['nav'],
            mode='lines',
            name='NAV',
            line=dict(color='#2E86AB', width=2),
            hovertemplate='<b>Date:</b> %{x}<br><b>NAV:</b> ₹%{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'NAV Trend - {fund_name[:60]}{"..." if len(fund_name) > 60 else ""}',
            xaxis_title='Date',
            yaxis_title='NAV (₹)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_returns_chart(self, df):
        """Create cumulative returns chart"""
        df = df.copy()
        df['cumulative_return'] = ((df['nav'] / df['nav'].iloc[0]) - 1) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['cumulative_return'],
            mode='lines',
            name='Cumulative Returns',
            line=dict(color='#F18F01', width=2),
            fill='tonexty',
            hovertemplate='<b>Date:</b> %{x}<br><b>Return:</b> %{y:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='Cumulative Returns Over Time',
            xaxis_title='Date',
            yaxis_title='Cumulative Return (%)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_drawdown_chart(self, df):
        """Create drawdown chart"""
        df = df.copy()
        df['daily_return'] = df['nav'].pct_change()
        cumulative = (1 + df['daily_return'].fillna(0)).cumprod()
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = ((cumulative - peak) / peak) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=drawdown,
            mode='lines',
            name='Drawdown',
            line=dict(color='#C73E1D', width=2),
            fill='tozeroy',
            hovertemplate='<b>Date:</b> %{x}<br><b>Drawdown:</b> %{y:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='Drawdown Analysis',
            xaxis_title='Date',
            yaxis_title='Drawdown (%)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_returns_distribution(self, df):
        """Create returns distribution histogram"""
        daily_returns = (df['nav'].pct_change().dropna() * 100)
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=daily_returns,
            nbinsx=50,
            name='Daily Returns',
            marker_color='#A23B72',
            opacity=0.7
        ))
        
        fig.update_layout(
            title='Daily Returns Distribution',
            xaxis_title='Daily Return (%)',
            yaxis_title='Frequency',
            template='plotly_white',
            height=400
        )
        
        return fig

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AMFI Mutual Fund Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .fund-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<p class="main-header">🏛️ AMFI Mutual Fund Analyzer</p>', unsafe_allow_html=True)
    st.markdown("### 📊 Comprehensive Analysis Using Real AMFI Data")
    
    # Initialize analyzer
    analyzer = StreamlitAMFIAnalyzer()
    
    # Sidebar for fund selection
    st.sidebar.header("🔍 Fund Selection")
    
    # Load AMFI schemes
    schemes = analyzer.load_amfi_schemes()
    
    if not schemes:
        st.error("❌ Could not load AMFI fund database. Please try again later.")
        return
    
    # Create fund selection options
    st.sidebar.success(f"✅ Loaded {len(schemes):,} funds from AMFI")
    
    # Search functionality
    search_term = st.sidebar.text_input("🔍 Search funds by name:", placeholder="e.g., SBI, HDFC, Axis")
    
    # Filter schemes based on search
    if search_term:
        filtered_schemes = [
            scheme for scheme in schemes 
            if search_term.lower() in scheme['scheme_name'].lower() or 
               search_term.lower() in scheme['amc_name'].lower()
        ][:50]  # Limit to 50 results
    else:
        # Show popular categories
        filtered_schemes = []
    
    if search_term and filtered_schemes:
        # Create selectbox options
        scheme_options = {}
        for scheme in filtered_schemes:
            display_name = f"{scheme['scheme_name'][:60]}{'...' if len(scheme['scheme_name']) > 60 else ''} ({scheme['amc_name'][:20]})"
            scheme_options[display_name] = scheme
        
        selected_display = st.sidebar.selectbox(
            "Select Fund:",
            options=list(scheme_options.keys()),
            key="fund_selector"
        )
        
        if selected_display:
            selected_scheme = scheme_options[selected_display]
            scheme_code = selected_scheme['scheme_code']
            
            # Display fund info
            st.sidebar.markdown(f"""
            <div class="fund-info">
            <strong>🏛️ Fund:</strong> {selected_scheme['scheme_name'][:50]}...<br>
            <strong>🏢 AMC:</strong> {selected_scheme['amc_name']}<br>
            <strong>🔢 Code:</strong> {scheme_code}<br>
            <strong>💰 Current NAV:</strong> ₹{selected_scheme['nav']}
            </div>
            """, unsafe_allow_html=True)
            
            # Time period selection
            st.sidebar.header("📅 Analysis Period")
            period = st.sidebar.selectbox(
                "Select Period:",
                ["1 Year", "3 Years", "5 Years", "All Data"]
            )
            
            period_days = {
                "1 Year": 365,
                "3 Years": 1095,
                "5 Years": 1825,
                "All Data": None
            }
            
            days = period_days[period]
            
            # Analyze button
            if st.sidebar.button("📊 Analyze Fund", type="primary"):
                with st.spinner("🔄 Fetching and analyzing fund data..."):
                    df, fund_name, error = analyzer.get_fund_data(scheme_code, days)
                    
                    if error:
                        st.error(f"❌ {error}")
                        return
                    
                    if df is None or len(df) < 2:
                        st.error("❌ Insufficient data for analysis")
                        return
                    
                    # Calculate metrics
                    metrics = analyzer.calculate_metrics(df)
                    
                    # Display results
                    st.success(f"✅ Analysis complete for {fund_name}")
                    
                    # Key metrics cards
                    st.subheader("📊 Key Performance Metrics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Total Return",
                            f"{metrics['total_return']:.2f}%",
                            f"Over {metrics['years']:.1f} years"
                        )
                    
                    with col2:
                        st.metric(
                            "Annualized Return",
                            f"{metrics['annualized_return']:.2f}%",
                            "CAGR"
                        )
                    
                    with col3:
                        st.metric(
                            "Current NAV",
                            f"₹{metrics['current_nav']:.2f}",
                            f"From ₹{metrics['initial_nav']:.2f}"
                        )
                    
                    with col4:
                        st.metric(
                            "Sharpe Ratio",
                            f"{metrics['sharpe_ratio']:.2f}",
                            "Risk-adjusted return"
                        )
                    
                    # Additional metrics
                    st.subheader("🎯 Risk Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Volatility", f"{metrics['volatility']:.2f}%")
                    
                    with col2:
                        st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")
                    
                    with col3:
                        st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
                    
                    # Charts
                    st.subheader("📈 Performance Charts")
                    
                    # NAV trend
                    nav_chart = analyzer.create_nav_chart(df, fund_name)
                    st.plotly_chart(nav_chart, use_container_width=True)
                    
                    # Two column layout for additional charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        returns_chart = analyzer.create_returns_chart(df)
                        st.plotly_chart(returns_chart, use_container_width=True)
                        
                        drawdown_chart = analyzer.create_drawdown_chart(df)
                        st.plotly_chart(drawdown_chart, use_container_width=True)
                    
                    with col2:
                        distribution_chart = analyzer.create_returns_distribution(df)
                        st.plotly_chart(distribution_chart, use_container_width=True)
                        
                        # Summary table
                        st.subheader("📋 Summary Statistics")
                        summary_data = {
                            "Metric": ["Data Points", "Analysis Period", "Start Date", "End Date"],
                            "Value": [
                                f"{metrics['total_days']:,} days",
                                f"{metrics['years']:.2f} years",
                                df['date'].min().strftime('%Y-%m-%d'),
                                df['date'].max().strftime('%Y-%m-%d')
                            ]
                        }
                        st.table(pd.DataFrame(summary_data))
    
    elif search_term and not filtered_schemes:
        st.sidebar.warning("🔍 No funds found. Try different search terms.")
    
    else:
        # Show instructions when no search
        st.info("""
        ## 🚀 Welcome to AMFI Mutual Fund Analyzer!
        
        ### How to use:
        1. 🔍 **Search** for funds in the sidebar using fund name or AMC
        2. 📊 **Select** your preferred fund from the results
        3. 📅 **Choose** analysis period (1Y, 3Y, 5Y, or All Data)
        4. 🎯 **Click** "Analyze Fund" to get comprehensive insights
        
        ### Features:
        - ✅ Real-time data from AMFI (13,000+ funds)
        - 📈 Interactive charts and visualizations
        - 🎯 Risk analysis and performance metrics
        - 📊 Sharpe ratio, drawdown, volatility analysis
        - 🏆 Professional-grade fund evaluation
        
        ### Example searches:
        - "SBI Small Cap" - for SBI funds
        - "HDFC" - for all HDFC funds
        - "Index" - for index funds
        - "ELSS" - for tax-saving funds
        """)

if __name__ == "__main__":
    main()
