# 🏛️ AMFI Mutual Fund Analyzer Pro

A comprehensi## ✨ Key Features

### 🔍 **Advanced Fund Analysis**
- **Real-time data** directly from AMFI (13,000+ mutual fund schemes)
- **Comprehensive metrics**: CAGR, volatility, Sharpe ratio, max drawdown, beta
- **Risk assessment** with detailed performance attribution
- **Historical performance** analysis with multiple time periods
- **Actual expense ratios** from curated database (not estimates)

### 📊 **Fund Comparison Tool**
- **Side-by-side comparison** of up to 5 funds
- **Risk vs Return** scatter plot analysis
- **Performance metrics** table with actual expense ratios
- **Winner/loser identification** across multiple criteria
- **Interactive charts** for visual comparison

### 🎯 **Smart Fund Screening**
- **Multi-criteria filtering** with CAGR, expense ratio, fund category
- **Plan type filtering** (Direct vs Regular)
- **AMC-based screening** with real performance data
- **NFO exclusion** and new fund filtering

### 💰 **Enhanced Investment Calculators**
- **SIP Calculator** with goal-based planning and inflation adjustment
- **Lumpsum Calculator** with target analysis and years-to-goal calculation
- **Combined planning** for existing investments + new SIP
- **Real returns** (post-inflation) calculation

### 💡 **Expense Analysis**
- **Actual vs estimated** expense ratio indicators
- **Impact analysis** on long-term returns
- **Cost comparison** across fund categories
- **Fee optimization** recommendationsgrade mutual fund analysis platform that uses real-time data directly from AMFI (Association of Mutual Funds in India) for accurate fund selection, comparison, and portfolio planning.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ramanathantrb/mutual-fund-analyser.git
   cd mutual-fund-analyser
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # Main application
   streamlit run app.py
   
   # Or use the Windows batch file
   start.bat
   ```

## ✨ Enhanced Features

### 🔍 **Advanced Fund Analysis**
- **🏛️ Real AMFI Data**: Fetches 13,000+ mutual fund schemes directly from AMFI
- **📊 Comprehensive Metrics**: CAGR, Sharpe Ratio, Sortino Ratio, VaR, CVaR
- **💰 Expense Analysis**: TER comparison, Direct vs Regular impact
- **📈 Technical Indicators**: Moving averages, RSI, MACD, Bollinger Bands

### 📊 **Multi-Fund Comparison**
- **Side-by-side comparison** of up to 6 funds
- **Risk vs Return** scatter plots  
- **Correlation analysis** and peer benchmarking
- **Performance attribution** and factor analysis

### 🎯 **Smart Fund Screening**
- **Advanced filtering** by category, AMC, expense ratio
- **Performance-based screening** with customizable criteria
- **ESG and thematic** fund identification
- **Automated recommendations** based on risk profile

### ⚖️ **Peer Group Analysis**
- **Category-wise benchmarking** against peer funds
- **Percentile rankings** and quartile analysis
- **Relative performance** tracking over time
- **Best-in-class** fund identification

### 💰 **Enhanced SIP Planning**
- **Goal-based planning** (retirement, education, house purchase)
- **Inflation-adjusted** calculations
- **Step-up SIP** optimization
- **Multiple scenario** analysis with Monte Carlo simulations

### � **Portfolio Management**
- **Multi-fund portfolio** tracking
- **Asset allocation** analysis and rebalancing alerts
- **Performance attribution** and risk decomposition
- **Tax optimization** and LTCG/STCG planning

## 📁 Project Structure

```
AMFI_Mutual_Fund_Analyzer/
├── src/                          # Source code
│   ├── analyzers/               # Analysis modules
│   │   ├── expense_analyzer.py  # Expense ratio analysis
│   │   ├── peer_comparison.py   # Peer group comparison
│   │   ├── fund_comparison.py   # Multi-fund comparison
│   │   ├── sip_calculator.py    # SIP planning tools
│   │   ├── advanced_analytics.py # Technical analysis
│   │   └── enhanced_risk_metrics.py # Risk metrics
│   ├── data/                    # Data modules
│   │   └── amfi_fund_fetcher.py # AMFI data fetching
│   └── ui/                      # User interface
│       └── main_app.py          # Streamlit UI components
├── docs/                        # Documentation
│   ├── ENHANCEMENT_GUIDE.md     # Feature enhancement guide
│   └── QUICK_WINS_GUIDE.md      # Quick wins documentation
├── scripts/                     # Utility scripts
│   ├── install_enhanced.bat     # Installation script
│   ├── run_enhanced.bat         # Run script
│   └── cli_analyzer.py          # Command-line interface
├── tests/                       # Unit tests
├── app.py                       # Main Streamlit application (stable)
├── app_main.py                  # Enhanced application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   # Run the automated installer (Windows)
   install_enhanced.bat
   
   # Or install manually
   pip install -r requirements.txt
   ```

### Usage

#### Option 1: Enhanced Web Application (Recommended)
```bash
# Windows - Run the launcher
run_enhanced.bat

# Or manually
streamlit run app.py
```
Then open your browser to `http://localhost:8501`

#### Option 2: Command Line Interface
```bash
python cli_analyzer.py
```

## 🎯 Application Features

