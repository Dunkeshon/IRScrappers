from pymongo import MongoClient
from bs4 import BeautifulSoup
import json
import logging

from base_scrapper import BaseScraper, ArticleItem
import requests

logger = logging.getLogger(__name__)


class IkeaTrustPilotScrapper(BaseScraper):
    source = 'https://www.trustpilot.com/review/www.ikea.com'

    def iterate_articles_list(self):

        page = 1
        done = False
        while not done:
            print("------------------------")
            print(f"{self.scraper_name}: Scraping page {page}...")
            page_url = f"https://www.trustpilot.com/review/www.ikea.com?page={page}"
            response = requests.get(page_url)
            page_html = response.text
            soup = BeautifulSoup(page_html, "lxml")
            reviews = soup.select(".styles_reviewCardInner__EwDq2")
            title_text = ""
            body_text = ""

            for review in reviews:
                title = review.select_one(".typography_heading-s__f7029")
                if title is not None:
                    title_text = title.get_text(strip=True)
                body = review.select_one(".typography_body-l__KUYFJ")
                if body is not None:
                    body_text = body.get_text(strip=True)
                yield ArticleItem(source_site=self.source, article_title=title_text, article_link=page_url,
                                  article_text=body_text)

            # next_page_link = soup.select_one(".pagination-button-next")
            next_page_link = soup.find('a', {'name': 'pagination-button-next'})
            if next_page_link is None or not reviews or next_page_link.get('.aria-disabled') == 'true':
                done = True
            page += 1

    def get_article_details(self, article_link: str, article_title: str, url: str) -> ArticleItem | None:
        return None


if __name__ == '__main__':
    db_client = MongoClient('localhost', 27017)
    db = db_client.IR_Ikea
    scrapedArticles = db.reviews

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
