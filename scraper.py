from __future__ import print_function
import requests
from bs4 import BeautifulSoup

RANGE = 32671

for pucatrade_id in range(1, RANGE + 1):
    try:
        r = requests.get("https://pucatrade.com/cards/show/{}".format(pucatrade_id))
        soup = BeautifulSoup(r.text, "html.parser")

        card_name = soup.find("h1", class_="title").text
        set_name = soup.find("div", class_="type").find("a").find("span").text
        # PucaTrade has uses the class "have" for both have and want counts
        #have_wants = soup.find_all("div", class_="have")
        normal_price = soup.find("div", class_="price").find("label", class_="on")
        if normal_price:
            normal_price = normal_price.text.replace(",", "")
        #normal_haves = have_wants[0].text.replace(" HAVES", "")
        #normal_wants = have_wants[1].text.replace(" WANTS", "")
        foil_price = soup.find("div", class_="price").find("label", class_="off")
        if foil_price:
            foil_price = foil_price.text.replace(",", "")
        #foil_haves = have_wants[2].text.replace(" HAVES", "")
        #foil_wants = have_wants[3].text.replace(" WANTS", "")

        if normal_price == "N/A":
            normal_price = None

        if foil_price == "N/A":
            foil_price = None

        # if normal_haves and int(normal_haves) < 0:
        #     normal_haves = 0

        # if normal_wants and int(normal_wants) < 0:
        #     normal_wants = 0

        # if foil_haves and int(foil_haves) < 0:
        #     foil_haves = 0

        # if foil_wants and int(foil_wants) < 0:
        #     foil_wants = 0

        # todo: normal_price and foil_price should be made int() earlier
        card = {
            "card_name": card_name,
            "set_name": set_name,
            "pucatrade_id": pucatrade_id,
            "normal_price": normal_price,
            "normal_haves": None,
            "normal_wants": None,
            "foil_price": foil_price,
            "foil_haves": None,
            "foil_wants": None
        }

        r2 = requests.post("http://pucaprice.herokuapp.com/scraper/add", json=card)

        print(card)
    except Exception:
        pass
