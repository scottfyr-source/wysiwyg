import json
import os
import sys

class MediaFormatSearcher:
    def __init__(self, json_filename="media_formats.json"):
        # Determine path relative to this script
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.json_path = os.path.join(base_path, json_filename)
        self.format_map = {}
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.json_path):
            print(f"Error: {self.json_path} not found.")
            return

        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Build a case-insensitive reverse index for O(1) lookup
            for category, content in data.items():
                if isinstance(content, dict):
                    # Handle nested categories (e.g., physical_audio_analog -> vinyl_and_shellac)
                    for sub_category, formats in content.items():
                        for fmt in formats:
                            self.format_map[fmt.lower()] = f"{category} ({sub_category})"
                elif isinstance(content, list):
                    # Handle flat lists
                    for fmt in content:
                        self.format_map[fmt.lower()] = category
        except Exception as e:
            print(f"Error loading JSON: {e}")

    def search(self, format_name):
        # Returns the category or None if not found
        return self.format_map.get(format_name.strip().lower(), "Unknown Format")

if __name__ == "__main__":
    searcher = MediaFormatSearcher()

    # Example Usage
    print(f"8-Track Cartridge -> {searcher.search('8-Track Cartridge')}")
    print(f"MP3               -> {searcher.search('MP3')}")
    print(f"Vinyl             -> {searcher.search('Vinyl')}")