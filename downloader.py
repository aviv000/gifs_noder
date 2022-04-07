from nis import cat
import requests
import json
import pathlib
import time

class GifsDownloader:
    def __init__(self, gifs_per_category : int) -> None:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = '{"client_id":"2_pF2lsA", "client_secret": "eoGH15vw3ziUHH4uQTrXXggfOYCHvfzV07rvjhE0GS8tsAJkGmTm9t8Pk25-5bDH", "grant_type": "client_credentials"}'

        response = requests.post('https://api.gfycat.com/v1/oauth/token', headers=headers, data=data)
        if response.status_code != 200:
            raise Exception("Server error")
        self.access_token = response.json()["access_token"]
        self.gifs_per_category = gifs_per_category
        self.header = {
            'Authorization': f'Bearer {self.access_token}',
        }

    def download_gifs(self):
        response = requests.get("https://api.gfycat.com/v1/reactions/populated", headers=self.header)
        categories = (tag["tag"] for tag in response.json()["tags"])
        params = {
            'gfyCount': str(self.gifs_per_category),
            'tagName' : ""
        }
        pathlib.Path("categories").mkdir(parents=True, exist_ok=True)
        for category in categories:
            pathlib.Path(f"categories/{category}").mkdir(parents=True, exist_ok=True)
            params["tagName"] = category
            response = requests.get('https://api.gfycat.com/v1/reactions/populated',
                                    headers=self.header, params=params)
            for gif_data in response.json()["gfycats"]:
                gif_url = gif_data["content_urls"]["largeGif"]["url"] if "largeGif" in  gif_data["content_urls"] and "url" in gif_data["content_urls"]["largeGif"] else gif_data["gifUrl"]
                response = requests.get(gif_url, allow_redirects=True)
                if response.status_code == 200:
                    with open(f"categories/{category}/{gif_data['gfyName']}.gif", "wb") as gif_file:
                        gif_file.write(response.content)
                    with open(f"categories/{category}/{gif_data['gfyName']}.tags", "w") as tags_file:
                        tags_file.write(json.dumps(gif_data["tags"]))
                else:
                    print(category)
                    with open("error_gifs", "a+") as error_files:
                        error_files.write(f"{gif_url}\n")
            time.sleep(0.3)
            # print(json.dumps(response.json(), indent=4))

def main():
    downloader = GifsDownloader(gifs_per_category=256)
    downloader.download_gifs()

if __name__ == "__main__":
    main()