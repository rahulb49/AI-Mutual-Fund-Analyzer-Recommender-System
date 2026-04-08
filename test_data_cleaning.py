"""
Test script for data cleaning module
Demonstrates:
- Removing zero/negative/null NAVs
- Detecting and handling outliers using IQR and Z-score methods
- Data quality reporting
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingestion.nav_ingestion import fetch_nav_data
from utils.data_cleaning import (
    clean_nav_data,
    get_data_quality_stats,
    print_data_quality_stats
)

# Load data
nav_file = Path(__file__).parent / "input" / "NAVAll.txt"

print("="*70)
print("DATA CLEANING TEST - NAV DATA")
print("="*70)

# Step 1: Load raw data
print("\n📥 Step 1: Loading raw data...")
df_raw, parsed_data = fetch_nav_data(str(nav_file))

# Show initial quality stats
print("\n📊 Initial Data Quality:")
raw_stats = get_data_quality_stats(df_raw)
print_data_quality_stats(raw_stats)

# Step 2: Clean data with IQR method
print("\n" + "="*70)
print("📋 Step 2: Cleaning with IQR Outlier Detection")
print("="*70)

df_cleaned_iqr, report_iqr = clean_nav_data(
    df_raw,
    outlier_method='iqr',
    remove_outliers=True,
    verbose=True
)

# Step 3: Show cleaned quality stats
print("\n📊 Post-Cleaning Data Quality (IQR method):")
cleaned_stats_iqr = get_data_quality_stats(df_cleaned_iqr)
print_data_quality_stats(cleaned_stats_iqr)

# Step 4: Compare before/after
print("\n" + "="*70)
print("📊 COMPARISON: Raw vs Cleaned (IQR)")
print("="*70)
print(f"Records removed:           {report_iqr.removed_count:>10,} ({report_iqr.removal_percentage:.2f}%)")
print(f"  - Zero NAVs:             {report_iqr.removed_zero_nav:>10,}")
print(f"  - Negative NAVs:         {report_iqr.removed_negative_nav:>10,}")
print(f"  - Null NAVs:             {report_iqr.removed_null_nav:>10,}")
print(f"  - Invalid dates:         {report_iqr.removed_invalid_dates:>10,}")
print(f"  - Empty schemes:         {report_iqr.removed_empty_schemes:>10,}")
print(f"  - Outliers (IQR):        {report_iqr.removed_outliers_iqr:>10,}")

print(f"\nNAV Range After Cleaning:")
print(f"  Before: ₹{raw_stats['nav_statistics']['min']:.4f} - ₹{raw_stats['nav_statistics']['max']:.4f}")
print(f"  After:  ₹{cleaned_stats_iqr['nav_statistics']['min']:.4f} - ₹{cleaned_stats_iqr['nav_statistics']['max']:.4f}")

# Step 5: Alternative - Z-score method
print("\n" + "="*70)
print("📋 Step 3: Cleaning with Z-Score Outlier Detection (Alternative)")
print("="*70)

df_cleaned_zscore, report_zscore = clean_nav_data(
    df_raw,
    outlier_method='zscore',
    remove_outliers=True,
    verbose=True
)

print(f"\n📊 Post-Cleaning Data Quality (Z-score method):")
cleaned_stats_zscore = get_data_quality_stats(df_cleaned_zscore)
print_data_quality_stats(cleaned_stats_zscore)

# Step 6: Show sample records from cleaned data
print("\n" + "="*70)
print("📋 Sample Records from Cleaned Data (IQR method)")
print("="*70)
print("\nTop 5 schemes by NAV (highest):")
print(df_cleaned_iqr.nlargest(5, 'net_asset_value')[['scheme_code', 'scheme_name', 'net_asset_value', 'fund_house']].to_string(index=False))

print("\n\nBottom 5 schemes by NAV (lowest):")
print(df_cleaned_iqr.nsmallest(5, 'net_asset_value')[['scheme_code', 'scheme_name', 'net_asset_value', 'fund_house']].to_string(index=False))

# Step 7: Show distribution by fund house in cleaned data
print("\n" + "="*70)
print("📦 Top 10 Fund Houses (Cleaned Data)")
print("="*70)
fund_dist = df_cleaned_iqr['fund_house'].value_counts().head(10)
for fund, count in fund_dist.items():
    pct = (count / len(df_cleaned_iqr)) * 100
    print(f"  {fund}: {count:,} ({pct:.1f}%)")

# Step 8: Comparison of methods
print("\n" + "="*70)
print("📊 METHOD COMPARISON")
print("="*70)
print(f"IQR Method:")
print(f"  Records after cleaning: {len(df_cleaned_iqr):,}")
print(f"  Outliers removed:       {report_iqr.removed_outliers_iqr:,}")
print(f"  Total removed:          {report_iqr.removed_count:,}")

print(f"\nZ-Score Method:")
print(f"  Records after cleaning: {len(df_cleaned_zscore):,}")
print(f"  Outliers removed:       {report_zscore.removed_outliers_zscore:,}")
print(f"  Total removed:          {report_zscore.removed_count:,}")

print(f"\nRecommendation: Use IQR method for skewed NAV distributions")

# Save cleaned data
output_file = Path(__file__).parent / "data" / "cleaned_nav_data.csv"
output_file.parent.mkdir(exist_ok=True)
df_cleaned_iqr.to_csv(output_file, index=False)
print(f"\n✓ Cleaned data saved to: {output_file}")

print("\n" + "="*70)
print("✓ DATA CLEANING COMPLETE")
print("="*70)
