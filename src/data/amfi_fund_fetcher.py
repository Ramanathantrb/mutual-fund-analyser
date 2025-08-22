import requests
import pandas as pd
import json
import re
from urllib.parse import quote
import time

class AMFIFundFetcher:
    """Fetch mutual fund data directly from AMFI website"""
    
    def __init__(self):
        self.amfi_base_url = "https://www.amfiindia.com"
        self.nav_url = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"
        self.scheme_url = "https://www.amfiindia.com/spages/NAVAll.txt"
        self.funds_cache = {}
        self.session = requests.Session()
        
    def fetch_all_schemes(self):
        """Fetch all mutual fund schemes from AMFI"""
        try:
            print("🔄 Fetching all schemes from AMFI...")
            response = self.session.get(self.scheme_url, timeout=15)
            response.raise_for_status()
            
            # Parse the NAV file
            lines = response.text.strip().split('\n')
            schemes = []
            current_amc = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # AMC name lines don't have semicolons
                if ';' not in line:
                    current_amc = line
                    continue
                
                # Parse scheme data
                parts = line.split(';')
                if len(parts) >= 6:
                    scheme_code = parts[0].strip()
                    scheme_name = parts[3].strip()
                    nav = parts[4].strip()
                    date = parts[5].strip()
                    
                    if scheme_code and scheme_name and scheme_code.isdigit():
                        # Determine scheme type
                        scheme_type = self._determine_scheme_type(scheme_name)
                        
                        schemes.append({
                            'scheme_code': scheme_code,
                            'scheme_name': scheme_name,
                            'amc_name': current_amc,
                            'scheme_type': scheme_type,
                            'nav': nav,
                            'date': date
                        })
            
            print(f"✅ Found {len(schemes)} schemes from AMFI")
            return schemes
            
        except Exception as e:
            print(f"❌ Error fetching AMFI schemes: {e}")
            return []
    
    def _determine_scheme_type(self, scheme_name):
        """Determine scheme type based on name"""
        name_lower = scheme_name.lower()
        
        if any(term in name_lower for term in ['equity', 'large cap', 'mid cap', 'small cap', 'multi cap', 'flexi cap']):
            return 'Equity'
        elif any(term in name_lower for term in ['debt', 'bond', 'gilt', 'liquid', 'ultra short', 'short term', 'medium term', 'long term']):
            return 'Debt'
        elif any(term in name_lower for term in ['hybrid', 'balanced', 'conservative', 'aggressive']):
            return 'Hybrid'
        elif any(term in name_lower for term in ['elss', 'tax saver', 'equity linked']):
            return 'ELSS'
        elif any(term in name_lower for term in ['index', 'etf']):
            return 'Index'
        else:
            return 'Other'
    
    def search_schemes(self, search_term, limit=10):
        """Search for schemes by name"""
        if not self.funds_cache:
            self.funds_cache = self.fetch_all_schemes()
        
        search_term_lower = search_term.lower()
        results = []
        
        for scheme in self.funds_cache:
            scheme_name_lower = scheme['scheme_name'].lower()
            amc_name_lower = scheme['amc_name'].lower()
            
            # Search in scheme name and AMC name
            if (search_term_lower in scheme_name_lower or 
                search_term_lower in amc_name_lower):
                results.append(scheme)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_popular_schemes_by_category(self):
        """Get popular schemes organized by category"""
        if not self.funds_cache:
            self.funds_cache = self.fetch_all_schemes()
        
        categories = {
            'large_cap': [],
            'mid_cap': [],
            'small_cap': [],
            'elss': [],
            'index': [],
            'debt': [],
            'hybrid': []
        }
        
        # Keywords for categorization
        keywords = {
            'large_cap': ['large cap', 'large-cap', 'bluechip', 'blue chip', 'top 100', 'nifty 50'],
            'mid_cap': ['mid cap', 'mid-cap', 'midcap'],
            'small_cap': ['small cap', 'small-cap', 'smallcap'],
            'elss': ['elss', 'tax saver', 'tax saving', 'equity linked'],
            'index': ['index', 'nifty', 'sensex', 'bse', 'nse'],
            'debt': ['debt', 'bond', 'gilt', 'liquid', 'ultra short', 'short term', 'medium term', 'long term'],
            'hybrid': ['hybrid', 'balanced', 'allocation', 'aggressive', 'conservative']
        }
        
        for scheme in self.funds_cache:
            scheme_name_lower = scheme['scheme_name'].lower()
            
            # Skip regular/dividend plans, prefer direct growth
            if any(x in scheme_name_lower for x in ['regular', 'dividend', 'idcw']) and 'direct' not in scheme_name_lower:
                continue
            
            # Categorize schemes
            categorized = False
            for category, terms in keywords.items():
                if any(term in scheme_name_lower for term in terms):
                    if len(categories[category]) < 5:  # Limit to 5 per category
                        categories[category].append(scheme)
                        categorized = True
                        break
        
        return categories
    
    def validate_scheme_code(self, scheme_code):
        """Validate if scheme code exists in AMFI data"""
        if not self.funds_cache:
            self.funds_cache = self.fetch_all_schemes()
        
        for scheme in self.funds_cache:
            if scheme['scheme_code'] == str(scheme_code):
                return True, scheme
        
        return False, None

