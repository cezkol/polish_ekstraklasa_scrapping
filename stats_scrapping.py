from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
from time import sleep

#######WEBDRIVER######

#function that initiates webdriver and open page with given url
def webdriver_init():
    #driver initialization
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome("C:\\chrdr\\chromedriver.exe", options=chrome_options)
    
    #open default website
    driver.get("https://www.ekstraklasa.org/terminarz/")

    #accept cookies
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//app-cookies/div/div/button[1]"))).click()
    driver.refresh()
    sleep(3)

    return(driver)


#######MATCH STATS SCRAPPING######

#function that scraps match from given url (pass by input driver variable) and return a list with statistics for both teams
def match_scrap(driver, url):
    
    #open website
    driver.get(url)
    sleep(3)
 
    print(f"Current url: {driver.current_url}")

    #list for stats
    #each list element will be a 3 element list: [stat value for host, stat name (in polish), stat value for visitor]
    stats_match = []
    
    if driver.current_url[-7:] == "relacja": #if url ends with "relacja", it means that this match has been played
        
        #go to the section with statistics
        driver.get(url+"po-meczu/statystyki")
        
        #team names, goals, final results and home/away scrapping
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//app-upcoming-match-highlight")))
        highlights = driver.find_element("xpath", "//app-upcoming-match-highlight").text.split(chr(10))
        stats_match.append([highlights[1], "TEAM", highlights[3]])
        stats_match.append(["HOME", "HOME/AWAY", "AWAY"])
        stats_match.append([highlights[3], "OPPONENT", highlights[1]])
        
        goals = highlights[2].split(":")
        goals = [float(a) for a in goals]
        if goals[0]>goals[1]:
            stats_match.append(["W", "RESULT", "L"])
        elif goals[0]<goals[1]:
            stats_match.append(["L", "RESULT", "W"])
        else:
            stats_match.append(["D", "RESULT", "D"])
        
        stats_match.append([goals[0], "GOALS SCORED", goals[1]])
        stats_match.append([goals[1], "GOALS LOST", goals[0]])
        
        
        #match stats scrapping
        stats = driver.find_element("xpath", "//app-teams-comparison").text
        new_data = stats.split(chr(10)) #stats are divided by DATA LINK ESCAPE character (10 in ASCII)
        new_data = [new_data[n:n+3] for n in range(0, len(new_data), 3)]    #spliting list into 3-element sublists
        new_data = [[float(subl[0]), subl[1], float(subl[2])] for subl in new_data]
        stats_match.extend(new_data)
        
        
        #transforming the stats list. It will contain 3 tuples: stats values for host team, stats names and stats values for visitor team
        stats_match = list(zip(*stats_match))
        
        
    return(stats_match)


#club names acronyms (will be used for table names in database)
clubs_acrons = {
    "CRACOVIA": "CRA",
    "GÓRNIK ZABRZE": "GOR",
    "JAGIELLONIA BIAŁYSTOK": "JAG",
    "KGHM ZAGŁĘBIE LUBIN": "ZAG",
    "KORONA KIELCE": "KOR",
    "LECH POZNAŃ": "LPO",
    "LEGIA WARSZAWA": "LEG",
    "ŁKS ŁÓDŹ": "LKS",
    "PGE FKS STAL MIELEC": "STM",
    "PIAST GLIWICE": "PIA",
    "POGOŃ SZCZECIN": "POG",
    "PUSZCZA NIEPOŁOMICE": "PUN",
    "RADOMIAK RADOM": "RAD",
    "RAKÓW CZĘSTOCHOWA": "RCZ",
    "RUCH CHORZÓW": "RCH",
    "ŚLĄSK WROCŁAW": "SLA",
    "WARTA POZNAŃ": "WAR",
    "WIDZEW ŁÓDŹ": "WID"
}

#names of the statistics (will be used as table column names in database)
stat_names=["Round",
            "Home_Away",
			"Opponent",
            "Result",
			"Goals_scored",
			"Goals_lost",
			"Possession",
			"Shots",
			"Shots_on_target",
			"Corners",
			"Passes",
			"Passes_completed",
			"Crosses",
			"Crosses_completed",
			"Interceptions",
			"Fouls",
			"Offsides",
			"Yellow_cards",
			"Red_cards",
			"Distance",
			"Sprints"]


######MAIN#####
#import matches_urls.db containing url for all matches in season (scrapped using urls_scrapping.py script)
conn1 = sqlite3.connect("matches_urls.db")
c1 = conn1.cursor()
c3 = conn1.cursor()

c1.execute("SELECT * FROM urls")
conn1.commit()

#stats database opening, each club is represented by its own table (so there are 18 tables in total)
conn2 = sqlite3.connect("ekstraklasa.db")
c2 = conn2.cursor()

#webdriver initialization
driver = webdriver_init()

#####IMPORTANT!!! DEFINING ROUNDS THAT WILL BE SCRAPPED (numbers from 1 to 34 possible)######
rounds = list(range(1,35))
############################################################################

#main scrapping loop - scraps all matches for all teams for all defined above rounds
for r in rounds:
    #we are selecting only matches for current round that are not scrapped yet
    c1.execute(f"SELECT url FROM urls WHERE scrapped='N' and round = {r}")
    conn1.commit()
    
    #loop through all selected matches in current round
    for m in c1:
        #scrap stats for match
        stats_lists = match_scrap(driver, m[0])
        
        #save stats for both teams in ekstraklasa.db
        for team in stats_lists[::2]:
            
            #if table for current team doesn't exist
            c2.execute(f"CREATE TABLE IF NOT EXISTS {clubs_acrons[team[0]]} "
                      f"({stat_names[0]} INTEGER, "
                      f"{stat_names[1]} TEXT, "
                      f"{stat_names[2]} TEXT, "
                      f"{stat_names[3]} TEXT, "
                      f"{stat_names[4]} INTEGER, "
                      f"{stat_names[5]} INTEGER, "
                      f"{stat_names[6]} INTEGER, "
                      f"{stat_names[7]} INTEGER, "
                      f"{stat_names[8]} INTEGER, "
                      f"{stat_names[9]} INTEGER, "
                      f"{stat_names[10]} INTEGER, "
                      f"{stat_names[11]} INTEGER, "
                      f"{stat_names[12]} INTEGER, "
                      f"{stat_names[13]} INTEGER, "
                      f"{stat_names[14]} INTEGER, "
                      f"{stat_names[15]} INTEGER, "
                      f"{stat_names[16]} INTEGER, "
                      f"{stat_names[17]} INTEGER, "
                      f"{stat_names[18]} INTEGER, "
                      f"{stat_names[19]} REAL, "
                      f"{stat_names[20]} INTEGER);")
            conn2.commit()
    
            #adding row with stats
            query_item=f"INSERT INTO {clubs_acrons[team[0]]} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
            c2.execute(query_item, [r]+list(team[1:]))
            conn2.commit()
            
            #updating the matches_urls.db: scrapped = 'Y' for scrapped match
            c3.execute(f"UPDATE urls SET scrapped = 'Y' WHERE url = ?;", (m[0],))
            conn1.commit()
 

#closing webdriver and db connections
driver.quit()
conn1.close()
conn2.close()       







