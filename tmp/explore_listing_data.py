import httpx
import asyncio
import json

async def get_full_item_details():
    token = "PzJscAOAJKspsQFlsvQTDChKjbnaWypCetHnoyGK"
    # I'll use one of the IDs from the previous fetch (e.g. 272230531)
    listing_id = 272230531
    headers = {
        "User-Agent": "WysiWygTool/1.0",
        "Authorization": f"Discogs token={token}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Fetch full Marketplace Listing
            listing_resp = await client.get(f"https://api.discogs.com/marketplace/listings/{listing_id}", headers=headers)
            if listing_resp.status_code == 200:
                listing_data = listing_resp.json()
                print("--- Marketplace Listing Details ---")
                print(json.dumps(listing_data, indent=2))
                
                # 2. Fetch the associated Release
                release_id = listing_data.get('release', {}).get('id')
                if release_id:
                    release_resp = await client.get(f"https://api.discogs.com/releases/{release_id}", headers=headers)
                    if release_resp.status_code == 200:
                        release_data = release_resp.json()
                        print("\n--- Associated Release Details (Sample) ---")
                        # Only show a sample of keys since releases are huge
                        sample_release = {k: release_data[k] for k in ["identifiers", "styles", "genres", "year", "tracklist", "notes"] if k in release_data}
                        print(json.dumps(sample_release, indent=2))
            else:
                print(f"Listing Error: {listing_resp.status_code} - {listing_resp.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(get_full_item_details())
