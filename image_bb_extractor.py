from base_image_extractor import *

"""
Meant to extract images from Image BB IL, user should be public
"""

IMAGE_SOURCE_EXTRACT_REGEX = r"img src=\"(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))?\""


# re.search(IMAGE_NAMES_EXTRACT, ex).group(1)


class ImageBBExtractor(BaseImageExtractor):
    def __init__(self, url):
        super().__init__(url)

    def get_image_urls(self):
        return [url_tuple[0] for url_tuple in [urls for urls in re.findall(IMAGE_SOURCE_EXTRACT_REGEX, self.get_images_server_content())]]

    def get_image_names(self, urls):
        return [re.search(IMAGE_NAMES_EXTRACT_REGEX, url).group(1)[1:] for url in urls]
