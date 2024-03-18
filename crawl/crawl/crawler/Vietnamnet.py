import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http.response.html import HtmlResponse
from bs4 import BeautifulSoup
import json
import re

rules = [
    r"\s*.*, (\d{1,2})/(\d{1,2})/(\d{4})\s*-\s*(\d{2}):(\d{2})\s*"
]

categories = [
    ["Chính trị", "/chinhtri", ]
]


class VietnamnetSpider(scrapy.Spider):
  def __init__(self, name="VietnamnetSpider", **kwargs):
    super().__init__(name, **kwargs)
    self.paper = "vietnamnet"
    self.base_url = "https://vietnamnet.com"
    self.start_url = "https://vietnamnet.vn/tin-tuc-24h-p40000"
    self.data_folder = f"./data/{self.paper}"
    self.writer = open("./data/p40000.json", "w+", encoding="utf-8")

  def start_requests(self):
    if not os.path.exists(self.data_folder):
      os.makedirs(self.data_folder)
    yield scrapy.Request(self.start_url, callback=self.parse_page)

  def parse_page(self, response: HtmlResponse):
    html = BeautifulSoup(response.text, "lxml")

    list_post = html.find_all("div", class_="horizontalPost")
    for i in list_post:
      title = None
      abstract = None
      link = None
      have_video = False
      img = None
      avatar_block = i.find("div", class_="horizontalPost__avt")
      if avatar_block:
        a_tag = avatar_block.find("a") or None
        if a_tag:
          title = a_tag.get("title") or None
          link = a_tag.get("href") or link or None
          video_icon = a_tag.find("span", class_="icon-avt")
          have_video = True if video_icon else False
          picture = a_tag.find("picture")
          if picture:
            img_tag = picture.find("img")
            if img_tag:
              img = img_tag.get("src") or None
              if img and img.startswith("data:"):
                img = img_tag.get("data-srcset") or None
            if img is None:
              source_tag = picture.get("source")
              if source_tag:
                img = source_tag.get("srcset") or None

      abstract_block = i.find("div", class_="horizontalPost__main-desc")
      if abstract_block:
        abstract = abstract_block.get_text() or None
      if link:
        metadata = {
            "title": title,
            "abstract": abstract,
            "have_video": have_video,
            "link": link,
            "image": img
        }
        yield scrapy.Request(
            url=link,
            callback=self.parse_new,
            meta=metadata
        )

    button_next = html.find(
        "li",
        class_="pagination__list-item pagination-next block"
    )
    if button_next is not None:
      next_page_link = button_next.find("a").get("href")
      if next_page_link is not None:
        pass
      else:
        return
    return

  def parse_new(self, response: HtmlResponse):

    title = response.request.meta["title"]
    abstract = response.request.meta["abstract"]
    have_video = response.request.meta["have_video"]
    link = response.request.meta["link"]
    image = response.request.meta["image"]

    html = BeautifulSoup(response.text, "lxml")

    title = self.find_title(html) or title
    abstract = self.find_abstract(html) or abstract
    content = self.find_content(html) or None
    publish = self.find_publish(html) or None

    self.writer.write(json.dumps({
        "title": title,
        "abstract": abstract,
        "have_video": have_video,
        "link": link,
        "image": image,
        "content": content,
        "publish": publish,
    }, ensure_ascii=False) + "\n")
    return

  def find_category(self, html):
    content = None
    return content
    pass

  def find_publish(self, html):
    publish = None
    date_block = html.find("div", class_="bread-crumb-detail__time")
    if date_block:
      time = date_block.get_text() or ""
      print(time)
      for rule in rules:
        match = re.match(time.strip(), rule)
        if match:
          day = int(match.group(1))
          month = int(match.group(2))
          year = int(match.group(3))
          hour = int(match.group(4))
          minute = int(match.group(5))
          return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00"
    return publish

  def find_title(self, html: BeautifulSoup):
    title = None
    h1_tag = html.find("h1", class_="content-detail-title")
    if h1_tag:
      title = h1_tag.get_text()
    return title

  def find_abstract(self, html: BeautifulSoup):
    abstract = None
    h2_tag = html.find("h2", class_="content-detail-sapo")
    if h2_tag:
      abstract = h2_tag.get_text()
    return abstract

  def find_content(self, html: BeautifulSoup):
    content = None
    return content

  def closed(self, _):
    self.writer.close()


def main():
  process = CrawlerProcess()
  process.crawl(VietnamnetSpider)
  process.start()


if __name__ == "__main__":
  main()
