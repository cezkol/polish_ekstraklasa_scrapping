**Scrapping data for the top Polish football division - PKO Ekstraklasa**

As a big football fan, I decided to write a script to scrape the data of the top Polish football league - PKO Ekstraklasa. I used data published on the official league website: https://www.ekstraklasa.org/
Because the content of https://www.ekstraklasa.org/ is dynamic (generated using JS scripts), I cannot use libraries like BeautifulSoup. So I used Selenium instead - to create the Google Chrome webdriver and just browse through the whole round schedule. 
I stored scrapped data in database using sqlite3. 

Content list: 
- ekstraklasa.db - database containing scrapped data. There are a total of 18 tables (one per team), with each match is represented by a single row.
- matches_urls - scrapped matches URLs (https://www.ekstraklasa.org/) for each one of 306 matches in the 2023/2024 season
-  urls_scrapping.py - script to scrape the urls of each match in the schedule (there are 18 teams and 34 rounds, so there are 306 matches in total). The schedule on https://www.ekstraklasa.org/ is dynamically generated using JS scripts, so I used Selenium to manually browse through each round and store the match address. The URLs are stored in matches_urls.db.
- stats_scrapping.py - script for scrapping statistics for each match. Match URLs are loaded from maches_urls.db and then - using Selenium - statistics for both teams in the match are scrapped and stored in ekstraklasa.db.

Use python libraries:
- selenium
- sqlite3
- pandas
- re

Last database update: 01.03.2024
