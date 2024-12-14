from typing import Generator
from pymongo import MongoClient
from bs4 import BeautifulSoup
import json
import logging

from base_scrapper import BaseScraper, ArticleItem
import requests

logger = logging.getLogger(__name__)




class IkeaHacksScrapper(BaseScraper):
    source = 'https://ikeahackers.net/hacks'

    def iterate_articles_list(self):

        page = 1
        done = False
        while not done:
            print("------------------------")
            print(f"{self.scraper_name}: Scraping page {page}...")
            page_url = f"https://ikeahackers.net/hacks/page/{page}"
            # response = self.client.get(page_url)
            response = requests.get(page_url)
            page_html = response.text
            soup = BeautifulSoup(page_html, "lxml")
            links = soup.select(".cb-post-title > a")
            for link in links:
                url = link["href"]
                if not url.startswith("https://ikeahackers.net/"):
                    continue
                title = link.get_text().strip()
                yield ArticleItem(source_site=self.source, article_title=title, article_link=url, article_text="")

            next_page_link = soup.select_one(".pagination .next")
            if next_page_link is None or not links:
                done = True
            page += 1

    def get_article_details(self, article_link: str, article_title: str, url: str) -> ArticleItem | None:

        response = requests.get(url)
        page_html = response.text
        soup = BeautifulSoup(page_html, "lxml")

        grant_body = soup.select_one(".entry-content-wrap")

        if grant_body is None:
            logger.error(f"no body {article_link}:  {article_title} {url}...")
            return None

        text_content = []

        for tag in grant_body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text_content.append(tag.get_text(strip=True))

        body_text = "\n".join(text_content)
        return ArticleItem(self.source, article_link, article_title, body_text)

if __name__ == '__main__':
    db_client = MongoClient('localhost', 27017)
    db = db_client.IR_Ikea
    scrapedArticles = db.articles



    scraper = IkeaHacksScrapper()

    for result in scraper.iterate_articles_list():
        scraped_article = scraper.get_article_details(result.article_link, result.article_title, result.article_link)
        if scraped_article is None:
            continue
        print(f"Scraped article {scraped_article.article_title} from url {scraped_article.article_link}")
        print("Body text:", json.dumps(scraped_article.article_text)[:100], "...")
        existing_document = scrapedArticles.find_one({"articleLink": scraped_article.to_dict()["articleLink"]})

        if existing_document:
            print("Document with the specified field value already exists. Skipping insert.")
            continue
        # Insert the document if no match is found
        scrapedArticles.insert_one(scraped_article.to_dict())




