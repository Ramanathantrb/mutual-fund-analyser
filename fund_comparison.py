import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

class FundComparison:
    """Compare multiple mutual funds side by side"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
    
    def compare_funds(self, fund_codes, period_days=None):
        """Compare multiple funds across various metrics"""
        comparison_data = {}
        fund_names = {}
        
        for code in fund_codes:
            df, name, error = self.analyzer.get_fund_data(code, period_days)
            if df is not None:
                metrics = self.analyzer.calculate_metrics(df)
                comparison_data[code] = {
                    'name': name,
                    'data': df,
                    'metrics': metrics
                }
                fund_names[code] = name
            else:
                st.warning(f"Could not fetch data for fund {code}: {error}")
        
        return comparison_data, fund_names
    
    def create_comparison_table(self, comparison_data):
        """Create a comparison table of key metrics"""
        if not comparison_data:
            return None
        
        metrics_data = []
        for code, data in comparison_data.items():
            metrics = data['metrics']
            metrics_data.append({
                'Fund Code': code,
                'Fund Name': data['name'][:40] + "..." if len(data['name']) > 40 else data['name'],
                'Total Return (%)': f"{metrics.get('total_return', 0):.2f}",
                'CAGR (%)': f"{metrics.get('annualized_return', 0):.2f}",
                'Volatility (%)': f"{metrics.get('volatility', 0):.2f}",
                'Max Drawdown (%)': f"{metrics.get('max_drawdown', 0):.2f}",
                'Sharpe Ratio': f"{metrics.get('sharpe_ratio', 0):.3f}",
                'Win Rate (%)': f"{metrics.get('win_rate', 0):.1f}"
            })
        
        return pd.DataFrame(metrics_data)
    
    def create_performance_comparison_chart(self, comparison_data):
        """Create normalized performance comparison chart"""
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for i, (code, data) in enumerate(comparison_data.items()):
            df = data['data'].copy()
            df['normalized_nav'] = (df['nav'] / df['nav'].iloc[0]) * 100
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['normalized_nav'],
                mode='lines',
                name=f"{data['name'][:30]}..." if len(data['name']) > 30 else data['name'],
                line=dict(color=colors[i % len(colors)], width=2),
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Normalized NAV: %{y:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Normalized Performance Comparison (Base = 100)',
            xaxis_title='Date',
            yaxis_title='Normalized NAV',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_risk_return_scatter(self, comparison_data):
        """Create risk-return scatter plot"""
        if not comparison_data:
            return None
        
        risk_data = []
        return_data = []
        names = []
        colors = []
        
        color_palette = px.colors.qualitative.Set3
        
        for i, (code, data) in enumerate(comparison_data.items()):
            metrics = data['metrics']
            risk_data.append(metrics.get('volatility', 0))
            return_data.append(metrics.get('annualized_return', 0))
            names.append(data['name'][:25] + "..." if len(data['name']) > 25 else data['name'])
            colors.append(color_palette[i % len(color_palette)])
        
        fig = go.Figure(data=go.Scatter(
            x=risk_data,
            y=return_data,
            mode='markers+text',
            text=names,
            textposition="top center",
            marker=dict(
                size=12,
                color=colors,
                line=dict(width=2, color='DarkSlateGrey')
            ),
            hovertemplate='<b>%{text}</b><br>Risk: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='Risk vs Return Comparison',
            xaxis_title='Volatility (%)',
            yaxis_title='Annualized Return (%)',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_correlation_heatmap(self, comparison_data):
        """Create correlation matrix heatmap"""
        if len(comparison_data) < 2:
            return None
        
        # Prepare returns data
        returns_df = pd.DataFrame()
        
        for code, data in comparison_data.items():
            df = data['data'].copy()
            df['daily_return'] = df['nav'].pct_change()
            df = df.set_index('date')
            returns_df[data['name'][:20]] = df['daily_return']
        
        # Calculate correlation matrix
        corr_matrix = returns_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Fund Correlation Matrix',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_drawdown_comparison(self, comparison_data):
        """Create drawdown comparison chart"""
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for i, (code, data) in enumerate(comparison_data.items()):
            df = data['data'].copy()
            df['daily_return'] = df['nav'].pct_change()
            cumulative = (1 + df['daily_return'].fillna(0)).cumprod()
            peak = cumulative.expanding(min_periods=1).max()
            drawdown = ((cumulative - peak) / peak) * 100
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=drawdown,
                mode='lines',
                name=f"{data['name'][:30]}..." if len(data['name']) > 30 else data['name'],
                line=dict(color=colors[i % len(colors)], width=2),
                fill='tonexty' if i == 0 else None,
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Drawdown: %{y:.2f}%<extra></extra>'
            ))
        
        fig.update_layout(
            title='Drawdown Comparison',
            xaxis_title='Date',
            yaxis_title='Drawdown (%)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig

def render_fund_comparison_page(analyzer):
    """Render the fund comparison page in Streamlit"""
    st.header("📊 Fund Comparison Tool")
    
    comparison_tool = FundComparison(analyzer)
    
    # Fund selection
    st.subheader("🔍 Select Funds to Compare")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fund_codes_input = st.text_area(
            "Enter Fund Codes (one per line)",
            placeholder="119551\n120503\n120834",
            height=150,
            help="Enter AMFI scheme codes, one per line. You can find codes using the main analyzer."
        )
    
    with col2:
        period_option = st.selectbox(
            "📅 Analysis Period",
            ["All Data", "5 Years", "3 Years", "1 Year"],
            index=1
        )
        
        period_mapping = {
            "All Data": None,
            "5 Years": 5 * 365,
            "3 Years": 3 * 365,
            "1 Year": 365
        }
        
        period_days = period_mapping[period_option]
    
    if st.button("🔍 Compare Funds", type="primary"):
        if fund_codes_input.strip():
            fund_codes = [code.strip() for code in fund_codes_input.strip().split('\n') if code.strip()]
            
            if len(fund_codes) < 2:
                st.error("⚠️ Please enter at least 2 fund codes for comparison")
            elif len(fund_codes) > 6:
                st.error("⚠️ Please limit comparison to maximum 6 funds")
            else:
                with st.spinner("🔄 Fetching and comparing fund data..."):
                    comparison_data, fund_names = comparison_tool.compare_funds(fund_codes, period_days)
                    
                    if len(comparison_data) < 2:
                        st.error("❌ Could not fetch data for sufficient number of funds")
                    else:
                        st.success(f"✅ Successfully compared {len(comparison_data)} funds")
                        
                        # Comparison table
                        st.subheader("📋 Key Metrics Comparison")
                        comparison_table = comparison_tool.create_comparison_table(comparison_data)
                        st.dataframe(comparison_table, use_container_width=True)
                        
                        # Performance chart
                        st.subheader("📈 Normalized Performance Comparison")
                        perf_chart = comparison_tool.create_performance_comparison_chart(comparison_data)
                        st.plotly_chart(perf_chart, use_container_width=True)
                        
                        # Risk-return scatter
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("🎯 Risk vs Return")
                            risk_return_chart = comparison_tool.create_risk_return_scatter(comparison_data)
                            st.plotly_chart(risk_return_chart, use_container_width=True)
                        
                        with col2:
                            st.subheader("🔗 Correlation Matrix")
                            corr_chart = comparison_tool.create_correlation_heatmap(comparison_data)
                            if corr_chart:
                                st.plotly_chart(corr_chart, use_container_width=True)
                        
                        # Drawdown comparison
                        st.subheader("📉 Drawdown Comparison")
                        drawdown_chart = comparison_tool.create_drawdown_comparison(comparison_data)
                        st.plotly_chart(drawdown_chart, use_container_width=True)
        else:
            st.error("⚠️ Please enter at least 2 fund codes")
