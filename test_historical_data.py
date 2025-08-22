#!/usr/bin/env python3
"""
Test script to verify historical data fetching works properly
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import sys

def test_mf_api(scheme_code="120503"):
    """Test MF API for historical data"""
    print(f"🔍 Testing MF API for scheme {scheme_code}...")
    
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                print(f"✅ MF API Success: Found {len(data['data'])} records")
                print(f"📅 Latest record: {data['data'][0]}")
                print(f"🏛️ Fund: {data.get('meta', {}).get('scheme_name', 'Unknown')}")
                return True, len(data['data'])
            else:
                print("❌ MF API: No data found")
                return False, 0
        else:
            print(f"❌ MF API: HTTP {response.status_code}")
            return False, 0
    except Exception as e:
        print(f"❌ MF API Error: {e}")
        return False, 0

def test_amfi_portal(scheme_code="120503"):
    """Test AMFI Portal for historical data"""
    print(f"🔍 Testing AMFI Portal for scheme {scheme_code}...")
    
    try:
        from_date = (datetime.now() - timedelta(days=30)).strftime('%d-%b-%Y')
        to_date = datetime.now().strftime('%d-%b-%Y')
        
        amfi_url = f"https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"
        payload = {
            'frmdt': from_date,
            'todt': to_date,
            'sccode': scheme_code
        }
        
        response = requests.post(amfi_url, data=payload, timeout=20, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        if response.status_code == 200 and response.text.strip():
            lines = response.text.strip().split('\n')
            print(f"✅ AMFI Portal Success: Found {len(lines)-1} records")
            if len(lines) > 1:
                print(f"📅 Sample record: {lines[1]}")
            return True, len(lines)-1
        else:
            print(f"❌ AMFI Portal: No data or HTTP {response.status_code}")
            return False, 0
    except Exception as e:
        print(f"❌ AMFI Portal Error: {e}")
        return False, 0

def test_amfi_current_nav(scheme_code="120503"):
    """Test AMFI current NAV fetching"""
    print(f"🔍 Testing AMFI Current NAV for scheme {scheme_code}...")
    
    try:
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            
            for line in lines:
                if ';' in line:
                    parts = line.split(';')
                    if len(parts) >= 6 and parts[0].strip() == str(scheme_code):
                        print(f"✅ AMFI Current NAV Success")
                        print(f"🏛️ Scheme: {parts[3].strip()}")
                        print(f"💰 NAV: ₹{parts[4].strip()}")
                        print(f"📅 Date: {parts[5].strip()}")
                        return True, parts[4].strip()
            
            print(f"❌ AMFI Current NAV: Scheme {scheme_code} not found")
            return False, None
        else:
            print(f"❌ AMFI Current NAV: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ AMFI Current NAV Error: {e}")
        return False, None

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 HISTORICAL DATA FETCHING TESTS")
    print("="*60)
    
    # Test with popular fund codes
    test_schemes = [
        "120503",  # SBI Bluechip Fund
        "100050",  # HDFC Top 100 Fund
        "119551",  # ICICI Prudential Bluechip Fund
    ]
    
    for scheme_code in test_schemes:
        print(f"\n🎯 Testing Scheme Code: {scheme_code}")
        print("-" * 40)
        
        # Test all methods
        mf_success, mf_records = test_mf_api(scheme_code)
        amfi_success, amfi_records = test_amfi_portal(scheme_code)
        nav_success, nav_value = test_amfi_current_nav(scheme_code)
        
        print(f"\n📊 Results for {scheme_code}:")
        print(f"   MF API: {'✅' if mf_success else '❌'} ({mf_records} records)")
        print(f"   AMFI Portal: {'✅' if amfi_success else '❌'} ({amfi_records} records)")
        print(f"   Current NAV: {'✅' if nav_success else '❌'} (₹{nav_value if nav_value else 'N/A'})")
        
        if mf_success or amfi_success:
            print(f"   🎉 Historical data AVAILABLE for scheme {scheme_code}")
        elif nav_success:
            print(f"   ⚠️  Only current NAV available for scheme {scheme_code}")
        else:
            print(f"   ❌ No data available for scheme {scheme_code}")
    
    print("\n" + "="*60)
    print("🏁 TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