def display_amfi_fund_selector():
    """Interactive AMFI-based fund selector"""
    fetcher = AMFIFundFetcher()
    
    print("\n" + "="*80)
    print("🏛️  AMFI MUTUAL FUND SELECTOR")
    print("="*80)
    
    while True:
        print("\n📋 Options:")
        print("1. 🔍 Search funds by name")
        print("2. 📊 Browse popular funds by category")
        print("3. 🔢 Enter scheme code directly")
        print("4. ❌ Exit")
        
        choice = input("\n🔍 Enter your choice (1-4): ").strip()
        
        if choice == "1":
            # Search functionality
            search_term = input("\n🔍 Enter search term (fund name, AMC name): ").strip()
            if search_term:
                results = fetcher.search_schemes(search_term, limit=20)
                
                if results:
                    print(f"\n📊 Found {len(results)} matching schemes:")
                    print("-" * 80)
                    
                    for i, scheme in enumerate(results, 1):
                        print(f"{i:2}. {scheme['scheme_name'][:60]}")
                        print(f"    AMC: {scheme['amc_name']}")
                        print(f"    Code: {scheme['scheme_code']} | NAV: ₹{scheme['nav']} | Date: {scheme['date']}")
                        print()
                    
                    try:
                        selection = int(input(f"Select scheme (1-{len(results)}): ")) - 1
                        if 0 <= selection < len(results):
                            selected_scheme = results[selection]
                            return selected_scheme['scheme_code'], selected_scheme['scheme_name']
                    except ValueError:
                        print("❌ Invalid selection")
                else:
                    print("❌ No schemes found matching your search")
        
        elif choice == "2":
            # Category browser
            categories = fetcher.get_popular_schemes_by_category()
            
            print("\n📊 Popular Funds by Category:")
            print("-" * 80)
            
            category_map = {
                '1': 'large_cap',
                '2': 'mid_cap', 
                '3': 'small_cap',
                '4': 'elss',
                '5': 'index',
                '6': 'debt',
                '7': 'hybrid'
            }
            
            print("1. 🏢 Large Cap Funds")
            print("2. 🏭 Mid Cap Funds") 
            print("3. 🏪 Small Cap Funds")
            print("4. 💰 ELSS/Tax Saver Funds")
            print("5. 📈 Index Funds")
            print("6. 🏛️  Debt Funds")
            print("7. ⚖️  Hybrid Funds")
            
            cat_choice = input("\nSelect category (1-7): ").strip()
            
            if cat_choice in category_map:
                category_schemes = categories[category_map[cat_choice]]
                
                if category_schemes:
                    print(f"\n📊 {category_map[cat_choice].replace('_', ' ').title()} Funds:")
                    print("-" * 80)
                    
                    for i, scheme in enumerate(category_schemes, 1):
                        print(f"{i}. {scheme['scheme_name'][:60]}")
                        print(f"   AMC: {scheme['amc_name']}")
                        print(f"   Code: {scheme['scheme_code']} | NAV: ₹{scheme['nav']}")
                        print()
                    
                    try:
                        selection = int(input(f"Select fund (1-{len(category_schemes)}): ")) - 1
                        if 0 <= selection < len(category_schemes):
                            selected_scheme = category_schemes[selection]
                            return selected_scheme['scheme_code'], selected_scheme['scheme_name']
                    except ValueError:
                        print("❌ Invalid selection")
                else:
                    print("❌ No funds found in this category")
        
        elif choice == "3":
            # Direct scheme code entry
            scheme_code = input("\n🔢 Enter AMFI scheme code: ").strip()
            if scheme_code.isdigit():
                is_valid, scheme_info = fetcher.validate_scheme_code(scheme_code)
                if is_valid:
                    print(f"✅ Found: {scheme_info['scheme_name']}")
                    print(f"AMC: {scheme_info['amc_name']}")
                    confirm = input("Proceed with this fund? (Y/N): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        return scheme_code, scheme_info['scheme_name']
                else:
                    print("❌ Invalid scheme code. Please check AMFI website.")
            else:
                print("❌ Please enter a valid numeric scheme code")
        
        elif choice == "4":
            return None, None
        
        else:
            print("❌ Invalid choice. Please select 1-4.")

# Integration function to use with existing analyzer
def get_amfi_fund_choice():
    """Get fund choice using AMFI data"""
    print("🚀 Welcome to AMFI-Integrated Mutual Fund Analyzer!")
    print("📊 This tool uses real-time data directly from AMFI website")
    
    scheme_code, scheme_name = display_amfi_fund_selector()
    
    if scheme_code:
        print(f"\n✅ Selected Fund: {scheme_name}")
        print(f"🔢 AMFI Scheme Code: {scheme_code}")
        return scheme_code, scheme_name
    else:
        print("\n👋 No fund selected. Exiting...")
        return None, None

if __name__ == "__main__":
    # Test the AMFI integration
    scheme_code, scheme_name = get_amfi_fund_choice()
    
    if scheme_code:
        print(f"\n🎯 Ready to analyze:")
        print(f"Fund: {scheme_name}")
        print(f"AMFI Code: {scheme_code}")
        
        # Here you would integrate with the existing analyzer
        print("\n💡 Next: Integrate this with MutualFundAnalyzer class")
    else:
        print("No analysis performed.")
