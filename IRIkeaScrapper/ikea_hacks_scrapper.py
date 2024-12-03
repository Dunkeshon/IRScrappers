from typing import Generator

from bs4 import BeautifulSoup
import json
import logging

from base_scrapper import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def iterate_articles_list(source):
    page = 0
    done = False
    while not done:
        logger.info(f"{source}: Scraping page {page}...")
        page_url = f"https://ikeahackers.net/hacks/page/{page}"


class IkeaHacksScrapper(BaseScraper):
    source = 'https://ikeahackers.net/hacks'

    def iterate_articles_list(self):
        page = 1
        done = False
        while not done:
            logger.info(f"{self.scraper_name}: Scraping page {page}...")
            page_url = f"https://www.caor.camcom.it/bandi?combine=&field_bando_stato_value=aperto&page={page}"
            response = self.client.get(page_url)
            page_html = response.text
            soup = BeautifulSoup(page_html, "lxml")
            links = soup.select(".cb-post-title > a")
            for link in links:
                url = link["href"]
                if not url.startswith("https://ikeahackers.net/"):
                    continue
                title = link.get_text().strip()
                yield ArticleItem(source_site=self.source, article_title=title, article_link=url, article_text="")

            next_page_link = soup.select(".pagination .next")
            if next_page_link is None or not links:
                done = True
        page += 1

    def get_article_details(self, article_link: str, article_title: str, url: str) -> ArticleItem | None:
        response = self.client.get(url)
        page_html = response.text

        soup = BeautifulSoup(page_html, "lxml")

        grant_body = soup.select_one("entry-content-wrap")

        if grant_body is None:
            logger.error(f"no body {article_link}:  {article_title} {url}...")
            return None

        text_content = []

        for tag in grant_body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text_content.append(tag.get_text(strip=True))

        body_text = "\n".join(text_content)
        return ArticleItem(self.source, article_link, article_title, body_text)

if __name__ == '__main__':
    print("hello world")

    scraper = IkeaHacksScrapper()

    for result in scraper.iterate_articles_list():
        scraped_article = scraper.get_article_details(result.article_link, result.article_title, result.article_link)
        print(f"Scraped article {scraped_article.article_title} from url {scraped_article.article_link}")
        print("Body text:", json.dumps(scraped_article.article_text)[:100], "...")
        save_to_json(scraped_article, "ikeahackers.json")




