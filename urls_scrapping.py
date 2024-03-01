from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import pandas as pd
import sqlite3
import re


#driver initialization
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome("C:\\chrdr\\chromedriver.exe", options=chrome_options)

#wait procedure initialization
wait = WebDriverWait(driver, 10)

#open website
driver.get("https://www.ekstraklasa.org/terminarz/")

#accept cookies
wait.until(EC.element_to_be_clickable((By.XPATH, "//app-cookies/div/div/button[1]"))).click()

#reload page
driver.refresh()
sleep(2)

#get number of current round
round_number = wait.until(EC.visibility_of_element_located((By.XPATH, "//app-view-main-round-schedules/app-section[2]/div[2]/div/div/app-league-widget-schedule/div[1]/div/span"))).text
round_number = int(round_number.replace(". KOLEJKA", ""))

#define parts of xpath for match sites
url_part1 = "//app-league-widget-schedule/div[2]/div["
url_part2 = "]/app-league-widget-schedule-match["
url_part3 = "]/div[1]/div"

#dataframe for urls and round numbers
matches_urls = pd.DataFrame(columns=["url", "round"])

#rewind (by clicking the left arrow in matches schedule) the schedule from current round to the first round
#for each round store all match urls and the round number in dataframe matches_urls
stop_flag = False #flag defining if left arrow in match schedule doesn't exist (if it doesn't exist we are in the first round)
current_round = round_number #number of currently processing round

#main url scrapping loop
while current_round > 0:
    round_urls = [] #list for scrapped matches url for particular round
    count1, count2 = 2, 1 #counters for creating xpaths
    
    print(f"Current round: {current_round}")
    
    #loop for scrapping all matches urls for current round (there are 9 matches in each round)
    while len(round_urls)<9:
        
        #click the schedule left arrow to reach the proper round schedule
        for i in range(0, round_number - current_round):
            #wait.until(EC.visibility_of_element_located((By.XPATH, "//app-league-widget-schedule/div[1]/div/div[1]/tui-svg"))).click()
            arrow_button = driver.find_element(by=By.XPATH, value="//app-league-widget-schedule/div[1]/div/div[1]/tui-svg")
            arrow_button.click()
            print("button clicked!")
            sleep(2)
            
        try:
            #locate match and click on it (openthe  match page)
            print(url_part1+str(count1)+url_part2+str(count2)+url_part3)
            match_button = driver.find_element(by=By.XPATH, value=url_part1+str(count1)+url_part2+str(count2)+url_part3)
            match_button.click()
            sleep(2)
            
            #add match page url to the list and go back
            #(going back results in schedule for different round (round_number), so for next match we should click the left arrow again)
            round_urls.append(driver.current_url)
            count2 += 1
            print("url scrapped!")
            driver.back()
            sleep(2)
                
        except NoSuchElementException: #if there is no match button to click
            count1 += 1
            count2 = 1
            driver.refresh()
            sleep(2)
    
    #when round_urls is full, add results to matches_url dataframe and decrement current round number
    for url in round_urls:
        matches_urls.loc[len(matches_urls)] = [url, current_round]
    
    current_round -= 1
 

#moving forward through the matches schedule (by clicking the rigth arrow) from the upcoming round to the list round
#again - for each round all match urls and the round number are stored in dataframe matches_urls
stop_flag = False #flag defining if left arrow in match schedule doesn't exist (if it doesn't exist we are in the first round)
current_round = round_number +1 #number of currently processing round (we start from the upcoming round)
last_round = 34 #number of the last round

#main url scrapping loop
while current_round <= last_round:
    round_urls = [] #list for scrapped matches url for particular round
    count1, count2 = 2, 1 #counters for creating xpaths
    
    print(f"Current round: {current_round}")

    #loop for scrapping all matches urls for current round (there are 9 matches in each round)
    while len(round_urls)<9:
        
        #click the schedule right arrow to reach the proper round schedule
        for i in range(0, current_round - round_number):
            arrow_button = driver.find_element(by=By.XPATH, value="//app-league-widget-schedule/div[1]/div/div[2]/tui-svg")
            arrow_button.click()
            print("button clicked!")
            sleep(2)
            
        try:
            #locate match and click on it (openthe  match page)
            print(url_part1+str(count1)+url_part2+str(count2)+url_part3)
            match_button = driver.find_element(by=By.XPATH, value=url_part1+str(count1)+url_part2+str(count2)+url_part3)
            match_button.click()
            sleep(2)
            
            #add match page url to the list and go back
            #(going back results in schedule for different round (round_number), so for next match we should click the left arrow again)
            round_urls.append(driver.current_url)
            count2 += 1
            print("url scrapped!")
            driver.back()
            sleep(2)
                
        except NoSuchElementException: #if there is no match button to click
            count1 += 1
            count2 = 1
            driver.refresh()
            sleep(2)
    
    #when round_urls is full, add results to matches_url dataframe and decrement current round number
    for url in round_urls:
        matches_urls.loc[len(matches_urls)] = [url, current_round]
    
    current_round += 1
 

#sort dataframe by round number (ascending)
matches_urls.sort_values(by=['round'], inplace=True)

#data base creation, table consists 2 columns: url and round number
conn = sqlite3.connect("matches_urls.db")
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS urls")
c.execute('''CREATE TABLE urls (
	url TEXT,
	round INTEGRER
	);''')
conn.commit()
query_item=f"INSERT INTO urls VALUES (?,?);"

#stored url must be shorted - the end of each link is additional and can cause some problem during the statistics scrapping
#pattern for important part of each url (rest will be deleted)
pattern_url = re.compile(r"([^/]+//([^/]+/){4})") 

new_url = pattern_url.search(matches_urls["url"][1]).group() 

#filling the database
for ind in matches_urls.index:
    new_url = pattern_url.search(matches_urls["url"][ind]).group() #shorted url
    new_row = (new_url, int(matches_urls["round"][ind]))
    c.execute(query_item, new_row)
    conn.commit()

#adding additional column describing if given match has been already scrapped or not (Y/N, defalut value is N)
c.execute("ALTER TABLE urls ADD scrapped CHAR(1) DEFAULT 'N'")
conn.commit()

#close db connection and driver
conn.close()
driver.quit()
