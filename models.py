from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tags = db.Column(db.String(120), nullable=False)
    summary = db.Column(db.String(250), nullable=False)
    details = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(250), nullable=False)
    related = db.Column(db.String(250), nullable=True)
    priority = db.Column(db.String(2), nullable=False)
