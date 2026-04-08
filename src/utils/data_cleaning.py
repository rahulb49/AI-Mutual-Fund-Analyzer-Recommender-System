"""
Data Cleaning Module for NAV Data
- Remove zero/negative/invalid NAVs
- Detect and handle outliers using statistical methods
- Provide detailed cleaning reports
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CleaningReport:
    """Report of cleaning operations performed"""
    original_count: int
    final_count: int
    removed_count: int
    removed_zero_nav: int
    removed_negative_nav: int
    removed_null_nav: int
    removed_outliers_iqr: int
    removed_outliers_zscore: int
    outlier_method_used: str
    removed_invalid_dates: int
    removed_empty_schemes: int
    
    @property
    def removal_percentage(self) -> float:
        """Calculate percentage of records removed"""
        if self.original_count == 0:
            return 0.0
        return (self.removed_count / self.original_count) * 100
    
    def print_report(self):
        """Print detailed cleaning report"""
        print(f"\n{'='*70}")
        print(f"DATA CLEANING REPORT")
        print(f"{'='*70}")
        print(f"Original records:          {self.original_count:>10,}")
        print(f"Final records:             {self.final_count:>10,}")
        print(f"Total removed:             {self.removed_count:>10,} ({self.removal_percentage:.2f}%)")
        print(f"{'-'*70}")
        print(f"Removed zero NAVs:         {self.removed_zero_nav:>10,}")
        print(f"Removed negative NAVs:     {self.removed_negative_nav:>10,}")
        print(f"Removed null NAVs:         {self.removed_null_nav:>10,}")
        print(f"Removed invalid dates:     {self.removed_invalid_dates:>10,}")
        print(f"Removed empty schemes:     {self.removed_empty_schemes:>10,}")
        print(f"Removed outliers ({self.outlier_method_used}):  {(self.removed_outliers_iqr + self.removed_outliers_zscore):>10,}")
        print(f"  - IQR method:            {self.removed_outliers_iqr:>10,}")
        print(f"  - Z-score method:        {self.removed_outliers_zscore:>10,}")
        print(f"{'='*70}\n")


def remove_zero_and_invalid_navs(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Remove records with zero, negative, or null NAV values.
    
    Args:
        df: DataFrame with NAV data
        
    Returns:
        Tuple of (cleaned_df, removal_counts)
    """
    removal_counts = {
        'zero_nav': 0,
        'negative_nav': 0,
        'null_nav': 0,
        'non_numeric_nav': 0
    }
    
    initial_count = len(df)
    
    # Convert NAV to numeric, coerce invalid values to NaN
    df['net_asset_value'] = pd.to_numeric(df['net_asset_value'], errors='coerce')
    
    # Count null NAVs
    removal_counts['null_nav'] = df['net_asset_value'].isna().sum()
    
    # Remove null NAVs
    df = df[df['net_asset_value'].notna()].copy()
    
    # Count and remove zero NAVs
    removal_counts['zero_nav'] = (df['net_asset_value'] == 0).sum()
    df = df[df['net_asset_value'] != 0].copy()
    
    # Count and remove negative NAVs
    removal_counts['negative_nav'] = (df['net_asset_value'] < 0).sum()
    df = df[df['net_asset_value'] > 0].copy()
    
    removed_total = sum(removal_counts.values())
    
    print(f"\n✓ Removed invalid NAVs:")
    print(f"  - Zero NAVs: {removal_counts['zero_nav']:,}")
    print(f"  - Negative NAVs: {removal_counts['negative_nav']:,}")
    print(f"  - Null/Missing NAVs: {removal_counts['null_nav']:,}")
    print(f"  - Total removed: {removed_total:,} ({(removed_total/initial_count)*100:.2f}%)")
    
    return df.reset_index(drop=True), removal_counts


