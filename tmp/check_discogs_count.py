import httpx
import asyncio
import json

async def check_inventory_count():
    token = "PzJscAOAJKspsQFlsvQTDChKjbnaWypCetHnoyGK"
    username = "foreveryoungrecords"
    headers = {
        "User-Agent": "WysiWygTool/1.0",
        "Authorization": f"Discogs token={token}"
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"https://api.discogs.com/users/{username}/inventory", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                print(f"Total Items: {data.get('pagination', {}).get('items')}")
                print(f"Total Pages: {data.get('pagination', {}).get('pages')}")
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(check_inventory_count())
