import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bpssuisse.items import Article


class BpsSpider(scrapy.Spider):
    name = 'bps'
    start_urls = ['https://www.bps-suisse.ch/news.php']

    def parse(self, response):
        links = response.xpath('//div[@class="col-md-4 col-sm-6 col-xs-12"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = " ".join(response.xpath('//div[@class="data_int margina-giu"]/text()').get().split()[2:])
        if date:
            date = datetime.strptime(date.strip(), '%d-%m-%Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="testo_home margina-su margina-giu"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
