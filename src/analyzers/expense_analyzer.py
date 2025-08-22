import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta

class ExpenseAnalyzer:
    """Analyze expense ratios and their impact on returns"""
    
    def __init__(self):
        # Common expense ratios by fund category (approximate industry averages)
        self.category_expense_ranges = {
            'Large Cap': {'min': 0.5, 'max': 2.5, 'avg': 1.2},
            'Mid Cap': {'min': 0.8, 'max': 2.8, 'avg': 1.8},
            'Small Cap': {'min': 1.0, 'max': 3.0, 'avg': 2.0},
            'Multi Cap': {'min': 0.8, 'max': 2.5, 'avg': 1.5},
            'ELSS': {'min': 0.8, 'max': 2.5, 'avg': 1.4},
            'Index': {'min': 0.1, 'max': 1.0, 'avg': 0.3},
            'Debt': {'min': 0.3, 'max': 2.0, 'avg': 0.8},
            'Hybrid': {'min': 0.5, 'max': 2.2, 'avg': 1.3},
            'Solution Oriented': {'min': 0.8, 'max': 2.5, 'avg': 1.6}
        }
    
    def categorize_fund_type(self, fund_name):
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
        elif any(term in fund_name_lower for term in ['debt', 'bond', 'gilt', 'liquid', 'ultra short', 'short term', 'medium term', 'long term', 'credit']):
            return 'Debt'
        elif any(term in fund_name_lower for term in ['hybrid', 'balanced', 'conservative', 'aggressive']):
            return 'Hybrid'
        elif any(term in fund_name_lower for term in ['retirement', 'children', 'solution']):
            return 'Solution Oriented'
        else:
            return 'Other'
    
    def estimate_expense_ratio(self, fund_name, is_direct=True):
        """Estimate expense ratio based on fund category and plan type"""
        category = self.categorize_fund_type(fund_name)
        
        if category in self.category_expense_ranges:
            base_expense = self.category_expense_ranges[category]['avg']
        else:
            base_expense = 1.5  # Default average
        
        # Direct plans typically have 0.5-1% lower expense ratio
        if is_direct:
            return max(0.1, base_expense - 0.7)
        else:
            return base_expense
    
    def calculate_expense_impact(self, investment_amount, annual_return, years, expense_ratio):
        """Calculate the impact of expense ratio on returns"""
        # Net return after expenses
        net_return = annual_return - expense_ratio
        
        # Future value with and without expenses
        gross_value = investment_amount * ((1 + annual_return/100) ** years)
        net_value = investment_amount * ((1 + net_return/100) ** years)
        
        expense_cost = gross_value - net_value
        
        return {
            'gross_value': gross_value,
            'net_value': net_value,
            'expense_cost': expense_cost,
            'expense_percentage': (expense_cost / gross_value) * 100,
            'net_return': net_return
        }
    
    def compare_direct_vs_regular(self, fund_name, investment_amount=100000, annual_return=12, years=10):
        """Compare direct vs regular plan impact"""
        regular_expense = self.estimate_expense_ratio(fund_name, is_direct=False)
        direct_expense = self.estimate_expense_ratio(fund_name, is_direct=True)
        
        regular_impact = self.calculate_expense_impact(investment_amount, annual_return, years, regular_expense)
        direct_impact = self.calculate_expense_impact(investment_amount, annual_return, years, direct_expense)
        
        savings = regular_impact['expense_cost'] - direct_impact['expense_cost']
        
        return {
            'regular': {
                'expense_ratio': regular_expense,
                'final_value': regular_impact['net_value'],
                'expense_cost': regular_impact['expense_cost']
            },
            'direct': {
                'expense_ratio': direct_expense,
                'final_value': direct_impact['net_value'],
                'expense_cost': direct_impact['expense_cost']
            },
            'savings': savings,
            'savings_percentage': (savings / investment_amount) * 100
        }
    
    def create_expense_impact_chart(self, fund_name, investment_amount=100000, annual_return=12):
        """Create visualization showing expense impact over time"""
        years = list(range(1, 21))  # 1 to 20 years
        regular_values = []
        direct_values = []
        
        for year in years:
            comparison = self.compare_direct_vs_regular(fund_name, investment_amount, annual_return, year)
            regular_values.append(comparison['regular']['final_value'])
            direct_values.append(comparison['direct']['final_value'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=direct_values,
            mode='lines+markers',
            name='Direct Plan',
            line=dict(color='green', width=3),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=regular_values,
            mode='lines+markers',
            name='Regular Plan',
            line=dict(color='red', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title=f'Direct vs Regular Plan Impact - {fund_name[:50]}...',
            xaxis_title='Investment Period (Years)',
            yaxis_title='Portfolio Value (₹)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def get_expense_analysis_summary(self, fund_name):
        """Get comprehensive expense analysis summary"""
        category = self.categorize_fund_type(fund_name)
        direct_expense = self.estimate_expense_ratio(fund_name, is_direct=True)
        regular_expense = self.estimate_expense_ratio(fund_name, is_direct=False)
        
        # Industry comparison
        if category in self.category_expense_ranges:
            category_avg = self.category_expense_ranges[category]['avg']
            category_min = self.category_expense_ranges[category]['min']
            category_max = self.category_expense_ranges[category]['max']
        else:
            category_avg = 1.5
            category_min = 0.5
            category_max = 2.5
        
        # Grade the expense ratio
        if direct_expense <= category_min + 0.2:
            grade = "A+ (Excellent)"
        elif direct_expense <= category_avg - 0.3:
            grade = "A (Very Good)"
        elif direct_expense <= category_avg:
            grade = "B (Good)"
        elif direct_expense <= category_avg + 0.3:
            grade = "C (Average)"
        else:
            grade = "D (High)"
        
        return {
            'fund_category': category,
            'estimated_direct_expense': direct_expense,
            'estimated_regular_expense': regular_expense,
            'category_average': category_avg,
            'category_range': f"{category_min}% - {category_max}%",
            'expense_grade': grade,
            'is_below_average': direct_expense < category_avg
        }

class FundScreener:
    """Screen and filter funds based on various criteria"""
    
    def __init__(self, amfi_fetcher):
        self.amfi_fetcher = amfi_fetcher
        
    def screen_funds(self, schemes_df, criteria):
        """Screen funds based on multiple criteria"""
        filtered_df = schemes_df.copy()
        
        # Filter by category
        if criteria.get('categories'):
            category_filter = '|'.join(criteria['categories'])
            filtered_df = filtered_df[
                filtered_df['scheme_name'].str.contains(category_filter, case=False, na=False)
            ]
        
        # Filter by AMC
        if criteria.get('amcs'):
            amc_filter = '|'.join(criteria['amcs'])
            filtered_df = filtered_df[
                filtered_df['amc_name'].str.contains(amc_filter, case=False, na=False)
            ]
        
        # Filter by plan type
        if criteria.get('plan_type'):
            if criteria['plan_type'] == 'Direct':
                filtered_df = filtered_df[
                    filtered_df['scheme_name'].str.contains('Direct', case=False, na=False)
                ]
            elif criteria['plan_type'] == 'Regular':
                filtered_df = filtered_df[
                    ~filtered_df['scheme_name'].str.contains('Direct', case=False, na=False)
                ]
        
        # Filter by scheme type
        if criteria.get('scheme_types'):
            type_filter = '|'.join(criteria['scheme_types'])
            filtered_df = filtered_df[
                filtered_df['scheme_type'].str.contains(type_filter, case=False, na=False)
            ]
        
        return filtered_df
    
    def get_category_options(self, schemes_df):
        """Get available category options for filtering"""
        categories = []
        category_keywords = {
            'Large Cap': ['Large Cap', 'Blue Chip', 'Bluechip'],
            'Mid Cap': ['Mid Cap', 'Midcap'],
            'Small Cap': ['Small Cap', 'Smallcap'],
            'Multi Cap': ['Multi Cap', 'Multicap', 'Flexi Cap'],
            'ELSS': ['ELSS', 'Tax Saver', 'Equity Linked'],
            'Index': ['Index', 'ETF', 'Nifty', 'Sensex'],
            'Debt': ['Debt', 'Bond', 'Gilt', 'Liquid'],
            'Hybrid': ['Hybrid', 'Balanced'],
            'Sector': ['Sector', 'Thematic', 'Banking', 'IT', 'Pharma'],
            'International': ['International', 'Global', 'US', 'Overseas']
        }
        
        for category, keywords in category_keywords.items():
            if any(schemes_df['scheme_name'].str.contains(keyword, case=False, na=False).any() 
                   for keyword in keywords):
                categories.append(category)
        
        return sorted(categories)
    
    def get_amc_options(self, schemes_df):
        """Get available AMC options for filtering"""
        return sorted(schemes_df['amc_name'].unique())
    
    def get_scheme_type_options(self, schemes_df):
        """Get available scheme type options"""
        return sorted(schemes_df['scheme_type'].unique())
