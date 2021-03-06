from datetime import datetime

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from itemadapter import ItemAdapter

from elkom.items import ProductItem, ImageItem


class ElkomCrawlerSpider(CrawlSpider):
    name = 'elkom_crawler'
    allowed_domains = ['elkom.kz']
    start_urls = ['http://elkom.kz/catalog']

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=r"//div[@class='catalog_section_list row items flexbox']/div//td[@class='image']/a",
                          deny=[
                                #r"kabelno-provodnikovaya-produktsiya/",
                                #r"svetotekhnika/",
                                #r"ustanovochnye-pribory/",
                                #r"elektrooborudovanie/",
                                #r"shkafy-shchity-boksy-i-aksessuary/",
                                #r"vspomogatelnye-materialy/",
                                #r"sezonnyy-tovar/",
                                #r"raznoe-12871/",
                                r"-rasprodazha/"
                                ]
                                ), # catalog
            follow=True),
        Rule(
            LinkExtractor(restrict_xpaths=r"//div[@class='right_block1 clearfix catalog compact']//ul[@class='flex-direction-nav']/li[@class='flex-nav-next ']/a"), # next page
            follow=True),
        Rule(
            LinkExtractor(restrict_xpaths=r"//div[@class='right_block1 clearfix catalog compact']//td[@class='item-name-cell item_info']/div[@class='title']/a"), # item page 
            callback='parse_item', 
            follow=True),
        Rule(
            LinkExtractor(restrict_xpaths=r"//div[@class='catalog_block items block_list']//div[@class='catalog_item_wrapp item']//div[@class='item-title']/a"), # item page 
            callback='parse_item', 
            follow=True),
    )

    def parse_item(self, response):
        # data
        product_item = ProductItem()
        product_item['title'] = response.xpath("//h1[@id='pagetitle']/text()").get()
        product_item['price'] = response.xpath("//div[@class='prices_block']//span[@class='price_value']/text()").get()
        product_item['url'] = response.url

        # image
        image_link = response.xpath("//div[@class='item_slider has_one' or @class='item_slider has_more']//li[@id='photo-0']/link")
        loader = ItemLoader(item=ImageItem(), selector=image_link)

        relative_url = image_link.xpath(".//@href").extract_first()
        absolute_url = response.urljoin(relative_url)
        loader.add_value('image_urls', absolute_url)

        name = datetime.now().strftime("%H%M%S%f")
        loader.add_value('image_name', name)

        yield loader.load_item()
        product_item['image_name'] = loader.item['image_name']

        # article
        article = response.xpath("//div[@class='right_info']//div[@class='article iblock']")
        if article:
            product_item['article'] = article.xpath(".//span[@class='value']/text()").get()
        # brand
        brand = response.xpath("//div[@class='right_info']//div[@class='brand']")
        if article:
            product_item['brand'] = article.xpath(".//meta/@content").get()
        
        # categories
        categories = []
        breadcrumbs = response.xpath("//div[@class='breadcrumbs']/div[@itemprop='itemListElement']")        
        for category in breadcrumbs[2:]:
            category_data = {
                'category_name': category.xpath(".//a/span[@itemprop='name']/text()").get(), 
                'category_level': category.xpath(".//a/meta[@itemprop='position']/@content").get()
                }
            categories.append(category_data)
        
        product_item['categories'] = categories


        yield product_item
