#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_migrate import Migrate

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from Models import *
from sqlalchemy.sql import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# local postgresql database
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)






#filters

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime




@app.route('/')
def index():
  return render_template('pages/home.html')


#MyVenue page
@app.route('/venues')
def venues():
  # All records of Venues, if error occurs while loading page 
  # flash(Please try again. Unable to show Venues at the moment, due to an error)
  try:
    MyvenueSearch = Venue.query.distinct(Venue.city, Venue.state).all()
    details = []
    for f in MyvenueSearch:
      M_venueItem ={}
      M_venueItem['city'] = f.city
      M_venueItem['state'] = f.state

      Listvenues = []
      data_Venue = Venue.query.filter(
        Venue.state == f.state, Venue.city == f.city).all()    
  
      for Showvenue in data_Venue:
        P_VenueShown = {}
        P_VenueShown['id'] = Showvenue.id
        P_VenueShown['name'] = Showvenue.name
        P_VenueShown['num_upcoming_shows'] = Show.query.filter()
        Listvenues.append(P_VenueShown)
      M_venueItem['venues'] = Listvenues
      details.append(M_venueItem)
  except:
    flash(
      f"Please try again. Unable to show Venues at the moment, due to an error", category="error")
    abort(500)
  finally:
    return render_template('pages/venues.html', areas=details)
        
    
@app.route('/venues/search', methods=['POST'])
def search_venues():

#Venue query search bar
  Samplevenue_search = request.form.get('search_term','')
  My_venues = (db.session.query(Venue).filter( Venue.name.ilike(f"%{Samplevenue_search}%") |
   Venue.city.ilike(f"%{Samplevenue_search}%") | Venue.state.ilike(f"%{Samplevenue_search}%")).all()) 
  response = { "count": len(My_venues), "details": [] } 

  for l in My_venues: 
    D_venue_dict = {} 
    D_venue_dict["id"] = l.id
    D_venue_dict["name"] = l.name 
    num_upcoming_shows = 0  

    for show in l.shows:
      if show.start_time > datetime.now(): 
        num_upcoming_shows =+ 1
      D_venue_dict["num_upcoming_shows"] = num_upcoming_shows
    response["details"].append(D_venue_dict)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  InfoVenue = Venue.query.get(venue_id)
  
  # Detail of each Venue ID
  details ={
    "id": InfoVenue.id,
    "name": InfoVenue.name,
    "genres": InfoVenue.genres.split(','),
    "address": InfoVenue.address,
    "city": InfoVenue.city,
    "state": InfoVenue.state,
    "phone": InfoVenue.phone,
    "website_link": InfoVenue.website_link,
    "facebook_link": InfoVenue.facebook_link,
    "seeking_venue": InfoVenue.seeking_venue,
    "seeking_description": InfoVenue.seeking_description,
    "image_link": InfoVenue.image_link,
    # "Display_past_shows": [],
    # "Display_upcoming_shows": [],
    # "Display_past_shows_count": [],
    # "Display_upcoming_shows_count": [],
  }

  Display_past_shows = []
  Display_upcoming_shows= []
  Display_past_shows_count= []
  Display_upcoming_shows_count = []
# Records based on past shows
  Display_past_shows =db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  
# Records based on upcoming shows
  Display_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  
# Number of upcoming and past shows
  details["Display_upcoming_shows_count"] = Show.query.filter(Show.venue_id==venue_id, Show.start_time<func.now()).count()
  details["Display_past_shows_count"] = Show.query.filter(Show.venue_id==venue_id, Show.start_time<func.now()).count()


  return render_template('pages/show_venue.html', venue=details)

#creating a Venue
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Validating and creating a new Venue record, if records are valid,
  # create and return 'was successfully listed' if not return 'An error occured'
  form = VenueForm(request.form)
  if form.validate:
    try:
      Newvenue = Venue(name=request.form['name'],city=request.form['city'], state=request.form['state'],address=request.form['address'],phone=request.form['phone'],
        genres=", ".join(request.form.get('genres')), image_link=request.form['image_link'], facebook_link=request.form['facebook_link'], 
        website_link=request.form['website_link'],seeking_venue=request.form.get('seeking_venue'),seeking_description=request.form['seeking_description'])
      db.session.add(Newvenue)
      db.session.commit();
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')    
    finally:
      db.session.close()
  else:
    flash('An error occurred. Venue ')
  return render_template('pages/home.html')
 

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  
  #Deleting a Venue
  error=False
  try:
    venue_to_delete =Venue.query.get(venue_id)
    db.session.delete(venue_to_delete)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred')
  else:
    flash('Deleted Successfully')
    return render_template('pages/home.html')

