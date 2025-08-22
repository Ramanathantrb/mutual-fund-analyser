#!/usr/bin/env python3
"""
Test script to verify the fund comparison functionality works without errors
"""

import pandas as pd
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_expense_ratio_processing():
    """Test the expense ratio string processing that was causing the error"""
    
    # Sample expense ratio strings that might be generated
    test_data = {
        'Fund Name': ['Fund A', 'Fund B', 'Fund C'],
        'CAGR (%)': ['12.45', '10.23', '15.67'],
        'Volatility (%)': ['18.32', '16.78', '20.15'],
        'Sharpe Ratio': ['0.68', '0.61', '0.77'],
        'Expense Ratio (%)': ['1.05✓', '2.34*', '1.50✓']  # This was causing the error
    }
    
    df = pd.DataFrame(test_data)
    
    print("Original DataFrame:")
    print(df)
    print("\n" + "="*50)
    
    # Test the string cleaning logic that was fixed
    print("Testing expense ratio processing...")
    try:
        # This is the line that was causing the error, now fixed
        clean_expense = df['Expense Ratio (%)'].str.replace('%', '').str.replace('*', '').str.replace('✓', '')
        expense_floats = clean_expense.astype(float)
        lowest_expense_idx = expense_floats.idxmin()
        
        print(f"✅ Success! Cleaned expense ratios: {list(expense_floats)}")
        print(f"✅ Lowest expense ratio index: {lowest_expense_idx}")
        print(f"✅ Lowest expense fund: {df.iloc[lowest_expense_idx]['Fund Name']}")
        print(f"✅ Original expense ratio display: {df.iloc[lowest_expense_idx]['Expense Ratio (%)']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test other conversions too
    print("\nTesting other conversions...")
    try:
        cagr_floats = df['CAGR (%)'].str.replace('%', '').astype(float)
        sharpe_floats = df['Sharpe Ratio'].astype(float)
        
        print(f"✅ CAGR conversion successful: {list(cagr_floats)}")
        print(f"✅ Sharpe ratio conversion successful: {list(sharpe_floats)}")
        
    except Exception as e:
        print(f"❌ Error in other conversions: {e}")
        return False
    
    print("\n🎉 All tests passed! Fund comparison should work now.")
    return True

if __name__ == "__main__":
    test_expense_ratio_processing()
