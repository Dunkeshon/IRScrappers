from pymongo import MongoClient
from bs4 import BeautifulSoup
import json
import logging
import re
from base_scrapper import BaseScraper, ArticleItem
import requests






class TheSpruceIkeaScrapper(BaseScraper):
    source = 'https://www.thespruce.com/search?q=ikea'

    def iterate_articles_list(self):

        page = 1
        done = False
        page_url = f"https://www.thespruce.com/search?q=ikea"
        while not done:
            print("------------------------")
            print(f"{self.scraper_name}: Scraping page {page}...")

            response = requests.get(page_url)
            page_html = response.text
            soup = BeautifulSoup(page_html, "lxml")
            reviews = soup.select(".card__content")
            title_text = ""
            body_text = ""

            links = soup.select(".card-list__entry > a")
            for link in links:
                url = link["href"]
                if not url.startswith("https://www.thespruce.com/"):
                    continue
                title = link.select_one(".card__title-text").strip()
                yield ArticleItem(source_site=self.source, article_title=title, article_link=url, article_text="")

            next_page_link = soup.select_one(".next_page_link > a")
            if next_page_link is None or not links:
                done = True
            else:
                page_url = next_page_link["href"]

    def get_article_details(self, article_link: str, article_title: str, url: str) -> ArticleItem | None:

        response = requests.get(url)
        page_html = response.text
        soup = BeautifulSoup(page_html, "lxml")

        grant_body = soup.select_one(".article--structured")

        if grant_body is None:
            print(f"no body {article_link}:  {article_title} {url}...")
            return None

        text_content = []

        for tag in grant_body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text_content.append(tag.get_text(strip=True))

        body_text = "\n".join(text_content)
        return ArticleItem(self.source, article_link, article_title, body_text)


if __name__ == '__main__':
    db_client = MongoClient('localhost', 27017)
    db = db_client.IR_Ikea
    scrapedArticles = db.articles2

    scraper = TheSpruceIkeaScrapper()

    for result in scraper.iterate_articles_list():
        scraped_article = scraper.get_article_details(result.article_link, result.article_title, result.article_link)
        if scraped_article is None:
            continue
        print(f"Scraped article {scraped_article.article_title} from url {scraped_article.article_link}")
        print("Body text:", json.dumps(scraped_article.article_text)[:100], "...")
        # existing_document = scrapedArticles.find_one({"articleLink": scraped_article.to_dict()["articleLink"]})
        #
        # if existing_document:
        #     print("Document with the specified field value already exists. Skipping insert.")
        #     continue
        # Insert the document if no match is found
        scrapedArticles.insert_one(scraped_article.to_dict())

