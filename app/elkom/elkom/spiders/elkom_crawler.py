import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader

from elkom.items import ProductItem, ImageItem


class ElkomCrawlerSpider(CrawlSpider):
    name = 'elkom_crawler'
    allowed_domains = ['elkom.kz']
    start_urls = ['http://elkom.kz/catalog']

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=r"//div[@class='catalog_section_list row items flexbox']/div//td[@class='image']/a"), # catalog
            follow=True),
        Rule(
            LinkExtractor(restrict_xpaths=r"//div[@class='right_block1 clearfix catalog vertical']//ul[@class='flex-direction-nav']/li[@class='flex-nav-next ']/a"), # next page
            follow=True),
        Rule(
            LinkExtractor(restrict_xpaths=r"//div[@class='right_block1 clearfix catalog compact']//td[@class='item-name-cell item_info']/div[@class='title']/a"), # item page 
            callback='parse_item', 
            follow=True),
    )

    def parse_item(self, response):
        # classes
        classes = []
        # tags
        tags = []

        # data
        product_item = ProductItem()
        product_item['title'] = response.xpath("//h1[@id='pagetitle']/@text()").get()
        product_item['price'] = response.xpath("//div[@class='prices_block']//span[@class='price_value']/text()").get()
        product_item['url'] = response.url

        # # image
        # image_link = response.xpaths("//div[@class='item_slider has_one']//li[@id='photo-0']/link")
        # loader = ItemLoader(item=ImageItem(), selector=image_link)

        # relative_url = image_link.xpath(".//@href").extract_first()
        # absolute_url = response.urljoin(relative_url)
        # loader.add_value('image_urls', absolute_url)

        # name = datetime.now().strftime("%H%M%S%f")
        # loader.add_value('image_name', name)

        # yield loader.load_item()

        # product_item['image_name'] = loader.item['image_name']
        product_item['image_name'] = ''
        product_item['article'] = ''
        product_item['brand'] = ''

        yield product_item
