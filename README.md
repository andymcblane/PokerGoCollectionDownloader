# PokerGoCollectionDownloader

PokerGo seem to think it's an OK UX to intrude on the video player (despite being a paying customer!)

Let's just download the mp4 files directly and serve them ourselves. 

## Prerequisites 

* Remote Selenium Grid (see https://github.com/SeleniumHQ/docker-selenium)
* Premium PokerGo account


## Environment Variables 

* COLLECTION_URL see collections secition below 
* USERNAME - PokerGo username
* PASSWORD - PokerGo password
* HUB_URL - URL of Selenium Hub

## PokerGo Collections 

At present, this code only supports downloading collections from PokerGo (and specifically only the list-type. Not where the videos are arranged in a scrolling left-right element)

Collections can be found from the home page - e.g https://www.pokergo.com/collections/4ef68d38-76f5-435a-8d65-ad374bed7a26
