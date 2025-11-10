from flask_sqlalchemy import SQLAlchemy
import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define the Draw model
class Draw(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key

    # Dates for the draw
    draw_date_rolled = db.Column(db.DateTime, nullable=False)  # Date when the draw was rolled
    draw_date = db.Column(db.DateTime, default=datetime.datetime.now)  # Date when the draw was saved

    # JSON fields for the draw sets
    draw_set_1 = db.Column(db.JSON, nullable=False)
    draw_set_2 = db.Column(db.JSON, nullable=False)
    draw_set_3 = db.Column(db.JSON, nullable=False)
    draw_set_4 = db.Column(db.JSON, nullable=False)