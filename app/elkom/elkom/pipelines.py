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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        price TEXT,
        image_name TEXT,
        article TEXT,
        brand TEXT,
        product_url TEXT
        )
'''
CREATE_TABLE_CATEGORIES = '''
    CREATE TABLE categories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        level TEXT
        )
'''
CREATE_TABLE_PRODUCTSCATEGORIES = '''
    CREATE TABLE productscategories(
        product_id TEXT,
        category_id TEXT
        )
'''
INSERT_TO_PRODUCTS = '''
    INSERT INTO products (title, price, image_name, article, brand, product_url) VALUES (?, ?, ?, ?, ?, ?)
'''
INSERT_TO_CATEGORIES = '''
    INSERT INTO categories(name, level) VALUES(?, ?)
    ON CONFLICT(name) DO NOTHING;
'''
INSERT_TO_PRODUCTSCATEGORIES = '''
    INSERT INTO productscategories(product_id, category_id) VALUES((SELECT id FROM products WHERE title = ?), 
                                                                   (SELECT id FROM categories WHERE name = ?));
'''

MSG_TABLE_ALREADY_EXISTS = "Table already exists"

class SQLlitePipeline:

    def open_spider(self, spider):
        self.connection = sqlite3.connect("imdb.db")
        self.c = self.connection.cursor()
        try:
            self.c.execute(CREATE_TABLE_PRODUCTS)
            # self.connection.commit()
            self.c.execute(CREATE_TABLE_CATEGORIES)
            # self.connection.commit()
            self.c.execute(CREATE_TABLE_PRODUCTSCATEGORIES)
            self.connection.commit()
        except sqlite3.OperationalError:
            logging.warning(MSG_TABLE_ALREADY_EXISTS)

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            self.c.execute(INSERT_TO_PRODUCTS, (
                item.get('title'),
                item.get('price'),
                item.get('image_name'),
                item.get('article'),
                item.get('brand'),
                item.get('url'),
            ))            

            categories = item.get('categories')
            for category in categories:
                self.c.execute(INSERT_TO_CATEGORIES, (
                    category['category_name'],
                    category['category_level'],
                ))
                self.c.execute(INSERT_TO_PRODUCTSCATEGORIES, (
                    item.get('title'),
                    category['category_name'],
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