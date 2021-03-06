# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst, MapCompose


class ProductItem(Item):
    title = Field()
    price = Field()
    url = Field()
    image_name = Field()
    # meta
    article = Field()
    brand = Field()
    categories = Field()

# class CategoryItem(scrapy.Item):
#     name = scrapy.Field()

class ImageItem(Item):
    image_urls = Field()
    images = Field()
    image_name = Field(
        # input_processor = MapCompose(remove_extention),
        output_processor = TakeFirst()
    )