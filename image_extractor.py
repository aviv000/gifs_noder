import re
import io
import random
import pathlib
import requests
from PIL import Image


"""
Meant to extract images from websites, probably from a user's profile
User should be public to extract
"""

IMAGE_NAMES_EXTRACT_REGEX = r"(/((\w)+(\-?))+)+\.(gif)"


class ImageExtractor:
    def __init__(self, images_path, images_url_base):
        self.images_path = images_path
        self.categories_metadata = {"cursor": "dummy", "gfycats": []}
        self.images_metadata = {"cursor": "dummy", "gfycats": []}
        self.images_url_base = images_url_base
        self.images = []
        self.image_names = []

        self.init_images_metadata()

    def init_images_metadata(self):
        self.images = [str(path) for path in pathlib.Path(self.images_path).resolve().glob("**/*") if re.match(IMAGE_NAMES_EXTRACT_REGEX , str(path))]
        self.image_names = [re.search(IMAGE_NAMES_EXTRACT_REGEX, path).group(1)[1:] for path in self.images]
        random_color = lambda: random.randint(0,255)
        self.images_metadata["found"] = len(self.images)

        for id, (image_name, image_path) in enumerate(zip(self.image_names, self.images)):
            image_url = f"{self.images_url_base}/{image_path.split('/')[-1]}"
            file_data = ImageExtractor.get_image_file_data(image_path)
            self.images_metadata["gfycats"].append({
                "max5mbGif": image_url,
                "max2mbGif": image_url,
                "rating": "R",
                "description": "",
                "webpUrl": image_url,
                "source": 1,
                "title": image_name,
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
                    "mobile": {
                        "url": image_url,
                        "size": file_data["size"],
                        "height": file_data["height"],
                        "width": file_data["width"]
                    }
                }
            })
    
    def filter_out_gifs(self, search):
        gifs_copy = self.images_metadata.copy()
        for index, gfycat in enumerate(self.images_metadata["gfycats"]):
            if search not in gfycat["title"]:
                gifs_copy["gfycats"].pop(index)
                gifs_copy["found"] -= 1
        return gifs_copy


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
    def get_avg_fps_and_frames(image_object):
        """ Returns the average framerate of a PIL Image object """
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