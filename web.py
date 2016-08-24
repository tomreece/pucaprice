import datetime
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#
# Models
#

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    pucatrade_id = db.Column(db.Integer)
    name = db.Column(db.String)

class Price(db.Model):
    __tablename__ = "prices"

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"))
    normal = db.Column(db.Integer)
    foil = db.Column(db.Integer)
    created = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    card = db.relationship("Card", primaryjoin=(card_id == Card.id), backref=db.backref("card", lazy="dynamic"))

#
# Routes
#

@app.route("/hello")
def hello():
    return "hello, i am alive"

@app.route("/scraper/add", methods=["POST"])
def scraper_add():
    data = request.json
    card = Card.query.filter_by(pucatrade_id=data["pucatrade_id"]).first()
    if not card:
        card = Card()
        card.pucatrade_id = data["pucatrade_id"]
        card.name = data["name"]
        db.session.add(card)
        db.session.commit()
    price = Price()
    price.card_id = card.id
    price.normal = data["normal_price"]
    price.foil = data["foil_price"]
    db.session.add(price)
    db.session.commit()
    return jsonify({ "success": True })

#
# Main
#

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")