#!/usr/bin/env python3
"""
Test script to verify the enhanced features
"""

import sys
import os
import math

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import functions to test
from app import calculate_lumpsum_returns, calculate_sip_with_goals

def test_lumpsum_calculator():
    """Test the lumpsum calculator functionality"""
    print("Testing Lumpsum Calculator:")
    print("=" * 40)
    
    # Test case: ₹1,00,000 for 10 years at 12% return
    amount = 100000
    years = 10
    return_rate = 12
    inflation_rate = 6
    target = 300000
    
    result = calculate_lumpsum_returns(amount, years, return_rate, inflation_rate, target)
    
    print(f"Initial Investment: ₹{amount:,}")
    print(f"Investment Period: {years} years")
    print(f"Expected Return: {return_rate}%")
    print(f"Inflation Rate: {inflation_rate}%")
    print(f"Target Amount: ₹{target:,}")
    print()
    print("Results:")
    print(f"Future Value: ₹{result['future_value']:,.0f}")
    print(f"Inflation Adjusted Value: ₹{result['inflation_adjusted_value']:,.0f}")
    print(f"Total Gains: ₹{result['gains']:,.0f}")
    print(f"Absolute Return: {result['absolute_return']:.1f}%")
    print(f"Real Return: {result['real_return']:.1f}%")
    
    if result['years_to_target']:
        print(f"Years to reach target: {result['years_to_target']:.1f}")
    if result['required_return']:
        print(f"Required return for target: {result['required_return']:.1f}%")
    if result['required_investment']:
        print(f"Required investment for target: ₹{result['required_investment']:,.0f}")

def test_enhanced_sip():
    """Test the enhanced SIP calculator with existing investment"""
    print("\n" + "=" * 50)
    print("Testing Enhanced SIP Calculator:")
    print("=" * 40)
    
    # Test case: ₹5,000 SIP for 15 years with ₹50,000 existing investment
    monthly_sip = 5000
    years = 15
    return_rate = 12
    inflation_rate = 6
    target = 2000000
    existing_lumpsum = 50000
    
    result = calculate_sip_with_goals(monthly_sip, years, target, return_rate, inflation_rate, existing_lumpsum)
    
    print(f"Monthly SIP: ₹{monthly_sip:,}")
    print(f"Existing Investment: ₹{existing_lumpsum:,}")
    print(f"Investment Period: {years} years")
    print(f"Expected Return: {return_rate}%")
    print(f"Target Amount: ₹{target:,}")
    print()
    print("Results:")
    print(f"Total Future Value: ₹{result['future_value']:,.0f}")
    print(f"SIP Future Value: ₹{result['sip_future_value']:,.0f}")
    print(f"Existing Investment Future Value: ₹{result['lumpsum_future_value']:,.0f}")
    print(f"Total Invested: ₹{result['total_invested']:,.0f}")
    print(f"SIP Invested: ₹{result['sip_invested']:,.0f}")
    print(f"Total Gains: ₹{result['gains']:,.0f}")
    
    if result['required_sip'] is not None:
        print(f"Required SIP for target: ₹{result['required_sip']:,.0f}")

if __name__ == "__main__":
    test_lumpsum_calculator()
    test_enhanced_sip()
    print("\n🎉 All calculator tests completed successfully!")
