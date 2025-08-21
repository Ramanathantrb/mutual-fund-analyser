import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the original analyzer components
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
import urllib3
from amfi_fund_fetcher import AMFIFundFetcher

# Import enhanced modules
from fund_comparison import render_fund_comparison_page
from sip_calculator import render_sip_calculator_page

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
        """Create returns distribution chart"""
        df = df.copy()
        df['daily_return'] = df['nav'].pct_change().dropna() * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=df['daily_return'],
            nbinsx=50,
            name='Daily Returns',
            marker_color='#45B7D1',
            opacity=0.7,
            hovertemplate='Return Range: %{x:.2f}%<br>Frequency: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Daily Returns Distribution',
            xaxis_title='Daily Return (%)',
            yaxis_title='Frequency',
            template='plotly_white',
            height=400
        )
        
        return fig

def analyzer_main():
    """Main analyzer function with enhanced features"""
    analyzer = StreamlitAMFIAnalyzer()
    
    # Enhanced sidebar
    with st.sidebar:
        st.header("🔍 Fund Search")
        
        # Load schemes
        schemes = analyzer.load_amfi_schemes()
        
        if schemes:
            # Search functionality
            search_term = st.text_input(
                "🔍 Search Fund",
                placeholder="Enter fund name, AMC, or keyword...",
                help="Search for mutual funds by name or AMC"
            )
            
            # Filter schemes based on search
            if search_term:
                search_term_lower = search_term.lower()
                filtered_schemes = [
                    scheme for scheme in schemes 
                    if search_term_lower in scheme['scheme_name'].lower() or 
                       search_term_lower in scheme['amc_name'].lower()
                ]
            else:
                filtered_schemes = []
            
            # Show search results
            if filtered_schemes:
                st.subheader(f"📊 Found {len(filtered_schemes)} funds")
                
                # Limit display to first 20 results
                display_schemes = filtered_schemes[:20]
                
                # Create selection options
                fund_options = {}
                for scheme in display_schemes:
                    display_name = f"{scheme['scheme_name'][:50]}... | {scheme['amc_name']}"
                    if len(scheme['scheme_name']) <= 50:
                        display_name = f"{scheme['scheme_name']} | {scheme['amc_name']}"
                    fund_options[display_name] = scheme['scheme_code']
                
                selected_fund = st.selectbox(
                    "🎯 Select Fund",
                    options=list(fund_options.keys()),
                    help="Choose a fund for analysis"
                )
                
                if selected_fund:
                    scheme_code = fund_options[selected_fund]
                    fund_name = next(s['scheme_name'] for s in display_schemes if s['scheme_code'] == scheme_code)
                    
                    # Analysis period selection
                    period_option = st.selectbox(
                        "📅 Analysis Period",
                        ["All Data", "5 Years", "3 Years", "1 Year", "6 Months"],
                        index=1,
                        help="Select time period for analysis"
                    )
                    
                    period_mapping = {
                        "All Data": None,
                        "5 Years": 5 * 365,
                        "3 Years": 3 * 365,
                        "1 Year": 365,
                        "6 Months": 180
                    }
                    
                    period_days = period_mapping[period_option]
                    
                    # Analyze button
                    if st.button("🚀 Analyze Fund", type="primary"):
                        with st.spinner(f"🔄 Analyzing {fund_name}..."):
                            df, fund_name, error = analyzer.get_fund_data(scheme_code, period_days)
                            
                            if df is not None:
                                st.success("✅ Analysis completed!")
                                
                                # Calculate metrics
                                metrics = analyzer.calculate_metrics(df)
                                
                                # Main content area
                                st.header("📊 Fund Analysis Results")
                                
                                # Fund info
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(90deg, #f0f2f6, #e8eaf6);
                                    padding: 1.5rem;
                                    border-radius: 10px;
                                    border-left: 5px solid #1f77b4;
                                    margin-bottom: 2rem;
                                ">
                                    <h3 style="color: #1f77b4; margin: 0;">{fund_name}</h3>
                                    <p style="margin: 0.5rem 0 0 0; color: #666;">
                                        <strong>AMFI Code:</strong> {scheme_code} | 
                                        <strong>Analysis Period:</strong> {period_option}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Key metrics
                                st.subheader("🎯 Key Performance Metrics")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric(
                                        "💰 Current NAV", 
                                        f"₹{metrics['current_nav']:.2f}",
                                        delta=f"{metrics['total_return']:+.2f}%"
                                    )
                                
                                with col2:
                                    st.metric(
                                        "📈 CAGR", 
                                        f"{metrics['annualized_return']:.2f}%",
                                        delta="Annualized"
                                    )
                                
                                with col3:
                                    st.metric(
                                        "📊 Sharpe Ratio", 
                                        f"{metrics['sharpe_ratio']:.3f}",
                                        delta="Risk-adjusted"
                                    )
                                
                                with col4:
                                    st.metric(
                                        "⚡ Total Return", 
                                        f"{metrics['total_return']:.2f}%",
                                        delta=f"{metrics['years']:.1f} years"
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
                            else:
                                st.error(f"❌ Error: {error}")
                
                if len(filtered_schemes) > 20:
                    st.info(f"📝 Showing first 20 results. Found {len(filtered_schemes)} total matches.")
        
        elif search_term and not filtered_schemes:
            st.sidebar.warning("🔍 No funds found. Try different search terms.")
        
        else:
            # Show instructions when no search
            st.info("""
            ## 🚀 Welcome to AMFI Mutual Fund Analyzer Pro!
            
            ### How to use:
            1. 🔍 **Search** for funds using fund name or AMC
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

def main():
    """Enhanced main application with multiple pages"""
    
    # Page configuration
    st.set_page_config(
        page_title="AMFI Mutual Fund Analyzer Pro",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com',
            'Report a bug': 'https://github.com',
            'About': "# AMFI Mutual Fund Analyzer Pro\nComprehensive mutual fund analysis tool with real-time AMFI data."
        }
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
    
    .sub-header {
        font-size: 1.5rem;
        color: #2E86AB;
        margin-bottom: 1rem;
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<p class="main-header">🏛️ AMFI Mutual Fund Analyzer Pro</p>', unsafe_allow_html=True)
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["🔍 Fund Analyzer", "📊 Fund Comparison", "💰 SIP Calculator", "📈 Portfolio Tracker", "🎯 Goal Planner"],
        icons=["search", "bar-chart", "calculator", "briefcase", "target"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#1f77b4", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#eee"
            },
            "nav-link-selected": {"background-color": "#1f77b4"},
        }
    )
    
    # Initialize analyzer
    analyzer = StreamlitAMFIAnalyzer()
    
    # Route to different pages based on selection
    if selected == "🔍 Fund Analyzer":
        render_fund_analyzer_page(analyzer)
    
    elif selected == "📊 Fund Comparison":
        render_fund_comparison_page(analyzer)
    
    elif selected == "💰 SIP Calculator":
        render_sip_calculator_page()
    
    elif selected == "📈 Portfolio Tracker":
        render_portfolio_tracker_page(analyzer)
    
    elif selected == "🎯 Goal Planner":
        render_goal_planner_page()

def render_fund_analyzer_page(analyzer):
    """Render the main fund analyzer page"""
    st.header("🔍 Individual Fund Analysis")
    
    # Add enhanced sidebar with filters
    with st.sidebar:
        st.header("🔍 Fund Search & Filters")
        
        # Category filter
        category_filter = st.selectbox(
            "📂 Fund Category",
            ["All Categories", "Equity", "Debt", "Hybrid", "Index", "ELSS", "International"],
            help="Filter funds by category"
        )
        
        # AUM filter
        aum_filter = st.selectbox(
            "💰 AUM Range",
            ["All Sizes", "Large (>₹10,000 Cr)", "Medium (₹1,000-10,000 Cr)", "Small (<₹1,000 Cr)"],
            help="Filter by Assets Under Management"
        )
        
        # Performance filter
        perf_filter = st.selectbox(
            "📊 Performance Filter",
            ["All Funds", "Top Performers", "Consistent Performers", "Low Volatility"],
            help="Filter by performance characteristics"
        )
        
        st.divider()
        
        # Advanced options
        st.subheader("⚙️ Advanced Options")
        
        show_technical_analysis = st.checkbox("📈 Show Technical Analysis", help="Add moving averages and technical indicators")
        show_sector_analysis = st.checkbox("🏭 Show Sector Analysis", help="Analyze sector allocation (if data available)")
        compare_with_benchmark = st.checkbox("📊 Compare with Benchmark", help="Compare performance with market indices")
    
    # Call the original analyzer main function with enhancements
    analyzer_main()

def render_portfolio_tracker_page(analyzer):
    """Render portfolio tracking page"""
    st.header("📈 Portfolio Tracker")
    
    st.info("🚧 **Coming Soon!** Portfolio tracking functionality will allow you to:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 **Portfolio Analytics**
        - Track multiple fund investments
        - Portfolio-level risk metrics
        - Asset allocation analysis
        - Rebalancing recommendations
        - Performance attribution
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 **Portfolio Management**
        - Set investment targets
        - Monitor SIP contributions
        - Tax loss harvesting alerts
        - Dividend tracking
        - Goal progress monitoring
        """)
    
    # Placeholder for portfolio input
    st.subheader("💼 Add Your Holdings")
    
    with st.form("portfolio_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fund_code = st.text_input("Fund Code", placeholder="119551")
        
        with col2:
            units_held = st.number_input("Units Held", min_value=0.0, step=0.001)
        
        with col3:
            avg_purchase_price = st.number_input("Avg Purchase Price", min_value=0.0)
        
        submitted = st.form_submit_button("➕ Add to Portfolio")
        
        if submitted:
            st.success("✅ Fund added to portfolio! (Feature in development)")

def render_goal_planner_page():
    """Render goal planning page"""
    st.header("🎯 Comprehensive Goal Planner")
    
    st.info("🚧 **Enhanced Goal Planning** - Advanced goal-based investment planning")
    
    # Multiple goal management
    st.subheader("🎯 Your Financial Goals")
    
    # Sample goals display
    goals_data = [
        {"Goal": "Child Education", "Target": "₹25,00,000", "Years Left": "15", "Progress": "25%"},
        {"Goal": "Retirement", "Target": "₹1,00,00,000", "Years Left": "25", "Progress": "15%"},
        {"Goal": "House Purchase", "Target": "₹50,00,000", "Years Left": "8", "Progress": "40%"}
    ]
    
    import pandas as pd
    goals_df = pd.DataFrame(goals_data)
    st.dataframe(goals_df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🛠️ **Advanced Features**
        - Multiple goal tracking
        - Tax-efficient planning
        - Inflation-adjusted targets
        - Monte Carlo simulations
        - Risk-based asset allocation
        """)
    
    with col2:
        st.markdown("""
        ### 📊 **Smart Recommendations**
        - Optimal fund selection per goal
        - Automatic rebalancing alerts
        - Tax loss harvesting
        - Goal prioritization
        - Emergency fund planning
        """)
    
    # Call the SIP calculator for basic functionality
    render_sip_calculator_page()

if __name__ == "__main__":
    main()
