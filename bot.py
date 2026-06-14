async def fetch_tiktok_data(tiktok_url):
    api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY, 
        "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
    }
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(api_url, headers=headers, params={"url": tiktok_url, "hd": "1"}, timeout=25.0)
            json_res = res.json()
            
            # ဒီစာကြောင်းက API က ဘာပြန်ပြောလဲဆိုတာကို Logs မှာ ပြပေးမှာပါ
            logging.info(f"API Response: {json_res}")
            
            if json_res.get("code") == 0:
                return json_res.get("data")
            else:
                # API ဘက်က error message ကို logs မှာ မှတ်မယ်
                logging.error(f"API Error Message: {json_res.get('msg')}")
                return None
        except Exception as e:
            logging.error(f"Fetch Error: {e}")
            return None
