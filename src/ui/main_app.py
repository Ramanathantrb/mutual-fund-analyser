"""
Main Streamlit Application for AMFI Mutual Fund Analyzer Pro
"""

import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(src_dir)

sys.path.extend([src_dir, root_dir])

# Import modules
from data.amfi_fund_fetcher import AMFIFundFetcher
from analyzers.expense_analyzer import ExpenseAnalyzer, FundScreener
from analyzers.peer_comparison import PeerComparison, BasicPortfolioTracker
from analyzers.fund_comparison import FundComparison
from analyzers.sip_calculator import SIPCalculator

# Import the core analyzer from legacy
sys.path.append(root_dir)
try:
    from app import StreamlitAMFIAnalyzer
except ImportError:
    st.error("Could not import core analyzer. Please check file structure.")

def main():
    """Enhanced main application with quick wins implemented"""
    
    # Page configuration
    st.set_page_config(
        page_title="AMFI Mutual Fund Analyzer Pro - Enhanced",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/Ramanathantrb/mutual-fund-analyser',
            'Report a bug': 'https://github.com/Ramanathantrb/mutual-fund-analyser/issues',
            'About': "# AMFI Mutual Fund Analyzer Pro\nComprehensive mutual fund analysis tool with expense analysis, peer comparison, and portfolio tracking."
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
    
    .feature-highlight {
        background: linear-gradient(90deg, #e8f4fd, #fff3e0);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .expense-grade-a {
        color: #28a745;
        font-weight: bold;
    }
    
    .expense-grade-b {
        color: #ffc107;
        font-weight: bold;
    }
    
    .expense-grade-c {
        color: #fd7e14;
        font-weight: bold;
    }
    
    .expense-grade-d {
        color: #dc3545;
        font-weight: bold;
    }
    
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with new features highlight
    st.markdown('<p class="main-header">🏛️ AMFI Mutual Fund Analyzer Pro</p>', unsafe_allow_html=True)
    
    # Show new features announcement
    st.markdown("""
    <div class="feature-highlight">
    🎉 <strong>Enhanced Features Available!</strong> 
    • Expense Ratio Analysis • Fund Screening & Filtering • Peer Comparison • Portfolio Tracking • Enhanced SIP Calculator
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["🔍 Fund Analyzer", "📊 Fund Comparison", "🎯 Fund Screener", "⚖️ Peer Analysis", "💰 SIP Calculator", "📁 Portfolio Tracker"],
        icons=["search", "bar-chart", "funnel", "people", "calculator", "briefcase"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#1f77b4", "font-size": "18px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "center",
                "margin": "0px",
                "padding": "10px",
                "--hover-color": "#eee"
            },
            "nav-link-selected": {"background-color": "#1f77b4"},
        }
    )
    
    # Show coming soon message for now
    st.info("🚧 The enhanced application is being reorganized. Please use the legacy app.py for now.")
    st.write("**Available features in development:**")
    st.write("• Enhanced Fund Analysis with Expense Ratio Analysis")
    st.write("• Fund Screening and Filtering")
    st.write("• Peer Group Comparison")
    st.write("• Basic Portfolio Tracking")
    st.write("• Enhanced SIP Calculator with Goal Planning")
    
    st.write("**To use the current working version, run:**")
    st.code("streamlit run app.py")

if __name__ == "__main__":
    main()
