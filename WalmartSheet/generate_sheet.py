"""
Walmart Sheet Generator
Reads history JSON and outputs formatted CSV for Walmart ingestion.
"""
import json
import csv
import re
import os
from datetime import datetime

# Configuration
INPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'wysiwyg_history.json')
OUTPUT_FILE = 'walmart_upload.csv'

# Walmart Column Headers (based on EXAMPLE.TXT)
HEADERS = [
    "SKU", "Music", "Product ID Type", "Product ID", "Product Name", "Selling Price", 
    "Shipping Weight (lbs)", "Country of Origin - Substantial Transformation", "Fulfillment Center ID", 
    "Inventory Qty", "Site Description", "Pre Order", "Site Description", "Key Features (+)", 
    "Key Features 1 (+)", "Key Features 2 (+)", "Main Image URL", "Is Prop 65 Warning Required", 
    "Condition", "Has Written Warranty", "Is Collectible", "Unit", "Measure", 
    "Additional Image URL (+)", "Measure", "Unit", "Measure", "Unit", "Measure", "Unit", 
    "Measure", "Unit", "Autographed by (+)", "Awards Won (+)", "Brand Name", 
    "California Prop 65 Warning Text", "Certification Type", "Character (+)", "Character Group (+)", 
    "Children Product Certificate Document Reference ID", "Children Product Test Report Document Reference ID", 
    "Composer (+)", "Configuration", "Count Per Pack", "Digital Audio File Format (+)", "Measure", 
    "Unit", "Edition", "General Certificate of Conformity Document Reference ID", 
    "Has Parental Advisory Label", "Is Edited", "Is Enhanced", "Language", "Manufacturer Name", 
    "Manufacturer Part Number", "Media Format (+)", "Model Number", "Multipack Quantity", 
    "Music Genre (+)", "Music Media Format (+)", "Music Producer", "Music Release Type", 
    "Music Subgenre (+)", "Net Content Statement", "Number in Series", "Number of Discs", 
    "Number of Pieces", "Number of Tracks", "Occasion (+)", "Original Release Date", 
    "Parental Advisory Label URL (+)", "Performer (+)", "Record Label - Pick 1", "Series Title", 
    "Songwriter", "Sports League (+)", "Sports Team (+)", "Target Audience (+)", 
    "Third Party Accreditation Symbol on Product Package Code (+)", "Title", "Total Count", 
    "Track Duration", "Track Name", "Track Number", "Warranty Text", "Warranty URL", 
    "Variant Group ID", "Variant Attribute Names (+)", "Is Primary Variant", "Swatch Image URL", 
    "Swatch Variant Attribute", "ZIP Codes", "States", "State Restrictions Reason", 
    "Product is or Contains an Electronic Component?", 
    "Product is or Contains a Chemical, Aerosol or Pesticide?", 
    "Product is or Contains this Battery Type", "Fulfillment Lag Time", "Ships in Original Packaging", 
    "Must ship alone?", "Is Preorder", "Release Date", "Site Start Date", "Site End Date", 
    "External Product ID Type", "External Product ID", "Product Id Update", "SKU Update", 
    "MSRP", "Maximum Seller Allowed Price", "Minimum Seller Allowed Price", "Repricer Strategy", 
    "Product Package Weight (lbs)", "Product Package Dimensions Depth (in)", 
    "Product Package Dimensions Width (in)", "Product Package Dimensions Height (in)"
]

# Dimensions Mapping
DIMENSIONS = {
    'Cassette': {'w': 6, 'd': 1, 'h': 5, 'wt': 6, 'wt_unit': 'oz'}, # Note: Example has 6oz, 3in? Mapping 1,5,3 approx
    'CD':       {'w': 6, 'd': 1, 'h': 5, 'wt': 6, 'wt_unit': 'oz'},
    'DVD':      {'w': 6, 'd': 1, 'h': 8, 'wt': 6, 'wt_unit': 'oz'},
    'Blu-ray':  {'w': 6, 'd': 1, 'h': 7, 'wt': 6, 'wt_unit': 'oz'},
    'LP':       {'w': 12, 'd': 1, 'h': 12, 'wt': 2, 'wt_unit': 'lb'},
    'Vinyl':    {'w': 12, 'd': 1, 'h': 12, 'wt': 2, 'wt_unit': 'lb'},
    '7"':       {'w': 8, 'd': 1, 'h': 7, 'wt': 6, 'wt_unit': 'oz'},
}

def parse_raw_text(text):
    """Parses the Discogs raw text blob."""
    info = {
        'artist': '', 'title': '', 'label': '', 'cat': '', 
        'format': '', 'year': '', 'country': ''
    }
    
    lines = text.split('\n')
    if not lines:
        return info

    # Line 1: Artist - Title
    parts = lines[0].split(' - ', 1)
    if len(parts) == 2:
        info['artist'] = parts[0].strip()
        info['title'] = parts[1].strip()
    else:
        info['artist'] = lines[0].strip()

    for line in lines:
        if line.startswith('Label:'):
            # "Label: MCA Records MCAC-1607" -> Label: MCA Records, Cat: MCAC-1607
            clean = line.replace('Label:', '').strip()
            # Simple heuristic: Split by space, last item is cat#
            # Ideally split by " / " if multiple
            tokens = clean.split(' ')
            if len(tokens) > 1:
                info['cat'] = tokens[-1]
                info['label'] = " ".join(tokens[:-1]).strip()
            else:
                info['label'] = clean
        
        elif line.startswith('Format:'):
            info['format'] = line.replace('Format:', '').strip()
            
        elif line.startswith('Released:'):
            info['year'] = line.replace('Released:', '').strip()
            
        elif line.startswith('Country:'):
            info['country'] = line.replace('Country:', '').strip()
            
    return info

