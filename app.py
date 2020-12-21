#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
from sqlalchemy import and_
import sys, setuptools, tokenize
import re
import psycopg2
from sqlalchemy import func
import dateutil.parser
import babel
from flask import (Flask,
render_template,
request, Response,
flash, redirect,
url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form 
from forms import *
from flask_migrate import  Migrate ,MigrateCommand

from models import app, db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# TODO: connect to a local postgresql database

app = Flask(__name__)
moment = Moment(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/postgres'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object('config')
db.init_app(app)
db = SQLAlchemy(app)
migrate =Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.

#----------------------------------------------------------------------------#
#db.drop_all()
#db.create_all()
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)
app.jinja_env.filters['datetime'] = format_datetime
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def index():
  return render_template('pages/home.html')
#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #      num_shows should be aggregated based on number of upcoming shows p
  data1=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  locals = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  for place in places:
    locals.append({
        'city': place.city,
        'state': place.state,
        'venues': [{
            'id': venue.id,
            'name': venue.name,
        } for venue in venues if
            venue.city == place.city and venue.state == place.state]
    })


  return render_template('pages/venues.html', areas=locals);
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  name =request.form.get('search_term', '')
  mylist = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  return render_template('pages/search_venues.html', results=mylist, search_term=name,count=len(mylist))
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
  filter(Show.venue_id == venue_id,Show.artist_id == Artist.id,
        Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
    all()
  venue = Venue.query.filter(Venue.id==venue_id).first_or_404()
  print(venue)
  data = {
         "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
        'past_shows': [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

  return render_template('pages/show_venue.html', venue=data)
# Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  try:
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
    flash('  validate Thank You   .')
  except ValueError as e:
    print(e)
    flash(' Error  You input Invalidate Please Try again  .')
    db.session.rollback()
  finally:
    db.session.close()
  error=False;
  venue= Venue(
        name= request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        address= request.form['address'],
        phone = request.form['phone'],
        genres = request.form.getlist('genres'),
        website=request.form['website'],
        image_link =request.form['image_link'],
        seeking_description=request.form['seeking_description'],
        facebook_link = request.form['facebook_link']
       )
  if(request.form['seeking_description']!=None):
          venue.seeking_talent=True
  try:
        db.session.add(venue)
        db.session.commit()
  except:
        error=True
        db.session.rollback()
  finally:
        db.session.close()
  if error:
    #TODO: on unsuccessful db insert, flash an error instead.
       flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
       flash('Venue ' + request.form['name'] + ' was successfully listed!')
       return render_template('pages/home.html')
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error=False
  # TODO: Complete this endpoint for taking a venue_id, and using

    venue=Venue.query.get(venue_id)
    show= Show.query.filter(Show.venue_id==venue_id).delete()
    
    try:
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        flash('An error occurred. Venue '+ ' could not be Deleted.')
    finally:
        db.session.close()
    if error:
    #TODO: on unsuccessful db insert, flash an error instead.
      error=True
      flash('An error occurred. Venue '+ ' could not be Deleted.')
    else:
      flash('Venue ' + venue_id+ ' was successfully Deleted!')
      return render_template('pages/venues.html')
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage 
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.filter(Venue.id==venue_id).first();
  venue1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    error=False;
    venue=Venue.query.filter(Venue.id==venue_id).first()
    print(venue.name)
  # TODO: take values from the form submitted, and update existing
    venue.id=venue_id
    venue.name=request.form['name']
    venue.city=request.form['city']
    venue.state= request.form['state'] 
    venue.address=  request.form['address']
    venue.phone=request.form['phone']
    venue.genres= genres = request.form.getlist('genres')
    venue.website=request.form['website'],
    venue.seeking_description=request.form['seeking_description'],
    venue.image_link=request.form['image_link'],
    venue.facebook_link=request.form['facebook_link']
    if(len(request.form['seeking_description'])!=0):
        venue.seeking_talent=True
    try:     
        db.session.commit()
    except:
        error=True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
    #TODO: on unsuccessful db Edited, flash an error Edited.
      flash('An error occurred. Venue '+ ' could not be Edited.')
    else:
       flash('venue ' + request.form['name'] + ' was successfully Edited!')
       return redirect(url_for('show_venue', venue_id=venue_id))
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive
  try:
      name =request.form.get('search_term', '')
      artist=Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()
  except:
      flash('Artist Not Found')
  finally:
      return render_template('pages/search_artists.html', results=artist, search_term=name,count=len(artist))
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
  filter(Show.artist_id == artist_id,Show.venue_id == Venue.id,
        Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.artist_id == artist_id,
        Show.artist_id == Venue.id,
        Show.start_time > datetime.now()
    ).\
    all()
  artist = Artist.query.filter(Artist.id==artist_id).first_or_404()
  
  data = {
      "id": artist.id,
    "name": artist.name,
    "genres": artist.genres, 
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
        'past_shows': [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

  return render_template('pages/show_artist.html', artist=data)
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.filter(Artist.id==artist_id).first();
  artists={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artists)
  artist1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    artist=Artist.query.filter(Artist.id==artist_id).first();
 
    error=False;
    if(request.form['seeking_description']!=None):
          artist.seeking_venue=True
    artist.name =request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state'] 
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.website =request.form['website']
    artist.seeking_description=request.form['seeking_description']
    artist.facebook_link = request.form['facebook_link']
    artist.image_link =request.form['image_link']
    try:
        db.session.commit()
    except:
        error=True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
    #TODO: on unsuccessful db insert, flash an error edited.
      flash('An error occurred. Artist '+ ' could not be Edited.')
    else:
       flash('Artist ' + request.form['name'] + ' was successfully Edited!')
       return redirect(url_for('show_artist', artist_id=artist_id)) 
#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()

  return render_template('forms/new_artist.html', form=form)
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  try:
    artist = Artist()
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    flash('  validate Thank You   .')
  except ValueError as e:
    print(e)
    flash(' Error  You input Invalidate Please Try again  .')
    db.session.rollback()
  finally:
    db.session.close()
  error=False
  artist = Artist()
  if(request.form['seeking_description']!=None):
          artist.seeking_venue=True
  artist.name =request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state'] 
  artist.phone = request.form['phone']
  artist.genres = request.form.getlist('genres')
  artist.website =request.form['website']
  artist.seeking_description=request.form['seeking_description']
  artist.facebook_link = request.form['facebook_link']
  artist.image_link =request.form['image_link']
  try:
       
        db.session.add(artist)
        db.session.commit()
  except:
        error=True
        db.session.rollback()
            #TODO: on unsuccessful db insert, flash an error instead.

        flash('An error occurred. Venue '+request.form['name']+ ' could not be listed.')

  finally:
        db.session.close()
  if error:
    error=True
  else:
       flash('Artist ' + request.form['name'] + ' was successfully listed!')
       return render_template('pages/home.html')
#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows_list = Show.query.all()
  data = []
  for show in shows_list:
    if(show.upcoming):
      data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })
 
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/shows.html', shows=data)
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
   
  return render_template('forms/new_show.html', form=form)
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error=False
  form = ShowForm(request.form)
  try:
    show = Show()
    form.populate_obj(show)
    db.session.add(show)
    db.session.commit()
    flash('  validate Thank You   .')
  except ValueError as e:
    print(e)
    flash(' Error  You input Invalidate Please Try again  .')
    db.session.rollback()
  finally:
    db.session.close()
  new_show = Show()
  new_show.artist_id = request.form['artist_id']
  new_show.venue_id = request.form['venue_id']
  new_show.start_time = request.form['start_time']
 
  now = datetime.now()
  new_show.upcoming = (now < dateutil.parser.parse(str(new_show.start_time)))
  try:
    db.session.add(new_show)
    updated_artist = Artist.query.get(new_show.artist_id)
    updated_venue = Venue.query.get(new_show.venue_id)
    if(new_show.upcoming):
      updated_artist.upcoming_shows_count += 1;
      updated_venue.upcoming_shows_count += 1;
    else:
      updated_artist.past_shows_count += 1;
      updated_venue.past_shows_count += 1;
    db.session.commit()
        
  except:
        error=True
        db.session.rollback()
        flash('Venues ID or Artist ID Not Found Please Cheack Again!',category='error')
        return render_template('pages/home.html')
  finally:
        db.session.close()
  if error:
    #TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Shows could not be listed.')
  else:
       flash('Show was successfully listed!')
       return render_template('pages/home.html')

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/







@app.errorhandler(401)
def server_error(error):
    return render_template('errors/401.html'), 401
@app.errorhandler(422)
def server_error(error):
    return render_template('errors/422.html'), 422
@app.errorhandler(403)
def server_error(error):
    return render_template('errors/403.html'), 403
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(405)
def server_error(error):
    return render_template('errors/405.html'), 405
@app.errorhandler(409)
def server_error(error):
    return render_template('errors/409.html'), 409
@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500



if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
