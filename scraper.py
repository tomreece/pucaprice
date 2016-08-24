from __future__ import print_function
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

RANGE = 32047

sched = BlockingScheduler()

@sched.scheduled_job("interval", days=1)
def scrape():
    for pucatrade_id in range(1, RANGE + 1):
        try:
            r = requests.get("https://pucatrade.com/cards/show/{}".format(pucatrade_id))
            soup = BeautifulSoup(r.text, "html.parser")

            card_name = soup.find("h1", class_="title").text
            set_name = soup.find("div", class_="type").find("a").find("span").text
            prices = soup.find_all("div", class_="price small")
            # PucaTrade has uses the class "have" for both have and want counts
            have_wants = soup.find_all("div", class_="have")
            normal_price = prices[0].text.replace(",", "")
            normal_haves = have_wants[0].text.replace(" HAVES", "")
            normal_wants = have_wants[1].text.replace(" WANTS", "")
            foil_price = prices[1].text.replace(",", "")
            foil_haves = have_wants[2].text.replace(" HAVES", "")
            foil_wants = have_wants[3].text.replace(" WANTS", "")

            if normal_price == "N/A":
                normal_price = None

            if foil_price == "N/A":
                foil_price = None

            card = {
                "card_name": card_name,
                "set_name": set_name,
                "pucatrade_id": pucatrade_id,
                "normal_price": normal_price,
                "normal_haves": normal_haves,
                "normal_wants": normal_wants,
                "foil_price": foil_price,
                "foil_haves": foil_haves,
                "foil_wants": foil_wants
            }

            r2 = requests.post("http://pucaprice.herokuapp.com/scraper/add", json=card)

            print(card)
        except Exception:
            pass

# Scrape on startup
scrape()

# Then scrape on a schedule
sched.start()
