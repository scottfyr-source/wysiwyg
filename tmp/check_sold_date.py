import httpx
import asyncio
import json

async def check_sold_details():
    token = "PzJscAOAJKspsQFlsvQTDChKjbnaWypCetHnoyGK"
    username = "foreveryoungrecords"
    headers = {
        "User-Agent": "WysiWygTool/1.0",
        "Authorization": f"Discogs token={token}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Search for sold items in inventory
            resp = await client.get(f"https://api.discogs.com/users/{username}/inventory?status=Sold&per_page=5", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                listings = data.get('listings', [])
                if listings:
                    print("Found Sold Listing Details:")
                    print(json.dumps(listings[0], indent=2))
                    
                    # Also try to check if there are any orders
                    order_resp = await client.get("https://api.discogs.com/marketplace/orders?status=All&per_page=1", headers=headers)
                    if order_resp.status_code == 200:
                        print("\nSample Order Detail:")
                        print(json.dumps(order_resp.json().get('orders', [{}])[0], indent=2))
                    else:
                        print(f"\nOrder API Error: {order_resp.status_code} - {order_resp.text}")
                else:
                    print("No sold items found in first 5 results.")
            else:
                print(f"Inventory Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(check_sold_details())
