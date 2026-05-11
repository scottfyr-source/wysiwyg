import httpx
import asyncio
import json

async def get_discogs_identity():
    token = "PzJscAOAJKspsQFlsvQTDChKjbnaWypCetHnoyGK"
    headers = {
        "User-Agent": "WysiWygTool/1.0",
        "Authorization": f"Discogs token={token}"
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("https://api.discogs.com/oauth/identity", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                print(json.dumps(data, indent=2))
                return data.get("username")
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Exception: {e}")
    return None

if __name__ == "__main__":
    asyncio.run(get_discogs_identity())