def map_media_format(raw_fmt):
    """Maps Discogs format to Walmart format and gets dimensions."""
    lower_fmt = raw_fmt.lower()
    
    media_type = "CD" # Default
    walmart_fmt = "CD"
    
    if "cassette" in lower_fmt:
        media_type = "Cassette"
        walmart_fmt = "Cassette Tape"
    elif "lp" in lower_fmt or "vinyl" in lower_fmt:
        media_type = "LP"
        walmart_fmt = "Vinyl"
    elif "dvd" in lower_fmt:
        media_type = "DVD"
        walmart_fmt = "DVD"
    elif "blu-ray" in lower_fmt:
        media_type = "Blu-ray"
        walmart_fmt = "Blu-ray"
    elif "7\"" in lower_fmt:
        media_type = '7"'
        walmart_fmt = "Vinyl" # Walmart usually calls 7 inch vinyl just Vinyl or Single
        
    return media_type, walmart_fmt

def process_item(item):
    parsed = parse_raw_text(item.get('raw_text', ''))
    
    # 1. Basic Info
    artist = parsed['artist']
    title = parsed['title']
    label = parsed['label']
    cat = parsed['cat']
    year = parsed['year']
    
    # 2. Media Logic
    media_key, media_fmt = map_media_format(parsed['format'])
    
    # Count detection (e.g., 2xLP)
    media_count = 1
    count_match = re.search(r'(\d+)x', parsed['format'])
    if count_match:
        media_count = int(count_match.group(1))
        
    media_desc = f"{media_count}x{media_fmt}" if media_count > 1 else media_fmt
    if media_fmt == "Cassette Tape": media_desc = "Audio Cassette" # Match example preference
    
    # 3. Product Name
    product_name = f"{artist} - {title} - {media_desc}"
    
    # 4. Site Description
    desc_extra = "Factory Sealed" # Static or needs input
    site_desc = f"{artist} - {title} - {media_desc} - {desc_extra} - {label} {cat}"
    
    # 5. Dimensions
    dims = DIMENSIONS.get(media_key, DIMENSIONS['CD'])
    
    # 6. Row Construction
    row = [''] * len(HEADERS)
    
    # Fill key columns
    row[HEADERS.index("Music")] = "Music"
    row[HEADERS.index("Product ID Type")] = "UPC"
    row[HEADERS.index("Product Name")] = product_name
    row[HEADERS.index("Shipping Weight (lbs)")] = "1"
    row[HEADERS.index("Country of Origin - Substantial Transformation")] = "United States"
    row[HEADERS.index("Fulfillment Center ID")] = "10001373153"
    row[HEADERS.index("Inventory Qty")] = "1"
    
    # Site Description (Handle both instances)
    for idx, h in enumerate(HEADERS):
        if h == "Site Description":
            row[idx] = site_desc

    row[HEADERS.index("Is Prop 65 Warning Required")] = "No"
    row[HEADERS.index("Condition")] = "New"
    row[HEADERS.index("Has Written Warranty")] = "No"
    row[HEADERS.index("Is Collectible")] = "Y"
    
    # Dimensions Columns (Indices based on header position logic)
    # 21: Unit=Each, 22: Measure=1
    row[21] = "Each"
    row[22] = "1"
    
    # 24/25: Depth
    row[24] = str(dims['d'])
    row[25] = "in"
    
    # 26/27: Width
    row[26] = str(dims['h']) # Note: height/width can be swapped depending on orientation
    row[27] = "in"
    
    # 28/29: Weight
    row[28] = str(dims['wt'])
    row[29] = dims['wt_unit']
    
    # 30/31: Height
    row[30] = str(dims['w'])
    row[31] = "in"

    row[HEADERS.index("Manufacturer Part Number")] = cat
    row[HEADERS.index("Media Format (+)")] = media_fmt
    row[HEADERS.index("Music Genre (+)")] = "Pop" # Placeholder
    row[HEADERS.index("Music Media Format (+)")] = media_fmt
    
    if len(year) == 4:
        row[HEADERS.index("Original Release Date")] = f"{year}-01-01"
    else:
        row[HEADERS.index("Original Release Date")] = year

    row[HEADERS.index("Performer (+)")] = artist
    row[HEADERS.index("Record Label - Pick 1")] = label
    row[HEADERS.index("Title")] = title
    row[HEADERS.index("Site Start Date")] = datetime.now().strftime("%Y-%m-%d")

    return row

def main():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_FILE}")
        return

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        for item in data:
            row = process_item(item)
            writer.writerow(row)
            
    print(f"Successfully generated {OUTPUT_FILE} with {len(data)} rows.")

if __name__ == "__main__":
    main()