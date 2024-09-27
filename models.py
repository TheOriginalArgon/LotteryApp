from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Draw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    draw_date = db.Column(db.DateTime, default=datetime.datetime.now)

    draw_set_1 = db.Column(db.JSON, nullable=False)
    draw_set_2 = db.Column(db.JSON, nullable=False)
    draw_set_3 = db.Column(db.JSON, nullable=False)
    draw_set_4 = db.Column(db.JSON, nullable=False)