import re
import scrapy
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from scrapy.http import Response, HtmlResponse
from scrap_vacancies.items import ScrapVacanciesItem

class DouSpider(scrapy.Spider):
    name = "dou"
    allowed_domains = ["jobs.dou.ua"]
    start_urls = [
        "https://jobs.dou.ua/vacancies/?category=Python&exp=0-1",
        "https://jobs.dou.ua/vacancies/?category=Python&exp=1-3",
        "https://jobs.dou.ua/vacancies/?category=Python&exp=3-5",
        "https://jobs.dou.ua/vacancies/?category=Python&exp=5plus"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.technologies = self.load_technologies("technologies.json")
        self.driver = webdriver.Chrome()

    def load_technologies(self, file_path: str) -> list:
        with open(file_path, "r") as file:
            return json.load(file)

    def parse(self, response: Response):
        self.driver.get(response.url)

        while True:
            try:
                more_button = self.driver.find_element(By.CSS_SELECTOR, ".more-btn a")
                more_button.click()
                time.sleep(2)
            except Exception:
                break

        html = self.driver.page_source
        scrapy_response = HtmlResponse(url=self.driver.current_url, body=html, encoding="utf-8")

        experience = self.get_experience_from_url(response.url)

        vacancies = scrapy_response.css("li.l-vacancy")
        for vacancy in vacancies:
            time.sleep(2)
            vacancy_url = vacancy.css("a.vt::attr(href)").get()
            if vacancy_url:
                yield scrapy_response.follow(vacancy_url, callback=self.parse_vacancy, meta={"experience": experience})

        self.driver.quit()

    def parse_vacancy(self, response: Response) -> ScrapVacanciesItem:
        item = ScrapVacanciesItem()

        item["title"] = response.css("h1.g-h2::text").get()
        item["company"] = response.css("div.l-n a::text").get()
        item["location"] = response.css("span.place::text").get()

        salary = response.css("span.salary::text").get()
        if salary:
            salary = re.sub(r"[^0-9\-$ ]", "", salary).strip()

        item["salary"] = salary

        description = response.css("div.b-typo.vacancy-section").getall()
        item["description"] = " ".join(description).strip()

        item["experience"] = response.meta.get('experience', 'N/A')

        technologies = self.extract_technologies(item["description"])
        item["technologies"] = technologies

        yield item

    def extract_technologies(self, description_text):
        found_technologies = [
            tech for tech in self.technologies if tech.lower() in description_text.lower()
        ]
        return found_technologies

    def get_experience_from_url(self, url):
        if "exp=0-1" in url:
            return "0-1 years"
        elif "exp=1-3" in url:
            return "1-3 years"
        elif "exp=3-5" in url:
            return "3-5 years"
        elif "exp=5plus" in url:
            return "5+ years"
        return "N/A"