### 1. 🔍 Fund Analyzer
- Individual fund analysis with comprehensive metrics
- Technical analysis with moving averages and indicators
- Advanced risk assessment and performance grading
- Interactive charts and visualizations

### 2. 📊 Fund Comparison
- Compare multiple funds side-by-side
- Risk-return analysis and correlation studies
- Performance benchmarking and relative analysis
- Export comparison reports

### 3. 💰 SIP Calculator
- Advanced SIP planning with step-up calculations
- Goal-based investment planning
- Multiple scenario analysis
- Inflation-adjusted target planning

### 4. 📈 Portfolio Tracker (Coming Soon)
- Multi-fund portfolio tracking
- Asset allocation analysis
- Rebalancing recommendations
- Performance attribution

### 5. 🎯 Goal Planner (Coming Soon)
- Comprehensive financial goal planning
- Tax-efficient investment strategies
- Risk-based asset allocation
- Monte Carlo simulations
- Real-time validation with AMFI database
- Fund information display (NAV, AMC, scheme code)

### 2. Analysis Periods
- 1 Year analysis
- 3 Years analysis  
- 5 Years analysis
- All available data

### 3. Interactive Dashboard
- **Key Metrics Cards**: Total Return, CAGR, Current NAV, Sharpe Ratio
- **Risk Analysis**: Volatility, Max Drawdown, Win Rate
- **Performance Charts**: 
  - NAV trend with hover details
  - Cumulative returns over time
  - Drawdown analysis
  - Daily returns distribution

### 4. Professional Insights
- Risk-adjusted return analysis
- Performance grading system
- Comprehensive summary statistics

## 🖥️ Command Line Interface

The CLI provides the same powerful analysis in a terminal-friendly format:

1. **Fund Selection**: 
   - Search by name/AMC
   - Browse by categories (Large Cap, Mid Cap, Small Cap, ELSS, Index, Debt, Hybrid)
   - Direct scheme code entry

2. **Analysis Output**:
   - Comprehensive metrics report
   - Performance grading (A+ to D)
   - Optional matplotlib charts

## 📊 Analysis Metrics

### Returns Analysis
- **Total Return**: Absolute percentage gain/loss
- **Annualized Return (CAGR)**: Compound Annual Growth Rate
- **Win Rate**: Percentage of positive return days

### Risk Analysis
- **Volatility**: Annualized standard deviation of returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure

### Performance Grading
Funds are graded on a scale from A+ (Excellent) to D (Poor) based on:
- Annualized returns (40% weight)
- Sharpe ratio (30% weight) 
- Maximum drawdown (20% weight)
- Win rate (10% weight)

## 📁 File Structure

```
AMFI_Mutual_Fund_Analyzer/
├── app.py                  # Streamlit web application
├── cli_analyzer.py         # Command-line interface
├── amfi_fund_fetcher.py   # AMFI data fetching utilities
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Technical Details

### Data Sources
- **AMFI**: Official mutual fund data from amfiindia.com
- **MFApi**: Historical NAV data from api.mfapi.in
- **Real-time**: Always uses current AMFI scheme database

### Key Libraries
- **Streamlit**: Web application framework
- **Plotly**: Interactive charting
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations
- **Requests**: API data fetching

### Error Handling
- SSL certificate validation bypass for API calls
- Robust error handling for network issues
- Data validation and cleaning
- User-friendly error messages

## 🎯 Example Use Cases

### For Individual Investors
- Compare multiple fund options
- Analyze risk vs return profile
- Track fund performance over time
- Make informed investment decisions

### For Financial Advisors
- Client portfolio analysis
- Fund recommendation reports
- Risk assessment presentations
- Performance benchmarking

### For Research & Analysis
- Mutual fund industry analysis
- Performance trend studies
- Risk metric calculations
- Data-driven insights

## 🚨 Important Notes

1. **Data Accuracy**: This tool uses official AMFI data for scheme validation
2. **Real-time**: NAV data is fetched in real-time from reliable sources
3. **Risk Disclaimer**: Past performance doesn't guarantee future results
4. **Internet Required**: Tool requires internet connection for data fetching

## 🆘 Troubleshooting

### Common Issues

1. **"Could not load AMFI fund database"**
   - Check internet connection
   - AMFI website might be temporarily unavailable
   - Try again after a few minutes

2. **"No NAV data available"**
   - Fund might be very new or discontinued
   - Try a different fund or check the scheme code

3. **Charts not displaying**
   - Ensure all dependencies are installed
   - Update your browser for web app
   - Check matplotlib backend for CLI

### Dependencies Issues
If you encounter package installation issues:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 🔄 Updates & Maintenance

This tool automatically:
- Fetches the latest AMFI fund database
- Uses real-time NAV data
- Validates fund scheme codes
- Handles API changes gracefully

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are correctly installed
3. Ensure stable internet connection
4. Review error messages for specific guidance

## 🎉 Success Examples

The tool has successfully analyzed funds showing:
- **258.88% total returns** over 6.81 years
- **20.63% CAGR** with detailed risk analysis
- **Real-time validation** of 13,000+ AMFI schemes
- **Professional-grade metrics** comparable to industry tools

---

**Happy Investing! 📈💰**

*Built with ❤️ for the Indian mutual fund investor community*
