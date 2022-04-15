import io
import json
from PIL import Image
from re import search
from pathlib import Path
from random import randint
from subprocess import Popen, PIPE
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sqlalchemy.ext.declarative as sqldcl
from sqlalchemy import Column, Integer, MetaData, VARCHAR, literal
from consts import *

GIF_SIMPLE_REGEX = fr"(.*).{GIF_EXTENSION}"

engine = create_engine(f'sqlite:///{DATABASE_FILE}', echo=True)
Base = sqldcl.declarative_base()

class Images(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    image_path = Column(VARCHAR)
    image_name = Column(VARCHAR)
    image_title = Column(VARCHAR)
    json_dump = Column(VARCHAR)
    tag_names = Column(VARCHAR)


    def __repr__(self):
        return "<Image(image_path='%s', image_name='%s', image_title='%s', json_dump='%s', tag_names='%s')>" % (self.image_path, self.image_name, self.image_title, self.json_dump, self.tag_names)


class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    tag_name = Column(VARCHAR)
    json_dump = Column(VARCHAR)

    def __repr__(self):
        return "<Tag(tag_name='%s', json_dump='%s')>" % (self.tag_name, self.json_dump)

Base.metadata.create_all(engine)

images_table = Base.metadata.tables['images']
session_maker = sessionmaker(bind=engine)

session = session_maker()

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
            if session.query(Images).filter_by(image_path=image_path).first(): continue
            if not image_path: continue
            image_url = f"{self.images_url_base}/{image_name}"
            file_data = ImageExtractor.get_image_file_data(image_path)
            title = image_name.split("/")[-1]
            gfycat = {
                "max5mbGif": image_url,
                "max2mbGif": image_url,
                "rating": "R",
                "description": "",
                "webpUrl": image_url,
                "source": 1,
                "title": title,
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
                }
            }
            session.add(Images(image_path=image_path, image_name=image_name, image_title=title ,json_dump=json.dumps(gfycat), tag_names=','.join(self.images[image_path])))
            session.commit()
            for tag in self.images[image_path]:
                tag_search = session.query(Tags).filter_by(tag_name=tag).first()
                if not tag_search:
                    session.add(Tags(tag_name=tag, json_dump=json.dumps({"cursor" : "dummy", "gfycats" : [gfycat] , "tag" : tag , "tagText": tag})))
                    session.commit()
                    break
    @property
    def tags(self):
        return {"cursor": "dummy", "tags": [json.loads(result.json_dump) for result in session.query(Tags).all()]}

    def search_gifs(self, search_text):
        tag_query = sqlalchemy.select([
            images_table.c.json_dump,
        ]).filter(images_table.c.tag_names.contains(search_text))

        tag_result = [json.loads(result[0]) for result in engine.execute(tag_query).fetchall()]

        title_query = sqlalchemy.select([
            images_table.c.json_dump,
        ]).filter(images_table.c.image_title.contains(search_text))

        title_result = [json.loads(result[0]) for result in engine.execute(title_query).fetchall()]

        return {"cursor": "dummy", "gfycats":[*tag_result, *title_result]}

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