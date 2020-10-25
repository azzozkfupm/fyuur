#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="Venue", lazy=True)
    def __repr__(self):
      return '<Venue name:{}>'.format(self.name)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="Artist", lazy=True)


    def __repr__(self):
      return '<Artist name:{}>'.format(self.name)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)


  def __repr__(self):
    return '<Show artist:{} venue:{} start date and time: {}'.format(self.artist_id,self.venue_id,self.start_time)

#----------------------------------------------------------------------------#
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
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data=[]
  areas = db.session.query(func.count(Venue.id),Venue.state,Venue.city).group_by(Venue.state,Venue.city).all()
  
  for area in areas:
    all_venues = db.session.query(Venue).filter_by(state=area.state).filter_by(city=area.city).all()
    venues = []
    for venue in all_venues:

     venues.append({
       "id": venue.id,
       "name": venue.name,
       "num_upcoming_shows": db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time > datetime.now()).count()
     }) 

    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venues 
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')

  search_term = search_term.casefold()
  venues = db.session.query(Venue).all()
  response = {}
  data = []
  upcoming_shows = []
  past_shows = []
  count = 0
  for venue in venues:
    name = venue.name
    name = name.casefold()

    if(name.rfind(search_term) > -1):
      count += 1
      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time > datetime.now()).count()
      })

  response= {
    "count": count,
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  
  past_shows_list = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<=datetime.now()).all()
  upcoming_shows_list = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  past_shows =[]
  upcoming_shows = []

  for show in upcoming_shows_list:
    
    
    upcoming_shows.append({
      "artist_id": show.Artist.id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in past_shows_list:
    past_shows.append({
      "artist_id": show.Artist.id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S') 
      })

 
  data ={
      "id": venue.id,
      "name":venue.name,
      "genres":venue.genres,
      "address":venue.address,
      "city": venue.city,
      "state":venue.state,
      "phone":venue.phone,
      "website":venue.website,
      "facebook_link":venue.facebook_link,
      "seeking_talent":venue.seeking_talent,
      "seeking_description":venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows":past_shows,
      "upcoming_shows":upcoming_shows,
      "num_past_shows": len(past_shows),
      "num_upcoming_shows": len(upcoming_shows)

  }

  

  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False

  try:
    name = request.form['name']
    state = request.form['state']
    city = request.form['city']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website = request.form['website']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description']


    venue = Venue(name=name,city=city,state=state,address=address,phone=phone,genres=genres,facebook_link=facebook_link,website=website,seeking_talent=seeking_talent,seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  
  except:

    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db insert, flash success
  if error:
    flash('An error occured. Venue' + request.form['name'] + ' couldnt be listed')
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()


  if error:
    flash('An error occured. Venue' + request.form['name'] + ' couldnt be listed')
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = db.session.query(Artist).all()
  data = []

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    }
    )
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term','')

  
  search_term = search_term.casefold()
  artists = db.session.query(Artist).all()
  response = {}
  data = []
  upcoming_shows = []
  count = 0
  for artist in artists:
    name = artist.name
    name = name.casefold()

    if(name.rfind(search_term) > -1):
      count += 1
      data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time > datetime.now()).count()
      })

  response= {
    "count": count,
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist = db.session.query(Artist).filter_by(id=artist_id).first()

  upcoming_shows_list = db.session.query(Show).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now())
  past_shows_list = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time <= datetime.now())

  upcoming_shows = []
  past_shows = []

  for show in upcoming_shows_list:
    upcoming_shows.append({
      "venue_id": show.Venue.id,
      "venue_name": show.Venue.name,
      "venue_image_link": show.Venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in past_shows_list:
    past_shows.append({
      "venue_id": show.Venue.id,
      "venue_name": show.Venue.name,
      "venue_image_link": show.Venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  data={
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
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  error = False
  artist = db.session.query(Artist).filter_by(id=artist_id).first()
  if artist:
    form.name.data= artist.name
    form.genres.data = artist.genres
    form.city.data= artist.city
    form.state.data= artist.state
    form.phone.data= artist.phone
    form.website.data= artist.website
    form.facebook_link.data= artist.facebook_link
    form.seeking_venue.data= artist.seeking_venue
    form.seeking_description.data= artist.seeking_description
    form.image_link.data= artist.image_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  error = False
  artist = db.session.query(Artist).filter_by(id=artist_id).first()

    
  try:
    artist.name = request.form['name']
    artist.genres = request.form.getlist('genres')
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone= request.form['phone']
    artist.website = request.form['website']
    artist.facebook_link=request.form['facebook_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']
    artist.image_link= request.form['image_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    flash('An error occured. Artist' + request.form['name'] + ' couldnt be listed')
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  if venue:
    form.name.data= venue.name
    form.genres.data= venue.genres
    form.address.data= venue.address
    form.city.data= venue.city
    form.state.data= venue.state
    form.phone.data= venue.phone
    form.website.data= venue.website
    form.facebook_link.data= venue.facebook_link
    form.seeking_talent.data= venue.seeking_talent
    form.seeking_description.data= venue.seeking_description
    form.image_link.data= venue.image_link
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  
  error = False
  venue = db.session.query(Venue).filter_by(id=venue_id).first()

    
  try:
    venue.name = request.form['name']
    venue.genres = request.form.getlist('genres')
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone= request.form['phone']
    venue.address = request.form['address']
    venue.website = request.form['website']
    venue.facebook_link=request.form['facebook_link']
    venue.seeking_venue = True if 'seeking_venue' in request.form else False
    venue.seeking_description = request.form['seeking_description']
    venue.image_link= request.form['image_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    flash('An error occured. Venue' + request.form['name'] + ' couldnt be listed')
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')


  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False

  try:
    name = request.form['name']
    state = request.form['state']
    city = request.form['city']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website = request.form['website']
    seeking_venue = True if 'seeking_venue' in request.form else False
    seeking_description = request.form['seeking_description']

  
    artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,website=website,seeking_venue=seeking_venue,seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  
  except:

    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db insert, flash success
  if error:
    flash('An error occured. Artist' + request.form['name'] + ' couldnt be listed')
  if not error:
    flash('Artist' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = db.session.query(Show).join(Venue).join(Artist).all()
  data = []
  for show in shows:
    data.append({
    "venue_id": show.venue_id,
    "venue_name": show.Venue.name,
    "artist_id": show.Artist.id,
    "artist_name": show.Artist.name,
    "artist_image_link": show.Artist.image_link,
    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')      
    })
 
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
  error = False

  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']



    show = Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
  
  except:

    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db insert, flash success
  if error:
    flash('Show was not successfully listed!')
  if not error:
    flash('Show was successfully listed!')

  # on successful db insert, flash success
 
  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

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
