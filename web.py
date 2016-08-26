import datetime
import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)
db = SQLAlchemy(app)

#
# Models
#

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    pucatrade_id = db.Column(db.Integer)
    name = db.Column(db.String)
    set_name = db.Column(db.String)

class Price(db.Model):
    __tablename__ = "prices"

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"))
    normal = db.Column(db.Integer)
    normal_haves = db.Column(db.Integer)
    normal_wants = db.Column(db.Integer)
    foil = db.Column(db.Integer)
    foil_haves = db.Column(db.Integer)
    foil_wants = db.Column(db.Integer)
    created = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    card = db.relationship("Card", primaryjoin=(card_id == Card.id), backref=db.backref("card", lazy="dynamic"))

#
# Routes
#

@app.route("/")
def hello():
    return "hello, i am alive"

@app.route("/scraper/add", methods=["POST"])
def scraper_add():
    data = request.json
    card = Card.query.filter_by(pucatrade_id=data["pucatrade_id"]).first()
    if not card:
        card = Card()
        card.pucatrade_id = data["pucatrade_id"]
        card.name = data["card_name"]
        card.set_name = data["set_name"]
        db.session.add(card)
        db.session.commit()
    price = Price()
    price.card_id = card.id
    price.normal = data["normal_price"]
    price.normal_haves = data["normal_haves"]
    price.normal_wants = data["normal_wants"]
    price.foil = data["foil_price"]
    price.foil_haves = data["foil_haves"]
    price.foil_wants = data["foil_wants"]
    db.session.add(price)
    db.session.commit()
    return jsonify({ "success": True })

#
# Templates
#

@app.route("/card/<int:id>")
def card_id(id):
    return render_template("test.html", id=id)

#
# API
#

@app.route("/api/v1/search/<string:query>")
def api_v1_search(query):
    if len(query) < 3:
        return error_response(400, "Please enter 3 or more characters.")
    cards = Card.query.filter(Card.name.ilike("%{}%".format(query))).all()
    return jsonify({ "results": [card_to_dict(card) for card in cards] })

@app.route("/api/v1/card/<int:id>")
def api_v1_card(id):
    card = Card.query.get(id)
    prices = Price.query.filter_by(card_id=card.id).order_by(Price.id).all()
    return jsonify({
        "card": {
            "name": card.name,
            "set_name": card.set_name,
            "url": "https://pucatrade.com/cards/show/{}".format(card.pucatrade_id)
        },
        "dates": [price.created.strftime("%Y-%m-%d") for price in prices],
        "prices": [{ "normal": price.normal, "foil": price.foil } for price in prices],
        "haves": [{ "normal": price.normal_haves, "foil": price.foil_haves } for price in prices],
        "wants": [{ "normal": price.normal_wants, "foil": price.foil_wants } for price in prices]
    })


#
# Helpers
#

def error_response(status, error):
    resp = jsonify({ "error": error })
    resp.status_code = status
    return resp

def card_to_dict(card):
    price = Price.query.filter_by(card_id=card.id).order_by(Price.id.desc()).first()

    d = {
        "id": card.id,
        "name": card.name,
        "set_name": card.set_name,
        "url": "https://pucatrade.com/cards/show/{}".format(card.pucatrade_id)
    }

    if price:
        d["prices"] = {
            "normal": price.normal,
            "foil": price.foil
        }

        d["haves"] = {
            "normal": price.normal_haves,
            "foil": price.foil_haves
        }

        d["wants"] = {
            "normal": price.normal_wants,
            "foil": price.foil_wants
        }

    return d


#
# Main
#

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")