def detect_outliers_iqr(df: pd.DataFrame, column: str = 'net_asset_value', 
                        iqr_multiplier: float = 1.5) -> pd.DataFrame:
    """
    Detect outliers using Interquartile Range (IQR) method.
    
    More robust for skewed distributions.
    
    Args:
        df: DataFrame with data
        column: Column to analyze
        iqr_multiplier: Multiplier for IQR (default 1.5 is standard)
        
    Returns:
        Boolean Series indicating outliers (True = outlier)
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - iqr_multiplier * IQR
    upper_bound = Q3 + iqr_multiplier * IQR
    
    outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
    
    return outliers, lower_bound, upper_bound


def detect_outliers_zscore(df: pd.DataFrame, column: str = 'net_asset_value',
                           threshold: float = 3.0) -> Tuple[pd.Series, float]:
    """
    Detect outliers using Z-score method.
    
    Good for normally distributed data.
    
    Args:
        df: DataFrame with data
        column: Column to analyze
        threshold: Z-score threshold (default 3.0 = ~99.7% data)
        
    Returns:
        Tuple of (Boolean Series for outliers, mean, std)
    """
    mean = df[column].mean()
    std = df[column].std()
    
    if std == 0:
        return pd.Series([False] * len(df)), mean, std
    
    z_scores = np.abs((df[column] - mean) / std)
    outliers = z_scores > threshold
    
    return outliers, mean, std


def handle_outliers(df: pd.DataFrame, method: str = 'iqr', 
                   remove: bool = True, cap: bool = False) -> Tuple[pd.DataFrame, Dict]:
    """
    Detect and handle outliers in NAV data.
    
    Args:
        df: DataFrame with NAV data
        method: 'iqr' (default) or 'zscore'
        remove: If True, remove outliers; if False, keep them
        cap: If True, cap outliers to boundary values (only if remove=False)
        
    Returns:
        Tuple of (cleaned_df, outlier_stats)
    """
    initial_count = len(df)
    stats = {
        'method': method,
        'outliers_found': 0,
        'outliers_removed': 0,
        'outliers_capped': 0,
        'bounds': {}
    }
    
    if method.lower() == 'iqr':
        outliers, lower_bound, upper_bound = detect_outliers_iqr(df)
        stats['bounds'] = {
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'Q1': float(df['net_asset_value'].quantile(0.25)),
            'Q3': float(df['net_asset_value'].quantile(0.75)),
            'IQR': float(df['net_asset_value'].quantile(0.75) - df['net_asset_value'].quantile(0.25))
        }
    elif method.lower() == 'zscore':
        outliers, mean, std = detect_outliers_zscore(df)
        stats['bounds'] = {
            'mean': float(mean),
            'std': float(std),
            'threshold': 3.0
        }
    else:
        raise ValueError(f"Unknown method: {method}")
    
    stats['outliers_found'] = outliers.sum()
    
    if remove:
        df = df[~outliers].copy()
        stats['outliers_removed'] = outliers.sum()
        print(f"\n✓ Removed {stats['outliers_removed']:,} outliers using {method.upper()} method")
    elif cap and method.lower() == 'iqr':
        _, lower_bound, upper_bound = detect_outliers_iqr(df)
        df_capped = df.copy()
        capped_count = 0
        
        below_lower = df_capped['net_asset_value'] < lower_bound
        above_upper = df_capped['net_asset_value'] > upper_bound
        
        df_capped.loc[below_lower, 'net_asset_value'] = lower_bound
        df_capped.loc[above_upper, 'net_asset_value'] = upper_bound
        
        capped_count = (below_lower | above_upper).sum()
        stats['outliers_capped'] = capped_count
        
        print(f"\n✓ Capped {capped_count:,} outliers to boundaries using IQR method")
        df = df_capped
    
    return df.reset_index(drop=True), stats


def remove_invalid_dates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Remove records with null or invalid dates.
    
    Args:
        df: DataFrame with date column
        
    Returns:
        Tuple of (cleaned_df, removed_count)
    """
    initial_count = len(df)
    
    # Handle date column - convert to datetime if not already
    if df['date'].dtype == 'object':
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    removed_count = df['date'].isna().sum()
    df = df[df['date'].notna()].copy()
    
    if removed_count > 0:
        print(f"✓ Removed {removed_count:,} records with invalid dates")
    
    return df.reset_index(drop=True), removed_count


