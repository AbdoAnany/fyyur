from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(200))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    website = db.Column(db.String(120),nullable=True)
    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    shows = db.relationship('Show',backref='venue',lazy=True,)
    def __repr__(self):
        return f'<Venue {self.id}, {self.name},{self.city},{self.state},{self.genres},{self.address},{self.phone},{self.facebook_link}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres =  db.Column(db.ARRAY(db.String),nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120),nullable=True)
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    shows = db.relationship('Show',backref='artist',lazy=True,)

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
    upcoming = db.Column(db.Boolean, nullable=False, default=True)
    def __repr__(self):
        return f'<Show {self.id}, {self.venue_id},{self.artist_id},{self.start_time}>'
