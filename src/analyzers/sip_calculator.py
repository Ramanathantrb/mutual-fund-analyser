import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import math

class SIPCalculator:
    """Enhanced SIP Calculator with goal-based planning and inflation adjustment"""
    
    def __init__(self):
        # Common financial goals with typical timeframes
        self.goal_templates = {
            'Retirement': {'typical_years': 30, 'inflation_sensitive': True},
            'Child Education': {'typical_years': 15, 'inflation_sensitive': True},
            'Child Marriage': {'typical_years': 20, 'inflation_sensitive': True},
            'House Purchase': {'typical_years': 10, 'inflation_sensitive': True},
            'Car Purchase': {'typical_years': 5, 'inflation_sensitive': False},
            'Emergency Fund': {'typical_years': 1, 'inflation_sensitive': False},
            'Vacation': {'typical_years': 2, 'inflation_sensitive': False},
            'Custom Goal': {'typical_years': 10, 'inflation_sensitive': True}
        }
    
    def calculate_sip_returns(self, monthly_amount, annual_return, years):
        """Calculate SIP returns using compound interest formula"""
        monthly_rate = annual_return / 12 / 100
        months = years * 12
        
        if monthly_rate == 0:
            future_value = monthly_amount * months
            total_invested = monthly_amount * months
        else:
            # Future Value of SIP formula
            future_value = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
            total_invested = monthly_amount * months
        
        returns = future_value - total_invested
        
        return {
            'future_value': future_value,
            'total_invested': total_invested,
            'returns': returns,
            'return_percentage': (returns / total_invested) * 100 if total_invested > 0 else 0
        }
    
    def calculate_required_sip(self, target_amount, annual_return, years):
        """Calculate required monthly SIP to reach target"""
        monthly_rate = annual_return / 12 / 100
        months = years * 12
        
        if monthly_rate == 0:
            required_sip = target_amount / months
        else:
            # Reverse calculation for required SIP
            required_sip = target_amount * monthly_rate / (((1 + monthly_rate) ** months - 1) * (1 + monthly_rate))
        
        return required_sip
    
    def calculate_inflation_adjusted_goal(self, current_cost, years, inflation_rate=6):
        """Calculate future value of goal considering inflation"""
        future_value = current_cost * ((1 + inflation_rate/100) ** years)
        return future_value
    
    def calculate_goal_based_sip(self, goal_amount, years, expected_return, inflation_rate=0):
        """Calculate SIP required for a specific goal"""
        # Adjust goal for inflation if specified
        if inflation_rate > 0:
            adjusted_goal = self.calculate_inflation_adjusted_goal(goal_amount, years, inflation_rate)
        else:
            adjusted_goal = goal_amount
        
        required_sip = self.calculate_required_sip(adjusted_goal, expected_return, years)
        
        return {
            'original_goal': goal_amount,
            'inflation_adjusted_goal': adjusted_goal,
            'required_monthly_sip': required_sip,
            'total_investment': required_sip * years * 12,
            'inflation_impact': adjusted_goal - goal_amount
        }
    
    def calculate_step_up_sip(self, initial_amount, annual_return, years, step_up_rate=10):
        """Calculate SIP with annual step-up"""
        monthly_rate = annual_return / 12 / 100
        total_value = 0
        yearly_projections = []
        
        for year in range(1, years + 1):
            # Calculate stepped up amount for this year
            current_sip = initial_amount * ((1 + step_up_rate/100) ** (year - 1))
            
            # Calculate value for this year's contributions
            months_in_year = 12
            if monthly_rate == 0:
                year_value = current_sip * months_in_year
            else:
                year_value = current_sip * (((1 + monthly_rate) ** months_in_year - 1) / monthly_rate) * (1 + monthly_rate)
            
            # Compound previous years' value
            if year > 1:
                total_value = total_value * (1 + annual_return/100) + year_value
            else:
                total_value = year_value
            
            yearly_projections.append({
                'year': year,
                'monthly_sip': current_sip,
                'annual_investment': current_sip * 12,
                'cumulative_value': total_value,
                'cumulative_investment': sum(p['annual_investment'] for p in yearly_projections)
            })
        
        total_invested = sum(p['annual_investment'] for p in yearly_projections)
        total_returns = total_value - total_invested
        
        return {
            'final_value': total_value,
            'total_invested': total_invested,
            'total_returns': total_returns,
            'return_percentage': (total_returns / total_invested) * 100 if total_invested > 0 else 0,
            'yearly_projections': yearly_projections
        }
    
    def compare_sip_scenarios(self, base_amount, annual_return, years):
        """Compare different SIP scenarios"""
        scenarios = {}
        
        # Regular SIP
        regular = self.calculate_sip_returns(base_amount, annual_return, years)
        scenarios['Regular SIP'] = regular
        
        # Step-up SIPs
        for step_up in [5, 10, 15]:
            step_up_result = self.calculate_step_up_sip(base_amount, annual_return, years, step_up)
            scenarios[f'Step-up {step_up}%'] = step_up_result
        
        return scenarios
        """Generate year-wise SIP projection"""
        projections = []
        cumulative_invested = 0
        cumulative_value = 0
        
        for year in range(1, years + 1):
            year_invested = monthly_amount * 12
            cumulative_invested += year_invested
            
            # Calculate value at end of this year
            result = self.calculate_sip_returns(monthly_amount, annual_return, year)
            cumulative_value = result['future_value']
            year_returns = cumulative_value - cumulative_invested
            
            projections.append({
                'Year': year,
                'Invested This Year': f"₹{year_invested:,.0f}",
                'Total Invested': f"₹{cumulative_invested:,.0f}",
                'Portfolio Value': f"₹{cumulative_value:,.0f}",
                'Total Returns': f"₹{year_returns:,.0f}",
                'Return %': f"{(year_returns/cumulative_invested)*100:.1f}%"
            })
        
        return pd.DataFrame(projections)
    
    def create_sip_growth_chart(self, monthly_amount, annual_return, years):
        """Create SIP growth visualization"""
        months = years * 12
        monthly_rate = annual_return / 12 / 100
        
        # Calculate month-wise values
        months_list = list(range(1, months + 1))
        invested_amounts = []
        portfolio_values = []
        
        for month in months_list:
            invested = monthly_amount * month
            
            if monthly_rate == 0:
                value = invested
            else:
                value = monthly_amount * (((1 + monthly_rate) ** month - 1) / monthly_rate) * (1 + monthly_rate)
            
            invested_amounts.append(invested)
            portfolio_values.append(value)
        
        # Create chart
        fig = go.Figure()
        
        # Invested amount area
        fig.add_trace(go.Scatter(
            x=months_list,
            y=invested_amounts,
            fill='tozeroy',
            mode='lines',
            name='Total Invested',
            line=dict(color='#FF6B6B', width=2),
            hovertemplate='Month: %{x}<br>Invested: ₹%{y:,.0f}<extra></extra>'
        ))
        
        # Portfolio value area
        fig.add_trace(go.Scatter(
            x=months_list,
            y=portfolio_values,
            fill='tonexty',
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#4ECDC4', width=2),
            hovertemplate='Month: %{x}<br>Value: ₹%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'SIP Growth Projection - ₹{monthly_amount:,}/month @ {annual_return}% p.a.',
            xaxis_title='Months',
            yaxis_title='Amount (₹)',
            template='plotly_white',
            hovermode='x unified',
            height=500
        )
        
        return fig
    
    def calculate_inflation_adjusted_target(self, current_cost, inflation_rate, years):
        """Calculate inflation-adjusted target amount"""
        future_cost = current_cost * (1 + inflation_rate/100) ** years
        return future_cost

class GoalPlanner:
    """Goal-based financial planning"""
    
    def __init__(self):
        self.sip_calc = SIPCalculator()
    
    def calculate_goal_planning(self, goal_amount, current_age, goal_age, expected_return, inflation_rate=6):
        """Calculate comprehensive goal planning"""
        years_to_goal = goal_age - current_age
        
        if years_to_goal <= 0:
            return None
        
        # Inflation-adjusted goal amount
        inflation_adjusted_goal = self.sip_calc.calculate_inflation_adjusted_target(
            goal_amount, inflation_rate, years_to_goal
        )
        
        # Required SIP calculation
        required_sip = self.sip_calc.calculate_required_sip(
            inflation_adjusted_goal, expected_return, years_to_goal
        )
        
        # SIP projection
        sip_result = self.sip_calc.calculate_sip_returns(
            required_sip, expected_return, years_to_goal
        )
        
        return {
            'years_to_goal': years_to_goal,
            'original_goal': goal_amount,
            'inflation_adjusted_goal': inflation_adjusted_goal,
            'required_monthly_sip': required_sip,
            'total_investment': sip_result['total_invested'],
            'final_corpus': sip_result['future_value'],
            'inflation_impact': inflation_adjusted_goal - goal_amount
        }

def render_sip_calculator_page():
    """Render SIP calculator and goal planning page"""
    st.header("💰 SIP Calculator & Goal Planner")
    
    # Tab selection
    tab1, tab2, tab3 = st.tabs(["🧮 SIP Calculator", "🎯 Goal Planner", "📊 Comparison Tool"])
    
    with tab1:
        st.subheader("📈 SIP Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_sip = st.number_input(
                "💵 Monthly SIP Amount (₹)",
                min_value=500,
                max_value=1000000,
                value=10000,
                step=500,
                help="Enter your monthly SIP investment amount"
            )
            
            investment_period = st.number_input(
                "📅 Investment Period (Years)",
                min_value=1,
                max_value=50,
                value=15,
                step=1,
                help="How long do you plan to invest?"
            )
        
        with col2:
            expected_return = st.slider(
                "📊 Expected Annual Return (%)",
                min_value=1.0,
                max_value=25.0,
                value=12.0,
                step=0.5,
                help="Expected annual return rate"
            )
            
            step_up_rate = st.slider(
                "🔄 Annual Step-up (%)",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=1.0,
                help="Annual increase in SIP amount"
            )
        
        if st.button("💡 Calculate SIP Returns", type="primary"):
            sip_calc = SIPCalculator()
            
            # Basic SIP calculation
            result = sip_calc.calculate_sip_returns(monthly_sip, expected_return, investment_period)
            
            # Display results
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Future Value", f"₹{result['future_value']:,.0f}")
            
            with col2:
                st.metric("📥 Total Invested", f"₹{result['total_invested']:,.0f}")
            
            with col3:
                st.metric("📈 Total Returns", f"₹{result['returns']:,.0f}")
            
            with col4:
                st.metric("📊 Return %", f"{result['return_percentage']:.1f}%")
            
            # SIP growth chart
            growth_chart = sip_calc.create_sip_growth_chart(monthly_sip, expected_return, investment_period)
            st.plotly_chart(growth_chart, use_container_width=True)
            
            # Year-wise projection table
            st.subheader("📋 Year-wise Projection")
            projection_df = sip_calc.generate_sip_projection_table(monthly_sip, expected_return, investment_period)
            st.dataframe(projection_df, use_container_width=True)
    
    with tab2:
        st.subheader("🎯 Goal-Based Planning")
        
        goal_planner = GoalPlanner()
        
        # Goal selection
        goal_type = st.selectbox(
            "🎯 Select Goal Type",
            ["Custom Goal", "Child Education", "Retirement", "House Purchase", "Car Purchase", "Vacation"]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if goal_type == "Child Education":
                goal_amount = st.number_input("💰 Education Cost Today (₹)", value=2500000, step=100000)
            elif goal_type == "Retirement":
                goal_amount = st.number_input("💰 Retirement Corpus (₹)", value=10000000, step=500000)
            elif goal_type == "House Purchase":
                goal_amount = st.number_input("💰 House Cost (₹)", value=5000000, step=500000)
            else:
                goal_amount = st.number_input("💰 Goal Amount (₹)", value=1000000, step=100000)
            
            current_age = st.number_input("👤 Current Age", min_value=18, max_value=80, value=30)
            
        with col2:
            if goal_type == "Child Education":
                goal_age = st.number_input("📅 Child's Education Age", min_value=current_age, max_value=100, value=48)
            elif goal_type == "Retirement":
                goal_age = st.number_input("📅 Retirement Age", min_value=current_age, max_value=100, value=60)
            else:
                goal_age = st.number_input("📅 Goal Achievement Age", min_value=current_age, max_value=100, value=45)
            
            expected_return_goal = st.slider("📊 Expected Return (%)", min_value=1.0, max_value=25.0, value=12.0, step=0.5)
            inflation_rate = st.slider("💹 Inflation Rate (%)", min_value=1.0, max_value=15.0, value=6.0, step=0.5)
        
        if st.button("🎯 Calculate Goal Plan", type="primary"):
            goal_plan = goal_planner.calculate_goal_planning(
                goal_amount, current_age, goal_age, expected_return_goal, inflation_rate
            )
            
            if goal_plan:
                st.success("✅ Goal plan calculated successfully!")
                
                # Display goal planning results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🎯 Original Goal", f"₹{goal_plan['original_goal']:,.0f}")
                    st.metric("💹 Inflation Impact", f"₹{goal_plan['inflation_impact']:,.0f}")
                
                with col2:
                    st.metric("📈 Inflation Adjusted Goal", f"₹{goal_plan['inflation_adjusted_goal']:,.0f}")
                    st.metric("📅 Years to Goal", f"{goal_plan['years_to_goal']}")
                
                with col3:
                    st.metric("💰 Required Monthly SIP", f"₹{goal_plan['required_monthly_sip']:,.0f}")
                    st.metric("📥 Total Investment", f"₹{goal_plan['total_investment']:,.0f}")
                
                # Goal achievement chart
                sip_calc = SIPCalculator()
                goal_chart = sip_calc.create_sip_growth_chart(
                    goal_plan['required_monthly_sip'], 
                    expected_return_goal, 
                    goal_plan['years_to_goal']
                )
                goal_chart.update_layout(title=f"Goal Achievement Plan - {goal_type}")
                st.plotly_chart(goal_chart, use_container_width=True)
            else:
                st.error("❌ Invalid goal parameters. Please check your inputs.")
    
    with tab3:
        st.subheader("📊 SIP Comparison Tool")
        st.info("Compare different SIP scenarios side by side")
        
        # Multiple SIP scenarios
        num_scenarios = st.slider("Number of Scenarios", min_value=2, max_value=5, value=3)
        
        scenarios = []
        for i in range(num_scenarios):
            st.subheader(f"Scenario {i+1}")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                amount = st.number_input(f"Monthly SIP {i+1} (₹)", value=5000*(i+1), key=f"amount_{i}")
            with col2:
                return_rate = st.number_input(f"Return Rate {i+1} (%)", value=10.0+i, key=f"return_{i}")
            with col3:
                period = st.number_input(f"Period {i+1} (Years)", value=15, key=f"period_{i}")
            
            scenarios.append({'amount': amount, 'return': return_rate, 'period': period, 'name': f"Scenario {i+1}"})
        
        if st.button("📊 Compare Scenarios", type="primary"):
            # Calculate all scenarios
            sip_calc = SIPCalculator()
            comparison_results = []
            
            fig = go.Figure()
            colors = px.colors.qualitative.Set3
            
            for i, scenario in enumerate(scenarios):
                result = sip_calc.calculate_sip_returns(
                    scenario['amount'], scenario['return'], scenario['period']
                )
                
                comparison_results.append({
                    'Scenario': scenario['name'],
                    'Monthly SIP': f"₹{scenario['amount']:,}",
                    'Return Rate': f"{scenario['return']}%",
                    'Period': f"{scenario['period']} years",
                    'Future Value': f"₹{result['future_value']:,.0f}",
                    'Total Returns': f"₹{result['returns']:,.0f}"
                })
                
                # Add to chart
                months = scenario['period'] * 12
                months_list = list(range(1, months + 1))
                portfolio_values = []
                
                monthly_rate = scenario['return'] / 12 / 100
                for month in months_list:
                    if monthly_rate == 0:
                        value = scenario['amount'] * month
                    else:
                        value = scenario['amount'] * (((1 + monthly_rate) ** month - 1) / monthly_rate) * (1 + monthly_rate)
                    portfolio_values.append(value)
                
                fig.add_trace(go.Scatter(
                    x=months_list,
                    y=portfolio_values,
                    mode='lines',
                    name=scenario['name'],
                    line=dict(color=colors[i % len(colors)], width=3)
                ))
            
            # Display comparison table
            comparison_df = pd.DataFrame(comparison_results)
            st.dataframe(comparison_df, use_container_width=True)
            
            # Display comparison chart
            fig.update_layout(
                title='SIP Scenarios Comparison',
                xaxis_title='Months',
                yaxis_title='Portfolio Value (₹)',
                template='plotly_white',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
