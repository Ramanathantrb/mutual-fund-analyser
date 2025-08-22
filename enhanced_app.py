import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import StreamlitAMFIAnalyzer, main as analyzer_main
from fund_comparison import render_fund_comparison_page
from sip_calculator import render_sip_calculator_page

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
