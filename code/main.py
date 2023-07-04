import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time 
import json 
from selenium.common.exceptions import ElementClickInterceptedException
import subprocess
from pathlib import Path
import os 

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-crash-reporter")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-in-process-stack-traces")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--log-level=3")
# chrome_options.add_argument("--window-size=1366,768")
chrome_options.add_argument('--disable-dev-shm-usage')        

WRITE_LOCATION = "/mnt/wsop/"
COLLECTION_URL = os.environ["COLLECTION_URL"]
def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response


chrome_options.set_capability('goog:loggingPrefs', {"performance": "ALL"})
driver = webdriver.Remote(os.environ["HUB_URL"], options=chrome_options)
# driver = webdriver.Chrome("C:\\chromedriver.exe", options=chrome_options)

driver.get("https://www.pokergo.com/login")

# driver.find_element("xpath", "//button[@class='Cookie__button']").click() # accept the cookies 
driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", "cookie:accepted", "true")

driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", "jwplayer.qualityLabel", "1080p")
driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", "jwplayer.bandwidthEstimate", "100000000") # 100MB ? 
driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", "jwplayer.bitrateSelection", "5000000")


driver.find_element("id", "username-input").send_keys(os.environ["USERNAME"])
driver.find_element("id", "password-input").send_keys(os.environ["PASSWORD"])
driver.find_element("id", "password-input").submit()
time.sleep(5)

remaining = True
failed = False
failed_count = 0 
index = 0
driver.get(COLLECTION_URL) 
time.sleep(2)

queued_downloads = []
try:
    while remaining:
        driver.get(COLLECTION_URL)
        time.sleep(5)
        episode_container = driver.find_element("xpath", "//div[@class='container']")
        episodes = episode_container.find_elements("xpath", "//div[@class='row-wrapper row-with-margin']")

        try:
            episode = episodes[index]
        except:
            remaining = False
            break 

        title = episode.text
        title = title.split("\n")
        for row in title:
            frags = row.split("|")
            if len(frags) > 0:
                if len(frags) == 2:
                    event_name = frags[0]
                    episode_name = frags[1]
                elif len(frags) == 3:
                    event_name = frags[0]
                    episode_name = frags[2]
                break
        print(episode_name)
        # something weird happens when the element to click is /just/ on the page
        if failed:
            driver.find_element("xpath", "//body").send_keys(Keys.END)
            time.sleep(5)
            failed = False
        try:
            # if the page needs to scroll, the element won't be cliclable right away
            episode.click()
        except ElementClickInterceptedException:
            time.sleep(2)
            episode.click()


        # the video player will (possibly?) select the best quality for the connection. Give it time to select the best
        time.sleep(20) 

        # get network logs 
        browser_log = driver.get_log('performance') 
        events = [process_browser_log_entry(entry) for entry in browser_log]
        events = [event for event in events if 'Network.responseReceived' in event['method']]

        last_event = ""
        for event in events:
            # print(event)
            if "response" in event["params"]:
                # assuming the video player will only improve quality, get the last record for the m3u8 
                if ".m3u8" in event["params"]["response"]["url"] and not "ping.gif" in event["params"]["response"]["url"]:
                    last_event = event["params"]["response"]["url"]
        if last_event != "":
            queued_downloads.append(["yt-dlp", "-o", f"{WRITE_LOCATION}{event_name.strip()}/{episode_name.strip()}.mp4", last_event]) 
        else:
            failed = True
            failed_count+=1
            if failed_count > 5:
                # can't download this episode - why? Have seen some just don't load. 
                index+=1
                failed = False
            continue
                
        driver.back()
        time.sleep(5) # give the back time to do it's thing. We will re-load the page anyway
        index+=1
    finally:
        driver.quit()
for item in queued_downloads:
    subprocess.call(item)
