# Scraping-data-analysis
This project is a web scraper developed using Scrapy and Selenium to gather job vacancy data from the "jobs.dou.ua" website.
It collects information about job titles, companies, locations, salaries, descriptions, and required technologies.
The scraped data is stored in CSV format for further analysis. 
The scraper is designed to handle various categories and experience levels, providing insights into job market trends in the tech industry.
Additionally, the project includes data analysis using Python and visualizations with libraries like Matplotlib and Pandas.
## Start the Project

1. Clone repository  
```shell
git clone https://github.com/mihavryliuk/scraping-data-analysis.git
```
2. Create and activate .venv environment  
```shell
python -m venv env
```

```shell
venv\Scripts\activate
```

3. Install requirements.txt by the command below  


```shell
pip install -r requirements.txt
```


4. Start parsing and collect data to csv by the command below
```shell
scrapy crawl dou -O vacancies.csv
```

5. Analyse data in vacancy_analysis.ipynb