def remove_empty_scheme_names(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Remove records with empty or whitespace-only scheme names.
    
    Args:
        df: DataFrame with scheme_name column
        
    Returns:
        Tuple of (cleaned_df, removed_count)
    """
    initial_count = len(df)
    
    # Remove null or whitespace-only scheme names
    df = df[df['scheme_name'].fillna('').str.strip() != ''].copy()
    
    removed_count = initial_count - len(df)
    
    if removed_count > 0:
        print(f"✓ Removed {removed_count:,} records with empty scheme names")
    
    return df.reset_index(drop=True), removed_count


def clean_nav_data(df: pd.DataFrame, outlier_method: str = 'iqr',
                   remove_outliers: bool = True,
                   cap_outliers: bool = False,
                   verbose: bool = True) -> Tuple[pd.DataFrame, CleaningReport]:
    """
    Comprehensive NAV data cleaning pipeline.
    
    Steps:
    1. Remove records with invalid/zero/negative NAVs
    2. Remove records with invalid dates
    3. Remove records with empty scheme names
    4. Detect and handle outliers
    
    Args:
        df: Input DataFrame with NAV data
        outlier_method: 'iqr' or 'zscore'
        remove_outliers: If True, remove outliers; else keep them
        cap_outliers: If True, cap outliers to boundaries
        verbose: If True, print detailed reports
        
    Returns:
        Tuple of (cleaned_df, CleaningReport)
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"STARTING DATA CLEANING PIPELINE")
        print(f"{'='*70}")
    
    df = df.copy()
    original_count = len(df)
    
    # Step 1: Remove invalid NAVs
    df, invalid_nav_counts = remove_zero_and_invalid_navs(df)
    
    # Step 2: Remove invalid dates
    df, removed_dates = remove_invalid_dates(df)
    
    # Step 3: Remove empty scheme names
    df, removed_schemes = remove_empty_scheme_names(df)
    
    # Step 4: Handle outliers
    df, outlier_stats = handle_outliers(
        df, 
        method=outlier_method,
        remove=remove_outliers,
        cap=cap_outliers
    )
    
    # Create report
    report = CleaningReport(
        original_count=original_count,
        final_count=len(df),
        removed_count=original_count - len(df),
        removed_zero_nav=invalid_nav_counts['zero_nav'],
        removed_negative_nav=invalid_nav_counts['negative_nav'],
        removed_null_nav=invalid_nav_counts['null_nav'],
        removed_outliers_iqr=outlier_stats.get('outliers_removed', 0) if outlier_stats['method'] == 'iqr' else 0,
        removed_outliers_zscore=outlier_stats.get('outliers_removed', 0) if outlier_stats['method'] == 'zscore' else 0,
        outlier_method_used=outlier_stats['method'].upper(),
        removed_invalid_dates=removed_dates,
        removed_empty_schemes=removed_schemes
    )
    
    if verbose:
        report.print_report()
    
    return df, report


def get_data_quality_stats(df: pd.DataFrame) -> Dict:
    """
    Compute data quality statistics.
    
    Args:
        df: DataFrame with NAV data
        
    Returns:
        Dictionary with quality metrics
    """
    stats = {
        'total_records': len(df),
        'unique_schemes': df['scheme_code'].nunique(),
        'unique_fund_houses': df['fund_house'].nunique() if 'fund_house' in df.columns else 0,
        'date_range': {
            'earliest': str(df['date'].min()),
            'latest': str(df['date'].max())
        },
        'nav_statistics': {
            'min': float(df['net_asset_value'].min()),
            'max': float(df['net_asset_value'].max()),
            'mean': float(df['net_asset_value'].mean()),
            'median': float(df['net_asset_value'].median()),
            'std': float(df['net_asset_value'].std()),
            'q1': float(df['net_asset_value'].quantile(0.25)),
            'q3': float(df['net_asset_value'].quantile(0.75))
        },
        'null_counts': {
            'scheme_code': df['scheme_code'].isna().sum(),
            'net_asset_value': df['net_asset_value'].isna().sum(),
            'date': df['date'].isna().sum(),
            'scheme_name': df['scheme_name'].isna().sum(),
            'fund_house': df['fund_house'].isna().sum() if 'fund_house' in df.columns else 0
        }
    }
    return stats


def print_data_quality_stats(stats: Dict):
    """Print data quality statistics in formatted report."""
    print(f"\n{'='*70}")
    print(f"DATA QUALITY STATISTICS")
    print(f"{'='*70}")
    print(f"Total records:             {stats['total_records']:>10,}")
    print(f"Unique schemes:            {stats['unique_schemes']:>10,}")
    print(f"Unique fund houses:        {stats['unique_fund_houses']:>10,}")
    print(f"{'-'*70}")
    print(f"Date Range:")
    print(f"  Earliest:                {stats['date_range']['earliest']}")
    print(f"  Latest:                  {stats['date_range']['latest']}")
    print(f"{'-'*70}")
    print(f"NAV Statistics:")
    print(f"  Min:                     ₹{stats['nav_statistics']['min']:>15,.4f}")
    print(f"  Max:                     ₹{stats['nav_statistics']['max']:>15,.4f}")
    print(f"  Mean:                    ₹{stats['nav_statistics']['mean']:>15,.4f}")
    print(f"  Median:                  ₹{stats['nav_statistics']['median']:>15,.4f}")
    print(f"  Std Dev:                 ₹{stats['nav_statistics']['std']:>15,.4f}")
    print(f"  Q1 (25%):                ₹{stats['nav_statistics']['q1']:>15,.4f}")
    print(f"  Q3 (75%):                ₹{stats['nav_statistics']['q3']:>15,.4f}")
    print(f"{'-'*70}")
    print(f"Null/Missing Values:")
    for col, count in stats['null_counts'].items():
        if count > 0:
            print(f"  {col}: {count:,} ({(count/stats['total_records'])*100:.2f}%)")
    print(f"{'='*70}\n")
