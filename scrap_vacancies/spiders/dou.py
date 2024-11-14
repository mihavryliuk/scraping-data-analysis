import scrapy
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from scrapy.http import HtmlResponse
from scrap_vacancies.items import ScrapVacanciesItem


class DouSpider(scrapy.Spider):
    name = "dou"
    allowed_domains = ["jobs.dou.ua"]
    start_urls = ["https://jobs.dou.ua/vacancies/?category=Python"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.technologies = self.load_technologies("technologies.json")
        self.driver = webdriver.Chrome()

    def load_technologies(self, file_path: str) -> list:
        with open(file_path, "r") as file:
            return json.load(file)

    def parse(self, response):
        self.driver.get(response.url)

        while True:
            try:
                more_button = self.driver.find_element(By.CSS_SELECTOR, ".more-btn a")
                more_button.click()
                time.sleep(2)
            except Exception:
                break

        html = self.driver.page_source

        scrapy_response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        vacancies = scrapy_response.css("li.l-vacancy")
        for vacancy in vacancies:
            time.sleep(1)
            vacancy_url = vacancy.css("a.vt::attr(href)").get()
            if vacancy_url:
                yield scrapy_response.follow(vacancy_url, callback=self.parse_vacancy)

        self.driver.quit()

    def parse_vacancy(self, response):
        item = ScrapVacanciesItem()

        item["title"] = response.css("h1.g-h2::text").get()
        item["company"] = response.css("div.l-n a::text").get()
        item["location"] = response.css("span.place::text").get()
        item["salary"] = response.css("span.salary::text").get()

        description = response.css("div.b-typo.vacancy-section").getall()
        item["description"] = " ".join(description).strip()

        technologies = self.extract_technologies(item["description"])
        item["technologies"] = technologies

        experience = self.extract_experience(item["description"])
        item["experience"] = experience

        yield item

    def extract_technologies(self, description_text):
        found_technologies = [
            tech for tech in self.technologies if tech.lower() in description_text.lower()
        ]
        return found_technologies

    def extract_experience(self, description_text):
        match = re.search(r"(\d+\+? years)", description_text)
        return match.group(0) if match else "N/A"
