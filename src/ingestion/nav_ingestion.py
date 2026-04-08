import pandas as pd
import requests as req
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.schemas import NAVRecord, ParsedNAVData

# AMFI NAV data source & local file path to save the downloaded data
AMFI_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt"
Local_file_path = r"C:\Users\Asus TUF F15\Desktop\MSC DS\input"

def download_nav_data(url, file_path, timeout=100):
    """Download a file from a URL and save it to your computer."""

    response = req.get(url, timeout=timeout) #Send a request to the URL and get the response
    response.raise_for_status() # Step 2: Check if the request was successful
    with open(file_path, "wb") as file: # Step 3: Open a file on your computer in write mode ("wb" = write binary)
        file.write(response.content) # Step 4: Write the downloaded content to the file
    print(f"File downloaded successfully to {file_path}")


def is_header_or_section(line: str) -> bool:
    """Check if line is a section header or fund name (not a data row)"""
    line = line.strip()
    
    # Empty lines
    if not line:
        return True
    
    # Check if first field is numeric (data row) or text (header)
    if ';' in line:
        first_field = line.split(';')[0].strip()
        # Try to convert to int - if fails, it's likely a header
        try:
            int(first_field)
            return False  # It's a data row
        except ValueError:
            return True   # It's a header/section
    else:
        # Single column lines are headers/fund names
        return True


def parse_nav_row(row: str, current_fund: str = None) -> Optional[Dict]:
    """
    Parse a single NAV data row and return dict or None if invalid.
    
    Expected format: Scheme Code;ISIN Div Payout;ISIN Growth;Scheme Name;NAV;Date
    """
    row = row.strip()
    if not row or ';' not in row:
        return None
    
    try:
        fields = row.split(';')
        if len(fields) < 6:
            return None
        
        scheme_code = fields[0].strip()
        isin_div_payout = fields[1].strip()
        isin_growth = fields[2].strip()
        scheme_name = fields[3].strip()
        nav = fields[4].strip()
        date = fields[5].strip()
        
        # Skip if scheme code is not numeric
        int(scheme_code)
        
        # Convert empty/dash to None for optional ISIN fields
        isin_div_payout = None if not isin_div_payout or isin_div_payout == '-' else isin_div_payout
        isin_growth = None if not isin_growth or isin_growth == '-' else isin_growth
        
        return {
            'scheme_code': scheme_code,
            'isin_div_payout': isin_div_payout,
            'isin_growth': isin_growth,
            'scheme_name': scheme_name,
            'net_asset_value': nav,
            'date': date,
            'fund_house': current_fund
        }
    except (ValueError, IndexError):
        return None


def parse_nav_file(file_path: str) -> ParsedNAVData:
    """
    Parse AMFI NAV file with validation.
    
    Returns ParsedNAVData with records and error tracking.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    records: List[NAVRecord] = []
    errors: List[Dict] = []
    current_fund = None
    data_date = None
    line_num = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line_num += 1
                line = line.strip()
                
                # Skip empty lines and header
                if not line or line_num == 1:
                    continue
                
                # Check if it's a section/fund header
                if is_header_or_section(line):
                    # Update current fund name if it looks like a fund house name
                    if 'Mutual Fund' in line or 'Scheme' not in line:
                        if line != 'Open Ended Schemes(Debt Scheme - Banking and PSU Fund)':
                            current_fund = line
                    continue
                
                # Parse data row
                parsed_row = parse_nav_row(line, current_fund)
                if not parsed_row:
                    errors.append({
                        'line': line_num,
                        'row': line,
                        'error': 'Could not parse row'
                    })
                    continue
                
                # Validate using Pydantic
                try:
                    record = NAVRecord(**parsed_row)
                    records.append(record)
                    
                    # Track latest date
                    if data_date is None or record.date > data_date:
                        data_date = record.date
                        
                except ValueError as e:
                    errors.append({
                        'line': line_num,
                        'row': line,
                        'error': str(e)
                    })
    
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")
    
    return ParsedNAVData(
        records=records,
        total_records=len(records),
        data_date=data_date,
        errors=errors
    )


def fetch_nav_data(file_path):
    """
    Load the AMFI NAV file into a pandas DataFrame (table in memory).
    
    This now uses validation and returns clean structured data.
    """
    parsed_data = parse_nav_file(file_path)
    
    if parsed_data.errors:
        print(f"⚠️  Warning: {len(parsed_data.errors)} parsing errors encountered")
        for i, err in enumerate(parsed_data.errors[:5]):  # Show first 5 errors
            print(f"   Line {err['line']}: {err['error']}")
        if len(parsed_data.errors) > 5:
            print(f"   ... and {len(parsed_data.errors) - 5} more errors")
    
    # Convert to DataFrame for compatibility
    data_dicts = [record.dict() for record in parsed_data.records]
    df = pd.DataFrame(data_dicts)
    
    print(f"✓ Loaded {len(df)} valid NAV records")
    print(f"  Data date: {parsed_data.data_date.strftime('%d-%b-%Y') if parsed_data.data_date else 'Unknown'}")
    
    return df, parsed_data