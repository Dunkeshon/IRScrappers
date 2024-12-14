from pymongo import MongoClient
from bs4 import BeautifulSoup
import json
import logging
import re
from base_scrapper import BaseScraper, ArticleItem
import requests

from selenium import webdriver

logger = logging.getLogger(__name__)


class IkeaTrustPilotScrapper(BaseScraper):
    source = 'https://www.consumeraffairs.com/furniture/ikea.html#scroll_to_reviews=true'
    def iterate_articles_list(self):

        page = 1
        done = False

        page_url = f"https://www.consumeraffairs.com/furniture/ikea.html?page={page}"
        driver_path = 'D:/chromedriver-win64/chromedriver'
        driver = webdriver.Chrome(driver_path)
        driver.get(page_url)


        # while not done:
        #     print("------------------------")
        #     print(f"{self.scraper_name}: Scraping page {page}...")
        #
        #
        #
        #
        #
        #     params = {"js_render": "true", "json_response": "true"}
        #     response = self.client.get(page_url, params=params)
        #
        #     page_html = response.text
        #     soup = BeautifulSoup(page_html, "lxml")
        #     reviews = soup.select(".js-rvw rvw")
        #     title_text = ""
        #     body_text = ""
        #
        #     for review in reviews:
        #
        #         p_elements = review.find_all('p')  # This includes nested <p> elements
        #         if p_elements:
        #             body_text = " ".join([p.get_text(strip=True) for p in p_elements])
        #             # Extract the first sentence from body_text
        #             title_text = re.split(r'\. ', body_text, 1)[0] + "."
        #
        #
        #         yield ArticleItem(source_site=self.source, article_title=title_text, article_link=page_url,
        #                           article_text=body_text)
        #
        #     next_page_link = soup.select_one(".js-pager-next")
        #     if next_page_link is None or not reviews:
        #         done = True
        #     page += 1

    def get_article_details(self, article_link: str, article_title: str, url: str) -> ArticleItem | None:
        return None


if __name__ == '__main__':
    db_client = MongoClient('localhost', 27017)
    db = db_client.IR_Ikea
    scrapedArticles = db.reviewsFurniture

    scraper = IkeaTrustPilotScrapper()

    for result in scraper.iterate_articles_list():

        if result.article_text == "" and result.article_title == "":
            print("skipping" + str(result.to_dict()))
            continue
        print(f"Scraped article {result.article_title} from url {result.article_link}")
        print("Body text:", json.dumps(result.article_text)[:100], "...")
        # existing_document = scrapedArticles.find_one({"articleLink": scraped_article.to_dict()["articleLink"]})
        #
        # if existing_document:
        #     print("Document with the specified field value already exists. Skipping insert.")
        #     continue
        # Insert the document if no match is found
        scrapedArticles.insert_one(result.to_dict())
