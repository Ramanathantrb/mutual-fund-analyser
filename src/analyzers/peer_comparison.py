import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta

class PeerComparison:
    """Compare funds against their peer group"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        
        # Define peer categories and their keywords
        self.peer_categories = {
            'Large Cap Equity': ['large cap', 'blue chip', 'bluechip'],
            'Mid Cap Equity': ['mid cap', 'midcap'],
            'Small Cap Equity': ['small cap', 'smallcap'],
            'Multi Cap Equity': ['multi cap', 'multicap', 'flexi cap'],
            'ELSS': ['elss', 'tax saver', 'equity linked'],
            'Index Funds': ['index', 'nifty', 'sensex'],
            'Debt Funds': ['debt', 'bond', 'gilt', 'liquid', 'ultra short'],
            'Hybrid Funds': ['hybrid', 'balanced', 'conservative', 'aggressive'],
            'Sector Funds': ['banking', 'it', 'pharma', 'fmcg', 'auto', 'infra'],
            'International': ['international', 'global', 'us', 'overseas']
        }
    
    def categorize_fund(self, fund_name):
        """Categorize fund based on its name"""
        fund_name_lower = fund_name.lower()
        
        for category, keywords in self.peer_categories.items():
            if any(keyword in fund_name_lower for keyword in keywords):
                return category
        
        return 'Other'
    
    def get_peer_funds(self, schemes_df, target_fund_name, limit=20):
        """Get peer funds for comparison"""
        target_category = self.categorize_fund(target_fund_name)
        
        if target_category == 'Other':
            return []
        
        # Find funds in same category
        peer_funds = []
        keywords = self.peer_categories[target_category]
        
        for _, scheme in schemes_df.iterrows():
            scheme_name = scheme['scheme_name'].lower()
            if any(keyword in scheme_name for keyword in keywords):
                # Prefer direct plans
                if 'direct' in scheme_name:
                    peer_funds.append({
                        'scheme_code': scheme['scheme_code'],
                        'scheme_name': scheme['scheme_name'],
                        'amc_name': scheme['amc_name']
                    })
        
        # Remove duplicates and limit results
        seen_names = set()
        unique_peers = []
        for fund in peer_funds:
            # Create a simplified name for deduplication
            simple_name = fund['scheme_name'].replace('Direct Plan', '').replace('Regular Plan', '').strip()
            if simple_name not in seen_names:
                seen_names.add(simple_name)
                unique_peers.append(fund)
                if len(unique_peers) >= limit:
                    break
        
        return unique_peers
    
    def analyze_peer_performance(self, target_fund_code, peer_funds, period_days=365):
        """Analyze target fund against peers"""
        results = {}
        
        # Get target fund data
        target_data, target_name, error = self.analyzer.get_fund_data(target_fund_code, period_days)
        if target_data is None:
            return None, f"Could not fetch target fund data: {error}"
        
        target_metrics = self.analyzer.calculate_metrics(target_data)
        results['target'] = {
            'name': target_name,
            'metrics': target_metrics,
            'data': target_data
        }
        
        # Get peer fund data
        peer_results = []
        successful_peers = 0
        
        for peer in peer_funds[:10]:  # Limit to top 10 for performance
            try:
                peer_data, peer_name, error = self.analyzer.get_fund_data(peer['scheme_code'], period_days)
                if peer_data is not None and len(peer_data) > 30:  # Ensure sufficient data
                    peer_metrics = self.analyzer.calculate_metrics(peer_data)
                    peer_results.append({
                        'code': peer['scheme_code'],
                        'name': peer_name,
                        'amc': peer['amc_name'],
                        'metrics': peer_metrics,
                        'data': peer_data
                    })
                    successful_peers += 1
                    if successful_peers >= 8:  # Limit to 8 successful peers
                        break
            except Exception as e:
                continue
        
        results['peers'] = peer_results
        
        if len(peer_results) == 0:
            return None, "No peer fund data available for comparison"
        
        # Calculate peer statistics
        peer_stats = self.calculate_peer_statistics(peer_results)
        results['peer_stats'] = peer_stats
        
        # Calculate rankings
        rankings = self.calculate_rankings(target_metrics, peer_results)
        results['rankings'] = rankings
        
        return results, None
    
    def calculate_peer_statistics(self, peer_results):
        """Calculate peer group statistics"""
        if not peer_results:
            return {}
        
        metrics_data = []
        for peer in peer_results:
            metrics_data.append(peer['metrics'])
        
        stats = {}
        key_metrics = ['total_return', 'annualized_return', 'volatility', 'max_drawdown', 'sharpe_ratio']
        
        for metric in key_metrics:
            values = [m.get(metric, 0) for m in metrics_data if m.get(metric) is not None]
            if values:
                stats[metric] = {
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'std': np.std(values),
                    'percentile_25': np.percentile(values, 25),
                    'percentile_75': np.percentile(values, 75)
                }
        
        return stats
    
    def calculate_rankings(self, target_metrics, peer_results):
        """Calculate target fund's ranking among peers"""
        rankings = {}
        
        # Metrics where higher is better
        higher_better = ['total_return', 'annualized_return', 'sharpe_ratio', 'win_rate']
        # Metrics where lower is better
        lower_better = ['volatility', 'max_drawdown']
        
        for metric in higher_better + lower_better:
            target_value = target_metrics.get(metric, 0)
            peer_values = [p['metrics'].get(metric, 0) for p in peer_results 
                          if p['metrics'].get(metric) is not None]
            
            if peer_values:
                total_funds = len(peer_values) + 1  # Include target fund
                
                if metric in higher_better:
                    # Count how many peers have lower values
                    better_count = sum(1 for v in peer_values if v < target_value)
                    rank = better_count + 1
                else:
                    # Count how many peers have higher values
                    better_count = sum(1 for v in peer_values if v > target_value)
                    rank = better_count + 1
                
                percentile = ((total_funds - rank) / (total_funds - 1)) * 100 if total_funds > 1 else 50
                
                rankings[metric] = {
                    'rank': rank,
                    'total': total_funds,
                    'percentile': percentile
                }
        
        return rankings
    
    def create_peer_comparison_chart(self, results):
        """Create visual comparison with peers"""
        if not results or 'peers' not in results:
            return None
        
        target = results['target']
        peers = results['peers']
        
        # Prepare data for scatter plot (Risk vs Return)
        peer_returns = [p['metrics'].get('annualized_return', 0) for p in peers]
        peer_volatility = [p['metrics'].get('volatility', 0) for p in peers]
        peer_names = [p['name'][:30] + "..." if len(p['name']) > 30 else p['name'] for p in peers]
        
        target_return = target['metrics'].get('annualized_return', 0)
        target_volatility = target['metrics'].get('volatility', 0)
        
        fig = go.Figure()
        
        # Add peer funds
        fig.add_trace(go.Scatter(
            x=peer_volatility,
            y=peer_returns,
            mode='markers',
            name='Peer Funds',
            marker=dict(size=8, color='lightblue', opacity=0.7),
            text=peer_names,
            hovertemplate='<b>%{text}</b><br>Return: %{y:.2f}%<br>Volatility: %{x:.2f}%<extra></extra>'
        ))
        
        # Add target fund
        fig.add_trace(go.Scatter(
            x=[target_volatility],
            y=[target_return],
            mode='markers',
            name='Target Fund',
            marker=dict(size=15, color='red', symbol='star'),
            text=[target['name'][:30] + "..." if len(target['name']) > 30 else target['name']],
            hovertemplate='<b>%{text}</b><br>Return: %{y:.2f}%<br>Volatility: %{x:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='Risk vs Return Comparison with Peers',
            xaxis_title='Volatility (%)',
            yaxis_title='Annualized Return (%)',
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_performance_comparison_table(self, results):
        """Create performance comparison table"""
        if not results or 'peers' not in results:
            return None
        
        target = results['target']
        peer_stats = results.get('peer_stats', {})
        rankings = results.get('rankings', {})
        
        comparison_data = []
        
        metrics_info = [
            ('total_return', 'Total Return (%)', True),
            ('annualized_return', 'Annualized Return (%)', True),
            ('volatility', 'Volatility (%)', False),
            ('max_drawdown', 'Max Drawdown (%)', False),
            ('sharpe_ratio', 'Sharpe Ratio', True)
        ]
        
        for metric, display_name, higher_better in metrics_info:
            target_value = target['metrics'].get(metric, 0)
            peer_median = peer_stats.get(metric, {}).get('median', 0)
            rank_info = rankings.get(metric, {})
            
            if rank_info:
                rank_text = f"{rank_info['rank']}/{rank_info['total']} ({rank_info['percentile']:.0f}th %ile)"
            else:
                rank_text = "N/A"
            
            comparison_data.append({
                'Metric': display_name,
                'Target Fund': f"{target_value:.2f}",
                'Peer Median': f"{peer_median:.2f}",
                'Ranking': rank_text,
                'Better than Median': "✅" if (higher_better and target_value > peer_median) or 
                                             (not higher_better and target_value < peer_median) else "❌"
            })
        
        return pd.DataFrame(comparison_data)

class BasicPortfolioTracker:
    """Basic portfolio tracking functionality"""
    
    def __init__(self):
        self.portfolio_key = 'user_portfolio'
    
    def add_fund_to_portfolio(self, fund_code, fund_name, investment_amount, investment_date=None):
        """Add fund to portfolio"""
        if 'portfolios' not in st.session_state:
            st.session_state.portfolios = {}
        
        if self.portfolio_key not in st.session_state.portfolios:
            st.session_state.portfolios[self.portfolio_key] = []
        
        portfolio = st.session_state.portfolios[self.portfolio_key]
        
        # Check if fund already exists
        for i, holding in enumerate(portfolio):
            if holding['fund_code'] == fund_code:
                # Update existing holding
                portfolio[i]['investment_amount'] += investment_amount
                return
        
        # Add new holding
        portfolio.append({
            'fund_code': fund_code,
            'fund_name': fund_name,
            'investment_amount': investment_amount,
            'investment_date': investment_date or datetime.now().strftime('%Y-%m-%d')
        })
    
    def remove_fund_from_portfolio(self, fund_code):
        """Remove fund from portfolio"""
        if self.portfolio_key in st.session_state.portfolios:
            portfolio = st.session_state.portfolios[self.portfolio_key]
            st.session_state.portfolios[self.portfolio_key] = [
                holding for holding in portfolio if holding['fund_code'] != fund_code
            ]
    
    def get_portfolio(self):
        """Get current portfolio"""
        if 'portfolios' not in st.session_state:
            return []
        
        return st.session_state.portfolios.get(self.portfolio_key, [])
    
    def calculate_portfolio_metrics(self, analyzer):
        """Calculate portfolio-level metrics"""
        portfolio = self.get_portfolio()
        if not portfolio:
            return {}
        
        portfolio_data = []
        total_investment = 0
        total_current_value = 0
        
        for holding in portfolio:
            # Get current fund data
            df, fund_name, error = analyzer.get_fund_data(holding['fund_code'])
            if df is not None and len(df) > 0:
                current_nav = df['nav'].iloc[-1]
                # Assuming units bought at average nav for simplicity
                avg_nav = df['nav'].mean()
                units = holding['investment_amount'] / avg_nav
                current_value = units * current_nav
                
                portfolio_data.append({
                    'fund_code': holding['fund_code'],
                    'fund_name': holding['fund_name'],
                    'investment_amount': holding['investment_amount'],
                    'current_value': current_value,
                    'units': units,
                    'current_nav': current_nav,
                    'returns': current_value - holding['investment_amount'],
                    'returns_percent': ((current_value - holding['investment_amount']) / holding['investment_amount']) * 100
                })
                
                total_investment += holding['investment_amount']
                total_current_value += current_value
        
        portfolio_returns = total_current_value - total_investment
        portfolio_returns_percent = (portfolio_returns / total_investment) * 100 if total_investment > 0 else 0
        
        return {
            'holdings': portfolio_data,
            'total_investment': total_investment,
            'total_current_value': total_current_value,
            'total_returns': portfolio_returns,
            'total_returns_percent': portfolio_returns_percent
        }
