from __future__ import print_function
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

#RANGE = 32047
RANGE = 10

sched = BlockingScheduler()

@sched.scheduled_job("interval", minutes=1)
def scrape():
    for pucatrade_id in range(1, RANGE + 1):
        r = requests.get("https://pucatrade.com/cards/show/{}".format(pucatrade_id))
        soup = BeautifulSoup(r.text, "html.parser")

        card_name = soup.find("h1", class_="title").text
        prices = soup.find_all("div", class_="price small")
        normal_price = prices[0].text
        foil_price = prices[1].text

        if normal_price = "N/A":
            normal_price = None

        if foil_price == "N/A":
            foil_price = None

        card = {
            "name": card_name,
            "pucatrade_id": pucatrade_id,
            "normal_price": normal_price,
            "foil_price": foil_price
        }

        r2 = requests.post("http://pucaprice.herokuapp.com/scraper/add", json=card)

        print(card)
        print(r2.status_code)

sched.start()
