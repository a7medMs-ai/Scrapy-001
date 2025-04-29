import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse
import os
import hashlib

class WebsiteSpider(scrapy.Spider):
    name = "website_spider"

    def __init__(self, start_url=None, depth_limit=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.allowed_domains = [urlparse(start_url).netloc]
        self.depth_limit = depth_limit
        self.visited = set()

    def parse(self, response):
        url = response.url
        if url in self.visited:
            return
        self.visited.add(url)

        language = self.detect_language_from_url(url)
        folder_path = f"output/html_pages/{language}"
        os.makedirs(folder_path, exist_ok=True)

        filename = self.clean_filename(response.url)
        full_path = os.path.join(folder_path, filename)

        with open(full_path, "wb") as f:
            f.write(response.body)

        links = response.css("a::attr(href)").getall()
        for link in links:
            full_url = response.urljoin(link)
            if urlparse(full_url).netloc == self.allowed_domains[0]:
                yield scrapy.Request(full_url, callback=self.parse)

    def detect_language_from_url(self, url):
        # You can improve detection by content later
        if "/ar" in url or url.endswith("/ar"):
            return "ar"
        elif "/en" in url or url.endswith("/en"):
            return "en"
        else:
            return "default"

    def clean_filename(self, url):
        path = urlparse(url).path.strip("/")
        if not path:
            return "home.html"
        if path.endswith("/"):
            path = path[:-1]
        hashed = hashlib.md5(url.encode()).hexdigest()[:6]
        filename = f"{path.replace('/', ' - ')} - {hashed}.html"
        return filename


def run_spider(start_url, depth_limit=None):
    from scrapy.settings import Settings
    settings = Settings()
    settings.set("DEPTH_LIMIT", depth_limit)
    settings.set("USER_AGENT", "Mozilla/5.0 (WebScrapyTool)")
    settings.set("LOG_ENABLED", False)
    settings.set("HTTPCACHE_ENABLED", False)

    process = CrawlerProcess(settings)
    process.crawl(WebsiteSpider, start_url=start_url, depth_limit=depth_limit)
    process.start()
