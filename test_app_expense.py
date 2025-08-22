#!/usr/bin/env python3
"""
Comprehensive expense ratio test for the app
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_actual_expense_ratio

def test_app_expense_fetching():
    """Test our app's expense ratio fetching"""
    
    test_funds = [
        ("120847", "quant ELSS Tax Saver Fund - Growth Option - Direct Plan"),
        ("120503", "Axis ELSS Tax Saver Fund - Direct Plan - Growth Option"),
        ("119551", "Aditya Birla Sun Life Banking & PSU Debt Fund - DIRECT - IDCW"),
        ("100175", "quant ELSS Tax Saver Fund - Growth Option - Regular Plan")
    ]
    
    print("🧪 Testing App's Expense Ratio Fetching")
    print("=" * 60)
    
    for scheme_code, fund_name in test_funds:
        print(f"\n🔍 Testing: {fund_name}")
        print(f"Code: {scheme_code}")
        
        try:
            expense_ratio = get_actual_expense_ratio(scheme_code, fund_name)
            print(f"✅ Expense Ratio: {expense_ratio:.2f}%")
            
            # Check if it's likely estimated vs actual
            from app import estimate_expense_ratio_improved
            estimated = estimate_expense_ratio_improved(fund_name)
            
            if abs(expense_ratio - estimated) < 0.01:
                print("   📊 Source: Estimated (no actual data found)")
            else:
                print("   🎯 Source: Actual data found!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_app_expense_fetching()
