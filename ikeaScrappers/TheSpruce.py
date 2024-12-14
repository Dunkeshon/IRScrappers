from pymongo import MongoClient
import json
import logging
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait

from base_scrapper import BaseScraper, ArticleItem
from selenium import webdriver
import time



options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Open browser in full-screen mode
driver = webdriver.Chrome(options=options)

articleLinks = []
articleItems = []
class TheSpruceIkeaScrapper(BaseScraper):
    source = 'https://www.thespruce.com/search?q=ikea'
    def iterate_articles_list(self):

        page = 1
        done = False



        page_url = f"https://www.thespruce.com/search?q=ikea"
        while not done:
            print("------------------------")
            print(f"{self.scraper_name}: Scraping page {page}...")

            driver.get(page_url)

            try:
                # Wait for the reviews to load

                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card-list__entry"))
                )
            except TimeoutException:
                print("No reviews found or timeout occurred.")
                break


            links = driver.find_elements(By.CSS_SELECTOR, ".card-list__entry > a")


            for link in links:


                url = link.get_attribute("href")
                if not url.startswith("https://www.thespruce.com/"):
                    continue
                title = link.find_element(By.CSS_SELECTOR, ".card__title-text").text.strip()
                articleItems.append(ArticleItem(source_site=self.source, article_title=title, article_link=url, article_text=""))
            articleLinks.append(links)
            # next_page_link = driver.find_element(By.CSS_SELECTOR, ".pagination__item-link--next")
            try:
                # Wait for the next page link to be present
                next_page_link = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".pagination__item-link--next"))

                )
                page_url = next_page_link.get_attribute("href")
                page+=1

            except (StaleElementReferenceException, TimeoutException):
                print("Next page link does not exist or was not found in time.")
                done = True

    def get_article_details(self, article_link: str, article_title: str, url: str) -> ArticleItem | None:

        driver.get(url)
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".main"))
        )

        main_element = driver.find_element(By.CSS_SELECTOR, ".main")

        # Locate the prefooter element to exclude its text
        prefooter_element = main_element.find_element(By.CSS_SELECTOR, ".prefooter")

        # Get all text from the main element
        main_text = main_element.text

        # Get text from the prefooter element
        prefooter_text = prefooter_element.text

        # Remove the prefooter text from the main text
        final_text = main_text.replace(prefooter_text, "").strip()


        return ArticleItem(self.source, article_link, article_title, final_text)

if __name__ == '__main__':
    db_client = MongoClient('localhost', 27017)
    db = db_client.IR_Ikea
    scrapedArticles = db.articles2

    scraper = TheSpruceIkeaScrapper()
    scraper.iterate_articles_list()
    for articleItem in articleItems:
        scraped_article = scraper.get_article_details(articleItem.article_link, articleItem.article_title, articleItem.article_link)
        if scraped_article is None:
            continue
        print(f"Scraped article {scraped_article.article_title} from url {scraped_article.article_link}")
        print("Body text:", json.dumps(scraped_article.article_text)[:100], "...")
        scrapedArticles.insert_one(scraped_article.to_dict())
    driver.quit()

