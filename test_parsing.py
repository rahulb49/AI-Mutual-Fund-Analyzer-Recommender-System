"""
Test script to validate NAV data parsing and validation
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingestion.nav_ingestion import parse_nav_file, fetch_nav_data

# Test with actual file
nav_file = Path(__file__).parent / "input" / "NAVAll.txt"

print("=" * 60)
print("NAV Data Parsing & Validation Test")
print("=" * 60)
print()

# Parse with detailed validation
print("📊 Parsing NAV file with validation...")
print(f"   File: {nav_file}")
print()

try:
    parsed_data = parse_nav_file(str(nav_file))
    
    print(f"✓ Successfully parsed file!")
    print()
    print("📈 Summary:")
    print(f"   Total records: {parsed_data.total_records}")
    print(f"   Data date: {parsed_data.data_date.strftime('%d-%b-%Y') if parsed_data.data_date else 'N/A'}")
    print(f"   Parsing errors: {len(parsed_data.errors)}")
    print()
    
    # Show sample records
    print("📋 Sample Records (first 3):")
    print("-" * 60)
    for i, record in enumerate(parsed_data.records[:3], 1):
        print(f"\n{i}. {record.scheme_name}")
        print(f"   Scheme Code: {record.scheme_code}")
        print(f"   Fund House: {record.fund_house}")
        print(f"   NAV: ₹{record.net_asset_value:.4f}")
        print(f"   Date: {record.date.strftime('%d-%b-%Y')}")
    
    # Show fund house distribution
    print()
    print("\n📦 Fund House Distribution (top 5):")
    print("-" * 60)
    from collections import Counter
    fund_counts = Counter(r.fund_house for r in parsed_data.records if r.fund_house)
    for fund, count in fund_counts.most_common(5):
        print(f"   {fund}: {count} schemes")
    
    # Show NAV statistics
    print()
    print("\n💰 NAV Statistics:")
    print("-" * 60)
    navs = [r.net_asset_value for r in parsed_data.records]
    print(f"   Min NAV: ₹{min(navs):.4f}")
    print(f"   Max NAV: ₹{max(navs):.4f}")
    print(f"   Avg NAV: ₹{sum(navs)/len(navs):.4f}")
    
    # Show errors if any
    if parsed_data.errors:
        print()
        print("\n⚠️  Parsing Errors (first 5):")
        print("-" * 60)
        for err in parsed_data.errors[:5]:
            print(f"   Line {err['line']}: {err['error']}")
            print(f"      {err['row'][:60]}...")
    
    # Test pandas conversion
    print()
    print("\n🔄 Converting to Pandas DataFrame...")
    df, _ = fetch_nav_data(str(nav_file))
    print(f"✓ DataFrame created with {len(df)} rows and {len(df.columns)} columns")
    print()
    print(df.head(3).to_string())
    
    print()
    print("=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
