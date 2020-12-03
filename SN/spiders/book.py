# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json
import re

'''
首页大分类
首页大分类下的小分类
小分类下的图书
'''

class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['suning.com']
    start_urls = ['http://book.suning.com/']

    def parse(self, response):
        #先获取大的xpath
        li_list = response.xpath("//div[@class='menu-item']/dl")
        for li in li_list:
            item = {}
            item["big_category"] = li.xpath(".//a/text()").extract_first()
            dd_list = li.xpath(".//dd/a")
            for dd in dd_list:
                #小分类
                item["small_category"] = dd.xpath("./text()").extract_first()
                #小分类的url地址
                item["small_href"] = dd.xpath("./@href").extract_first()
                #访问小分类下的图书
                yield scrapy.Request(url=item["small_href"],callback=self.parse_list,meta={"item":deepcopy(item)})

    # 小分类的详情页面
    def parse_list(self,response):
        #接收传过来的数据
        item = response.meta.get("item")
        #子页面的所有的图书
        books_list = response.xpath("//ul[@class='clearfix']/li")
        for book in books_list:
            item["book_name"] = book.xpath("//div[@class='res-img']//img/@alt").extract_first()
            item["book_image"] = book.xpath("//div[@class='res-img']//img/src").extract_first()
            item["href"] = book.xpath("//div[@class='res-img']//a/@href").extract_first()
            if item["href"] is not None:
                item["href"] = "https:" + item["href"]
                yield scrapy.Request(url=item["href"],callback=self.parse_detail,meta={"item":deepcopy(item)})

        # 分页
        # https://list.suning.com/emall/showProductList.do?ci=502308&pg=03&cp=2 这是第三页的列表页面
        page_count = int(re.findall(r"param.pageNumbers='(.*?)';",response.text)[0])
        current_page = int(re.findall(r'param.currentPage = "(.*?)";', response.text)[0])



    def parse_data(self,data):
        return data.replace("\n","").replace("\r","").replace("\t","").replace("</span>","")




    #每个图书的详情页面
    def parse_detail(self,response):
        item = response.meta.get("item")
        #每个图书的详情页面的作者和出版社
        item["book_author"] = response.xpath("//ul[@class='bk-publish clearfix']/li[1]/text()").extract_first()
        #清洗数据 删除字符
        item["book_author"] = self.parse_data(item["book_author"])
        item["book_press"] = response.xpath("//ul[@class='bk-publish clearfix']/li[2]/text()").extract_first()
        item["book_press"] = self.parse_data(item["book_press"])
        print(item)
        #保存查询到的数据
        with open("book.text","a",encoding="utf-8") as f:
            f.write(json.dumps(item,ensure_ascii=False))











