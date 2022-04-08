import io
import json
from PIL import Image
from pathlib import Path
from random import randint
from subprocess import Popen, PIPE
from re import search

from consts import *

GIF_SIMPLE_REGEX = fr"(.*).{GIF_EXTENSION}"

class ImageExtractor:
    def __init__(self, images_path, images_url_base):
        self.images_path = images_path
        self.categories_metadata = {"cursor": "dummy", "tags": []}
        self.images_metadata = {"cursor": "dummy", "gfycats": []}
        self.images_url_base = images_url_base
        self.images = []
        self.image_names = []

        self.init_metadata()

    def init_metadata(self):
        # This requires for every image to have a tags file
        files_without_extension = [search(GIF_SIMPLE_REGEX, file).group(1) for file in Popen(f"find . -type f -name *.{GIF_EXTENSION}".split(" "), stdout=PIPE).communicate()[0].decode().split("\n") if file]
        self.images = dict(zip(
            [f"{file}.{GIF_EXTENSION}" for file in files_without_extension],
            [json.load(open(tag_file)) if tag_file else [] for tag_file in [f"{file}.{TAGS_EXTENSION}" for file in files_without_extension]]
        ))

        self.image_names = ['/'.join(path.split("/")[-2:]) for path in self.images.keys()]
        self.images_metadata["found"] = len(self.images)

        for id, (image_name, image_path) in enumerate(zip(self.image_names, self.images.keys())):
            if not image_path: continue
            image_url = f"{self.images_url_base}/{image_name}"
            file_data = ImageExtractor.get_image_file_data(image_path)
            gfycat = {
                "max5mbGif": image_url,
                "max2mbGif": image_url,
                "rating": "R",
                "description": "",
                "webpUrl": image_url,
                "source": 1,
                "title": image_name.split("/")[-1],
                "domainWhitelist": [],
                "gatekeeper": 0,
                "hasTransparency": False,
                "frameRate": float(file_data["fps"]),
                "posterUrl": image_url,
                "sitename": "",
                "mobilePosterUrl": image_url,
                "webmSize": file_data["size"],
                "mobileUrl": image_url,
                "gfyName": image_name.split("/")[-1],
                "views": 0,
                "likes": 0,
                "height": file_data["height"],
                "createDate": 0,
                "webmUrl": image_url,
                "hasAudio": False,
                "extraLemmas": "",
                "nsfw": "0",
                "languageText2": "",
                "avgColor": '#%02X%02X%02X' % (self.random_color(), self.random_color(), self.random_color()),
                "dislikes": 0,
                "published": 1,
                "miniUrl": image_url,
                "gif100px": image_url,
                "userName": "anonymous",
                "thumb100PosterUrl": image_url,
                "max1mbGif": image_url,
                "gfyId": id,
                "tags": self.images[image_path],
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
                    "mobile": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    }
                }
            }
            self.images_metadata["gfycats"].append(gfycat)
            for tag in self.images[image_path]:
                if not next((item for item in self.categories_metadata["tags"] if item and item["tag"] == tag), None):
                    self.categories_metadata["tags"].append({"cursor" : "dummy", "gfycats" : [gfycat] , "tag" : tag , "tagText": tag})
                    break
    
    def search_gifs(self, search_text):
        return {"cursor": "dummy", "gfycats": [gfycat for gfycat in self.images_metadata["gfycats"] if any(search_text in text for text in gfycat["tags"]) or search_text in gfycat["title"]]}

    @staticmethod
    def get_image_file_data(image_path):
        image_fp = open(image_path, "rb")
        image_bytes = image_fp.read()
        image_size_bytes = len(image_bytes)
        image_object = Image.open(io.BytesIO(image_bytes))
        frames, fps = ImageExtractor.get_avg_fps_and_frames(image_object)
        width = image_object.width
        height = image_object.height

        del image_fp
        del image_object

        return {"size": image_size_bytes, "width": width, "height": height, "fps": fps, "frames": frames}

    @staticmethod
    def random_color():
        return randint(0,255)

    @staticmethod
    def get_avg_fps_and_frames(image_object):
        image_object.seek(0)
        frames = duration = 0
        while True:
            try:
                frames += 1
                duration += image_object.info['duration']
                image_object.seek(image_object.tell() + 1)
            except Exception:
                try:
                    return frames, frames / duration * 1000
                except ZeroDivisionError:
                    return frames, 0