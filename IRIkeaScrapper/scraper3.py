from selenium import webdriver
from base_scrapper import BaseScraper, ArticleItem
from pymongo import MongoClient

import json
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re


class IkeaTrustPilotScrapper(BaseScraper):
    source = 'https://www.consumeraffairs.com/furniture/ikea.html#scroll_to_reviews=true'
    def iterate_articles_list(self):

        page = 1
        done = False

        driver = webdriver.Chrome()
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")  # Open browser in full-screen mode
        driver = webdriver.Chrome(options=options)

        while not done:

            page_url = f"https://www.consumeraffairs.com/furniture/ikea.html?page={page}"

            driver.get(page_url)
            print("------------------------")
            print(f"{self.scraper_name}: Scraping page {page}...")

            try:
                # Wait for the reviews to load
                WebDriverWait(driver,1000000).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".js-rvw.rvw"))
                )
            except TimeoutException:
                print("No reviews found or timeout occurred.")
                break

            # Extract reviews
            reviews = driver.find_elements(By.CSS_SELECTOR, ".js-rvw.rvw")
            for review in reviews:
                body_text = ""
                title_text = ""

                # Extract the <p> elements inside each review
                p_elements = review.find_elements(By.TAG_NAME, 'p')
                if p_elements:
                    body_text = " ".join([p.text.strip() for p in p_elements])
                    # Extract the first sentence from body_text
                    title_text = re.split(r'\. ', body_text, 1)[0] + "."


                yield ArticleItem(source_site=self.source, article_title=title_text, article_link=page_url,
                                          article_text=body_text)

            # Check for a next page button
            try:
                next_page_button = driver.find_element(By.CSS_SELECTOR, ".js-pager-next")
                next_page_button.click()
                page += 1
                WebDriverWait(driver, 1000000).until(
                    EC.staleness_of(reviews[0])  # Wait for the page to load completely
                )
            except Exception as e:
                print("No next page or error:", e)
                done = True


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
