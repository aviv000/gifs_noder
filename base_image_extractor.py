import re
import io
import random
import requests
from PIL import Image


"""
Meant to extract images from websites, probably from a user's profile
User should be public to extract
"""

IMAGE_NAMES_EXTRACT_REGEX = r"(/((\w)+(\-?))+)+\.(gif)"


class BaseImageExtractor:
    def __init__(self, images_server_url):
        self.images_server_url = images_server_url
        self.categories_metadata = {"cursor": "dummy", "gfycats": []}
        self.images_metadata = {"cursor": "dummy", "gfycats": []}

        self.init_images_metadata()

    def init_images_metadata(self):
        image_urls = self.get_image_urls()
        random_color = lambda: random.randint(0,255)
        self.images_metadata["found"] = len(image_urls)

        image_names = self.get_image_names(image_urls)

        for id, (image_name, image_url) in enumerate(zip(image_names, image_urls)):
            file_data = BaseImageExtractor.get_image_file_data(image_url)
            self.images_metadata["gfycats"].append({
                "max5mbGif": image_url,
                "max2mbGif": image_url,
                "rating": "R",
                "description": "",
                "webpUrl": image_url,
                "source": 1,
                "title": "",
                "domainWhitelist": [],
                "gatekeeper": 0,
                "hasTransparency": False,
                "frameRate": float(file_data["fps"]),
                "posterUrl": image_url,
                "sitename": "",
                "mobilePosterUrl": image_url,
                "webmSize": file_data["size"],
                "mobileUrl": image_url,
                "gfyName": image_name,
                "views": 0,
                "likes": 0,
                "height": file_data["height"],
                "createDate": 1562142243,
                "webmUrl": image_url,
                "hasAudio": False,
                "extraLemmas": "",
                "nsfw": "0",
                "languageText2": "",
                "avgColor": '#%02X%02X%02X' % (random_color(),random_color(),random_color()),
                "dislikes": 0,
                "published": 1,
                "miniUrl": image_url,
                "gif100px": image_url,
                "userName": "anonymous",
                "thumb100PosterUrl": image_url,
                "max1mbGif": image_url,
                "gfyId": id,
                "tags": "",
                "gifUrl": image_url,
                "gfyNumber": id,
                "numFrames": file_data["frames"],
                "curated": 0,
                "miniPosterUrl": image_url,
                "width": file_data["width"],
                "mp4Size": file_data["size"],
                "languageCategories": "",
                "mp4Url": image_url,
                "content_urls": {
                    "largeGif": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "max2mbGif": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "webp": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "max1mbGif": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "100pxGif": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "mobilePoster": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "mp4": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "webm": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "max5mbGif": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "largeGif": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    },
                    "mobile": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    }
                }
            })

    def get_images_server_content(self):
        return requests.get(url=self.images_server_url).content.decode()

    @staticmethod
    def download_image(image_url):
        downloaded_image = requests.get(image_url, stream=True)
        downloaded_image.raw.decode_content = True
        return downloaded_image.content

    @staticmethod
    def get_image_file_data(image_url):
        image_bytes = BaseImageExtractor.download_image(image_url)
        image_size_bytes = len(image_bytes)
        image_obj = Image.open(io.BytesIO(image_bytes))
        frames, fps = BaseImageExtractor.get_avg_fps_and_frames(image_obj)
        width = image_obj.width
        height = image_obj.height

        del image_bytes
        del image_obj

        return {"size": image_size_bytes, "width": width, "height": height, "fps": fps, "frames": frames}

    @staticmethod
    def get_avg_fps_and_frames(PIL_Image_object):
        """ Returns the average framerate of a PIL Image object """
        PIL_Image_object.seek(0)
        frames = duration = 0
        while True:
            try:
                frames += 1
                duration += PIL_Image_object.info['duration']
                PIL_Image_object.seek(PIL_Image_object.tell() + 1)
            except Exception:
                try:
                    return frames, frames / duration * 1000
                except ZeroDivisionError:
                    return frames, 0

    def get_image_urls(self):
        pass

    def get_image_names(self, urls):
        pass