#Artist page
@app.route('/artists')
def artists():
  #All records of Artists
  details= db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=details)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  #Artist query search bar
  ArtistSearch = request.form.get('search_term','')
  artists = (db.session.query(Artist).filter( Artist.name.ilike(f"%{ArtistSearch}%") |
   Artist.city.ilike(f"%{ArtistSearch}%") | Artist.state.ilike(f"%{ArtistSearch}%")).all()) 
  response = { "count": len(artists), "details": [] } 

  for artist in artists: 
    Sample_artist_list = {} 
    Sample_artist_list["id"] = artist.id
    Sample_artist_list["name"] = artist.name 
    Display_upcoming_shows = 0  

    for show in artist.shows:
      if show.start_time > datetime.now(): 
        Display_upcoming_shows =+ 1
      Sample_artist_list["Display_upcoming_shows"] = Display_upcoming_shows
    response["details"].append(Sample_artist_list)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Views the artist page with the given artist_id
  viewArtist = Artist.query.get(artist_id)
  setattr(viewArtist, "genres", viewArtist.genres.split(","))

  #View the past shows
  Display_past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()

  shows_list = []
  for show in Display_past_shows:
    ShowL = {}
    ShowL["venue_name"] = show.venues.name
    ShowL["venue_id"] = show.venues.id
    ShowL["venue_image_link"] = show.venues.image_link
    ShowL["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    shows_list.append(ShowL)
  setattr(viewArtist, "Display_past_shows", shows_list)
  setattr(viewArtist, "Display_past_shows_count", len(shows_list))

  #View the upcoming shows
  Display_upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()

  shows_list = []
  for show in Display_upcoming_shows:
    ShowL = {}
    ShowL["venue_name"] = show.venues.name
    ShowL["venue_id"] = show.venues.id
    ShowL["venue_image_link"] = show.venues.image_link
    ShowL["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    shows_list.append(ShowL)
  setattr(viewArtist, "Display_upcoming_shows", shows_list)
  setattr(viewArtist, "Display_upcoming_shows_count", len(shows_list))


  return render_template('pages/show_artist.html', artist=viewArtist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  # Getting an Artist details through its ID and updating it
  artistUpdate = Artist.query.get(artist_id)
  form.genres.details = artistUpdate.genres.split(",")
  return render_template('forms/edit_artist.html', form=form, artist=artistUpdate)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Updating Artist using the info from the edit artist page
  form = ArtistForm(request.form)
  if form.validate:
    try:
      artist = Artist.query.get(artist_id)
      if request.form.get('seeking_venue'):
        seeking_venue=1
      else:
        seeking_venue = 0
      artist.name = request.form['name']
      artist.city=request.form['city']
      artist.state=request.form['state']
      artist.phone=request.form['phone']
      artist.image_link=request.form['image_link']
      artist.facebook_link=request.form['facebook_link']
      artist.website_link=request.form['website_link']
      artist.seeking_venue=seeking_venue
      artist.seeking_description=request.form['seeking_description']
      artist.genres=", ".join(request.form.get('genres'))
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully Updated!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    flash('An error occurred.')

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
   #Editing a particular venue with the with an ID
  Venue_data = Venue.query.get(venue_id)
  demo_edit_venue={
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

  return render_template('forms/edit_venue.html', form=form, venue=Venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Taking values from the form submitted, and update existing details
  form = VenueForm(request.form)
  if form.validate:
    try:
      venue = Venue.query.get(venue_id)
      if request.form.get('seeking_venue'):
        seeking_venue=1
      else:
        seeking_venue = 0
      venue.name = request.form['name']
      venue.address=request.form['address']
      venue.city=request.form['city']
      venue.state=request.form['state']
      venue.phone=request.form['phone']
      venue.image_link=request.form['image_link']
      venue.facebook_link=request.form['facebook_link']
      venue.website_link=request.form['website_link']
      venue.seeking_venue=seeking_venue
      venue.seeking_description=request.form['seeking_description']
      venue.genres=", ".join(request.form.get('genres'))
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully Updated!')
    except:
      db.session.rollback()
      flash('An error occurred. could not be edited')
    finally:
      db.session.close()
  else:
    flash('An error occurred. Venue ')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  #Validating and creating a new  Artist
  form = ArtistForm(request.form)
  if form.validate:
    try:
      Newartist = (Artist(name=form.name.details,city=form.city.details,state=form.state.details,phone=form.phone.details,
        image_link=form.image_link.details,facebook_link=form.facebook_link.details,website_link=form.website_link.details,
        seeking_venue=form.seeking_venue.details,seeking_description=form.seeking_description.details,genres=", ".join(form.genres.details)))
      db.session.add(Newartist)
      db.session.commit();
      flash('Artist ' + request.form['name'] + ' was created successfully')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be created.')
    finally:
      db.session.close()
  else:
    flash('Please try again, An error occurred.')
  
  return render_template('pages/home.html')

  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # Displays shows list
  details = []
  showsView = Show.query.all()
  for show in showsView:
    ShowList={}
    ShowList['venue_id'] = show.venues.id
    ShowList['venue_name'] = show.venues.name
    ShowList['artist_id'] = show.artists.id
    ShowList['artist_name'] = show.artists.name
    ShowList['artist_image_link'] = show.artists.image_link
    ShowList["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    details.append(ShowList)
  demodata=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }]
  return render_template('pages/shows.html', shows=details)

@app.route('/shows/create')
def create_shows():
  
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  #  New Show records
  new_show_artist = db.session.query(Artist).filter(Artist.id==request.form.get('artist_id')).count()
  new_show_venue = db.session.query(Venue).filter(Venue.id==request.form.get('venue_id')).count()
  
  form = ShowForm(request.form)
  if form.validate:
    if new_show_artist == 0 or new_show_venue ==0:
      flash('An error occurred. Venue ID or Artist ID are invalid.')
    else:
      try:
        shows = Show(artist_id=request.form.get('artist_id'),venue_id=request.form.get('venue_id'),start_time=request.form.get('start_time'))
        db.session.add(shows)
        db.session.commit();

        flash('Show was successfully listed!')
      except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      finally:
        db.session.close()
  else:
    flash('An error occurred. Show could not be listed.')
     
  return render_template('pages/home.html')

 


#Error handler for error404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

#Error handler for error500
@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

#File Handler
if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


# Launch

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''