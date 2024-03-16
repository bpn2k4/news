import scrapy

categories = [
    ("Chính trị", "/chinhtri", )
]


class VietnamnetSpider(scrapy.Spider):
  def __init__(self, name="VietnamnetSpider", **kwargs):
    super().__init__(name, **kwargs)
