# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import DongguanItem


class DgSpider(CrawlSpider):
    name = 'dg'
    allowed_domains = ['wz.sun0769.com']
    start_urls = ['http://d.wz.sun0769.com/index.php/question/questionType?type=4&page=0']
    # 每一页的匹配链接
    pagelink = LinkExtractor(allow="type=4")
    # 每一页里的每个帖子的匹配规则
    contentlink = LinkExtractor(allow=r'html/question/\d+/\d+.shtml')
    rules = (
        # 本案例的url被web服务器篡改，需要调用process_links来处理提取出来的url
        # 没写callback函数，follow为真,否则默认为False,写了就需要指明follow为True或者False
        Rule(pagelink, process_links="deal_links"),
        Rule(contentlink, callback="parse_item")
    )

    # links是当前response里提取出来的链接列表
    def deal_links(self,links):
        for i in links:
            i.url = i.url.replace("?", "&").replace("Type&", "Type?")
        return links

    def parse_item(self, response):

        item = DongguanItem()
        # 标题
        item['title'] = response.xpath('//div[contains(@class,"pagecenter p3"]//strong/text()').extract()
        # 标号
        item['number'] = item['title'].split(' ')[-1].split(":")[-1]
        # 内容,先使用有图片下的匹配规则，如果有内容，返回内容的列表集合
        content = response.xpath('//div[@class="c1 text14_2"]/text()').extract()
        # 如果没有内容，返回空列表，则使用无图片情况下的匹配规则
        if len(content) == 0:
            item["content"] = "".join(content).strip()
        else:
            item['content'] = "".join(content).strip()
        # 链接
        item['url'] = response.url

        yield item

