from typing import Generator
from dataclasses import dataclass


@dataclass
class ArticleItem:
    source_site: str
    article_link: str
    article_title: str
    article_text:str

    def to_dict(self):
        return {
            "sourceSite": self.source_site,
            "articleLink": self.article_link,
            "articleTitle": self.article_title,
            "articleText": self.article_text
        }


class BaseScraper:
    source: str


    def __init__(self):
        self.scraper_name = type(self).__name__

        if not self.source:
            raise ValueError(f"Source not set for {self.scraper_name}")

    def iterate_articles_list(self) -> Generator[ArticleItem, None, None]:
        raise NotImplementedError()



    def get_article_details(self, article_link: str, article_title: str, url: str) -> ArticleItem:
        raise NotImplementedError()
