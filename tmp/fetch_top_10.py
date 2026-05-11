import httpx
import asyncio
import json

async def fetch_top_10():
    token = "PzJscAOAJKspsQFlsvQTDChKjbnaWypCetHnoyGK"
    username = "foreveryoungrecords"
    headers = {
        "User-Agent": "WysiWygTool/1.0",
        "Authorization": f"Discogs token={token}"
    }
    
    # We'll fetch more than 10 just to have a buffer, but take first 10
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"https://api.discogs.com/users/{username}/inventory?per_page=10", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                listings = data.get('listings', [])
                top_10 = []
                for l in listings[:10]:
                    release = l.get('release', {})
                    top_10.append({
                        "id": l.get('id'),
                        "title": release.get('title'),
                        "artist": release.get('artist'),
                        "format": release.get('format'),
                        "label": release.get('label'),
                        "status": l.get('status'),
                        "price": f"{l.get('price', {}).get('currency')} {l.get('price', {}).get('value')}",
                        "condition": l.get('condition'),
                        "sleeve_condition": l.get('sleeve_condition'),
                        "location": l.get('location'),
                        "comments": l.get('comments')
                    })
                
                with open(r"c:\Git\Forever_Tools\WysiWyg - release\tmp\discogs_top_10.json", 'w') as f:
                    json.dump(top_10, f, indent=4)
                
                print(json.dumps(top_10, indent=2))
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_top_10())
