# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
import logging

from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

from elkom.items import ProductItem

CREATE_TABLE_PRODUCTS = '''
    CREATE TABLE products(
        title TEXT,
        price TEXT,
        product_url TEXT,
        image_name TEXT
        )
'''
INSERT_PRODUCT = '''
    INSERT INTO products (title, price, product_url, image_name) VALUES (?, ?, ?, ?)
'''

MSG_TABLE_ALREADY_EXISTS = "Table already exists"

class SQLlitePipeline:

    def open_spider(self, spider):
        self.connection = sqlite3.connect("imdb.db")
        self.c = self.connection.cursor()
        try:
            self.c.execute(CREATE_TABLE_PRODUCTS)
            self.connection.commit()
        except sqlite3.OperationalError:
            logging.warning(MSG_TABLE_ALREADY_EXISTS)

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            self.c.execute(INSERT_PRODUCT, (
                item.get('title'),
                item.get('price'),
                item.get('url'),
                item.get('image_name'),
            ))
            self.connection.commit()
        return item

class ElkomImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        return [Request(x, meta={'image_name': item["image_name"]}) 
            for x in item.get('image_urls', [])]

    def file_path(self, request, response=None, info=None, *, item=None):
        # image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        image_name = request.meta['image_name']
        path = f'elkom/{image_name}.jpg'
        return path