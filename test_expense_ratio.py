#!/usr/bin/env python3
"""
Test script to find actual expense ratio data sources
"""

import requests
import re
import json
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_expense_sources(scheme_code, scheme_name):
    """Test various sources for expense ratio data"""
    print(f"🧪 Testing expense ratio sources for: {scheme_name}")
    print(f"📊 Scheme Code: {scheme_code}")
    print("=" * 80)
    
    # 1. Test AMFI scheme details page
    print("🔍 Testing AMFI Scheme Details...")
    try:
        url = f"https://www.amfiindia.com/modules/SchemeDetailsPopup.aspx?SchemeCode={scheme_code}"
        response = requests.get(url, timeout=15, verify=False)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            # Save content for analysis
            with open(f"amfi_scheme_{scheme_code}.html", "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Saved content to amfi_scheme_{scheme_code}.html")
            
            # Look for expense patterns
            expense_patterns = [
                r'expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                r'total\s*expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                r'ter[:\s]*(\d+\.?\d*)%?',
                r'(\d+\.?\d*)%?\s*expense\s*ratio',
                r'ongoing\s*charges[:\s]*(\d+\.?\d*)%?'
            ]
            
            for pattern in expense_patterns:
                matches = re.findall(pattern, content.lower())
                if matches:
                    print(f"📈 Found pattern '{pattern}': {matches}")
        else:
            print(f"❌ Failed to fetch AMFI data")
    except Exception as e:
        print(f"❌ AMFI Error: {e}")
    
    print("\n" + "-" * 40)
    
    # 2. Test MorningStar India
    print("🔍 Testing MorningStar API...")
    try:
        # Search for fund on MorningStar
        search_url = f"https://www.morningstar.in/search/default.aspx?q={scheme_name.replace(' ', '%20')}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ MorningStar accessible - would need detailed parsing")
        else:
            print("❌ MorningStar not accessible")
    except Exception as e:
        print(f"❌ MorningStar Error: {e}")
    
    print("\n" + "-" * 40)
    
    # 3. Test Value Research API
    print("🔍 Testing Value Research...")
    try:
        # Try to find fund on VR
        search_term = scheme_name.replace(' ', '%20')
        vr_url = f"https://www.valueresearchonline.com/funds/search/?s={search_term}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(vr_url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Value Research accessible - would need detailed parsing")
        else:
            print("❌ Value Research not accessible")
    except Exception as e:
        print(f"❌ Value Research Error: {e}")
    
    print("\n" + "-" * 40)
    
    # 4. Test MF Central API
    print("🔍 Testing MF Central...")
    try:
        # MF Central might have expense ratio data
        mfc_url = f"https://portal.mfcentral.com/api/schemes/search?q={scheme_name.replace(' ', '%20')}"
        response = requests.get(mfc_url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MF Central response: {len(str(data))} chars")
        else:
            print("❌ MF Central not accessible")
    except Exception as e:
        print(f"❌ MF Central Error: {e}")
    
    print("\n" + "-" * 40)
    
    # 5. Test RupeeVest/MoneyControl
    print("🔍 Testing MoneyControl...")
    try:
        search_term = scheme_name.replace(' ', '-').lower()
        mc_url = f"https://www.moneycontrol.com/mutual-funds/search?query={search_term}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(mc_url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ MoneyControl accessible")
        else:
            print("❌ MoneyControl not accessible")
    except Exception as e:
        print(f"❌ MoneyControl Error: {e}")

if __name__ == "__main__":
    # Test with Quant ELSS Tax Saver Direct
    test_cases = [
        ("120503", "Axis ELSS Tax Saver Fund - Direct Plan - Growth Option"),
        ("145606", "Quant ELSS Tax Saver Fund - Direct Plan - Growth Option"),  # If we can find the code
        ("119551", "Aditya Birla Sun Life Banking & PSU Debt Fund - DIRECT - IDCW")
    ]
    
    for scheme_code, scheme_name in test_cases:
        test_expense_sources(scheme_code, scheme_name)
        print("\n" + "=" * 80 + "\n")
