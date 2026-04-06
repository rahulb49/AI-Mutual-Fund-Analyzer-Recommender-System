import pandas as pd
import requests as req

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


def fetch_nav_data(file_path):
    """Load the AMFI NAV file into a pandas DataFrame (table in memory)."""
    
    data = pd.read_csv(file_path, sep=';', skip_blank_lines=True) # AMFI NAV file is semicolon-delimited, skip blank lines
    data = data[pd.to_numeric(data['Scheme Code'], errors='coerce').notna()] # Remove rows where Scheme Code looks like a section header (non-numeric)
    return data.reset_index(drop=True) # Reset the index of the DataFrame after filtering out non-numeric Scheme Codes