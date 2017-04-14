#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import pdb
import os
import re
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from dateutil.parser import parse
from datetime import datetime

def not_date(string):
    try: 
        parse(string)
        return False
    except ValueError:
        return True

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
DEBUG = True

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.135.151/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@104.196.135.151/proj1part2"
#
DATABASEURI = "postgresql://jk3655:5537@104.196.135.151/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM artists_lived")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#




# artists page
@app.route('/artists')
def artists():
  cursor = g.conn.execute("SELECT name FROM artists_lived")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("artists.html", **context)

# curators page
@app.route('/curators')
def curators():
  cursor = g.conn.execute("SELECT name FROM curators_lived")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("curators.html", **context)

# exhibitions page
@app.route('/exhibitions')
def exhibitions():
  cursor = g.conn.execute("SELECT title FROM exhibitions_exhibited")
  names = []
  for result in cursor:
    names.append(result['title'])  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("exhibitions.html", **context)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

# -------------------------- 
@app.route('/getArtistsInfo', methods=['POST'])
def getArtistsInfo():
 # pdb.set_trace()
  name = request.form['name']
  cursor = g.conn.execute(
    "SELECT * FROM artists_lived a WHERE a.name=%s", 
    name)
  artistsInfo = []
  print(cursor)
  artistsInfo = cursor.fetchall()
  cursor.close()

  cursor3 = g.conn.execute(
    "SELECT * FROM artistprofiles_isrec p WHERE p.a_id = (SELECT a_id FROM artists_lived a WHERE a.name=%s)",
    name)
  artistProfilesInfo = []
  artistProfilesInfo = cursor3.fetchall()
  cursor3.close()

  cursor2 = g.conn.execute(
    "SELECT * FROM artists_lived a, featured_in f, exhibitions_exhibited e, artistprofiles_isrec p WHERE a.name=%s AND a.a_id=f.a_id AND f.e_num=e.e_num AND a.a_id = p.a_id", 
    name)
  exhibitionsInfo = []
  exhibitionsInfo = cursor2.fetchall()
  cursor2.close()

  context = dict(data = artistsInfo, dataAProfiles = artistProfilesInfo, dataExhibits = exhibitionsInfo)
  return render_template("getArtistsInfo.html", **context)

# for searching curators
@app.route('/getCuratorsInfo', methods=['POST'])
def getCuratorsInfo():
  name = request.form['name']
  # cursor = g.conn.execute("SELECT * FROM artists_lived a WHERE a.name=%s", name)
  cursor = g.conn.execute(
    "SELECT * FROM curators_lived c WHERE c.name=%s", 
    name)
  curatorsInfo = []
  curatorsInfo = cursor.fetchall()
  cursor.close()
  
  cursorExhibits = g.conn.execute(
    "SELECT e.title FROM curators_lived c, directed d, exhibitions_exhibited e WHERE c.name=%s AND c.c_id=d.c_id AND d.e_num=e.e_num", 
    name)
  curatorsExhibition = []
  curatorsExhibition = cursorExhibits.fetchall()
  cursorExhibits.close()

  context = dict(dataInfo = curatorsInfo, dataExhibit = curatorsExhibition)
  return render_template("getCuratorsInfo.html", **context)

# searching exhibitions
@app.route('/getExhibitionsInfo', methods=['POST'])
def getExhibitionsInfo():
  name = request.form['name']
  # cursor = g.conn.execute("SELECT * FROM artists_lived a WHERE a.name=%s", name)
  # basic info
  cursor = g.conn.execute(
    "SELECT * FROM exhibitions_exhibited e WHERE e.title=%s", 
    name)
  exhibitionsInfo = []
  exhibitionsInfo = cursor.fetchall()
  cursor.close()

  # curators featured
  cursor2 = g.conn.execute(
    "SELECT c.name FROM exhibitions_exhibited e, directed d, curators_lived c WHERE e.title=%s AND e.e_num=d.e_num AND d.c_id=c.c_id", 
    name)
  curatorsFeatured = []
  curatorsFeatured = cursor2.fetchall()
  cursor2.close()

  # artists featured
  cursor3 = g.conn.execute(
    "SELECT a.name FROM exhibitions_exhibited e, directed d, curators_lived c, featured_in f, artists_lived a WHERE e.title=%s AND e.e_num=d.e_num AND d.c_id=c.c_id AND e.e_num = f.e_num AND f.a_id=a.a_id", 
    name)
  artistFeatured = []
  artistFeatured = cursor3.fetchall()
  cursor3.close()

  #artists
  cursor4 = g.conn.execute(
    "SELECT a.name, a.a_id  FROM artists_lived a")
  artists = []
  artists = cursor4.fetchall()
  cursor4.close()

  #curators
  cursor5 = g.conn.execute(
    "SELECT c.name, c.c_id  FROM curators_lived c")
  curators = []
  curators = cursor5.fetchall()
  cursor5.close()

  context = dict(data = exhibitionsInfo, dataCurators = curatorsFeatured, dataArtists = artistFeatured, artistsList = artists, curatorsList = curators)
  return render_template("getExhibitionsInfo.html", **context)

# update exhibition title
@app.route('/updateExhibitionsTitle', methods=['POST'])
def updateExhibitionsTitle():
  e_num = request.form['e_num']
  title = request.form['title']
  # startDate = request.form['startDate']
  # endDate = request.form['endDate']
  # url = request.form['url']
  try:
    intEnum = int(e_num)
  except ValueError:
    return render_template("invalidId.html")

  #check for existing
  queryResult = g.conn.execute("SELECT e.e_num FROM exhibitions_exhibited e WHERE e.e_num=%s", e_num)
  existing = queryResult.fetchall()
  if existing:
    return render_template("doesnotExist.html")
  queryResult.close()

  if e_num=="" or title=="":
    return render_template("dont.html")
  else:
    g.conn.execute('UPDATE exhibitions_exhibited SET title=%s WHERE e_num = %s', title, e_num)
  return render_template("updateExhibitionDone.html")

# update exhibition start date
@app.route('/updateExhibitionsFrom', methods=['POST'])
def updateExhibitionsFrom():
  e_num = request.form['e_num']
  userStartDate = request.form['startDate']
  try:
    intEnum = int(e_num)
  except ValueError:
    return render_template("invalidId.html")

  queryResult = g.conn.execute('SELECT to_ FROM exhibitions_exhibited e WHERE e.e_num=%s', e_num)

  try:
    startDate = datetime.strptime(userStartDate, "%Y-%m-%d").date()
  except ValueError:
    return render_template("dateError.html")

  rows = queryResult.fetchall()
  
  try:
    endDate = rows[0][0]
  except IndexError:
    return render_template("invalidId.html")

  #check for existing
  queryResult = g.conn.execute("SELECT e.e_num FROM exhibitions_exhibited e WHERE e.e_num=%s", e_num)
  existing = queryResult.fetchall()
  if existing:
    return render_template("doesnotExist.html")
  queryResult.close()

  if e_num=="" or userStartDate=="":
    return render_template("dont.html")
  elif not_date(userStartDate):
    return render_template("dateError.html")
  elif startDate >= endDate:
    return render_template("dateError.html")
  else:
    g.conn.execute('INSERT INTO durations (from_, to_) SELECT %s, (SELECT to_ FROM exhibitions_exhibited e WHERE e.e_num=%s) WHERE NOT EXISTS (SELECT from_, to_ FROM durations WHERE from_=%s AND to_=(SELECT to_ FROM exhibitions_exhibited e WHERE e.e_num=%s))', userStartDate, e_num, userStartDate, e_num)
    g.conn.execute('UPDATE exhibitions_exhibited SET from_=%s WHERE e_num = %s', userStartDate, e_num)
  return render_template("updateExhibitionDone.html")

# update exhibition end date
@app.route('/updateExhibitionsTo', methods=['POST'])
def updateExhibitionsTo():
  e_num = request.form['e_num']
  userEndDate = request.form['endDate']

  try:
    intEnum = int(e_num)
  except ValueError:
    return render_template("invalidId.html")

  queryResult = g.conn.execute('SELECT from_ FROM exhibitions_exhibited e WHERE e.e_num=%s', e_num) 
  
  try:
    endDate = datetime.strptime(userEndDate, "%Y-%m-%d").date()
  except ValueError:
    return render_template("dateError.html")

  rows = queryResult.fetchall()

  try:
    startDate = rows[0][0]
  except IndexError:
    return render_template("invalidId.html")

  #check for existing
  queryResult = g.conn.execute("SELECT e.e_num FROM exhibitions_exhibited e WHERE e.e_num=%s", e_num)
  existing = queryResult.fetchall()
  if existing:
    return render_template("doesnotExist.html")
  queryResult.close()

  if e_num=="" or userEndDate=="":
    return render_template("dont.html")
  elif not_date(userEndDate):
    return render_template("dateError.html")
  elif startDate >= endDate:
    return render_template("dateError.html")
  else:
    g.conn.execute('INSERT INTO durations (from_, to_) SELECT (SELECT from_ FROM exhibitions_exhibited e WHERE e.e_num=%s), %s WHERE NOT EXISTS (SELECT from_, to_ FROM durations WHERE from_=(SELECT from_ FROM exhibitions_exhibited e WHERE e.e_num=%s) AND to_=%s)', e_num, userEndDate, e_num, userEndDate)
    g.conn.execute('UPDATE exhibitions_exhibited SET to_=%s WHERE e_num = %s', userEndDate, e_num)
    # g.conn.execute('UPDATE exhibitions_exhibited SET to_=%s WHERE title = %s AND EXISTS (SELECT from_, to_ FROM durations WHERE from_=%s AND to_=%s)', endDate, title, startDate, endDate)
    # g.conn.execute('UPDATE exhibitions_exhibited SET url=%s WHERE title = %s AND EXISTS (SELECT from_, to_ FROM durations WHERE from_=%s AND to_=%s)', url, title, startDate, endDate)
  return render_template("updateExhibitionDone.html")

# update exhibition url
@app.route('/updateExhibitionsUrl', methods=['POST'])
def updateExhibitionsUrl():
  e_num = request.form['e_num']
  url = request.form['url']

  #check for valid input
  try:
    intEnum = int(e_num)
  except ValueError:
    return render_template("invalidId.html")

  #check for existing
  queryResult = g.conn.execute("SELECT e.e_num FROM exhibitions_exhibited e WHERE e.e_num=%s", e_num)
  existing = queryResult.fetchall()
  if existing:
    return render_template("doesnotExist.html")
  queryResult.close()

  #check if empty
  if e_num=="" or url=="":
    return render_template("dont.html")
  else:
    # g.conn.execute('INSERT INTO durations (from_, to_) SELECT %s, %s WHERE NOT EXISTS (SELECT from_, to_ FROM durations WHERE from_=%s AND to_=%s)', startDate, endDate, startDate, endDate)
    g.conn.execute('UPDATE exhibitions_exhibited SET url=%s WHERE e_num = %s', url, e_num)
    # g.conn.execute('UPDATE exhibitions_exhibited SET to_=%s WHERE title = %s AND EXISTS (SELECT from_, to_ FROM durations WHERE from_=%s AND to_=%s)', endDate, title, startDate, endDate)
    # g.conn.execute('UPDATE exhibitions_exhibited SET url=%s WHERE title = %s AND EXISTS (SELECT from_, to_ FROM durations WHERE from_=%s AND to_=%s)', url, title, startDate, endDate)
  return render_template("updateExhibitionDone.html")

# delete exhibitions
@app.route('/deleteExhibitionsInfo', methods=['POST'])
def deleteExhibitionsInfo():
  e_num = request.form['e_num']

  #check for existing
  queryResult = g.conn.execute("SELECT e.e_num FROM exhibitions_exhibited e WHERE e.e_num=%s", e_num)
  existing = queryResult.fetchall()
  if existing:
    return render_template("doesnotExist.html")
  queryResult.close()


  queryResult = g.conn.execute("SELECT from_, to_ FROM exhibitions_exhibited e WHERE e.e_num=%s", e_num)
  eDates = queryResult.fetchall()
  startdateObject = eDates[0][0]
  enddateObject = eDates[0][1]
  startDate = startdateObject.strftime("%Y-%m-%d")
  endDate = enddateObject.strftime("%Y-%m-%d")
  queryResult.close()

  try:
    intEnum = int(e_num)
  except ValueError:
    return render_template("invalidId.html")

  if e_num=="":
    return render_template("dont.html")
  else:
   g.conn.execute('DELETE FROM featured_in WHERE e_num=%s', e_num)
   g.conn.execute('DELETE FROM directed WHERE e_num=%s', e_num)
   g.conn.execute('DELETE FROM exhibitions_exhibited WHERE e_num=%s', e_num)
   g.conn.execute('DELETE FROM durations WHERE from_=%s AND to_=%s', startDate, endDate)
   return render_template("deleteExhibitionDone.html")


# create exhibitions
@app.route('/createExhibition', methods=['POST'])
def createExhibition():
  e_num = request.form['e_num']
  title = request.form['title']
  userStartDate = request.form['startDate']
  url = request.form['url']
  curator = request.form['curator']
  artist1 = request.form['artist1']
  artist2 = request.form['artist2']
  artist3 = request.form['artist3']
  userEndDate = request.form['endDate']

  try:
    intEnum = int(e_num)
  except ValueError:
    return render_template("invalidId.html")
  try:
    intEnum = int(curator)
  except ValueError:
    return render_template("invalidId.html")

  try:
    endDate = datetime.strptime(userEndDate, "%Y-%m-%d").date()
  except ValueError:
    return render_template("dateError.html")
  try:
    startDate = datetime.strptime(userStartDate, "%Y-%m-%d").date()
  except ValueError:
    return render_template("dateError.html")

  #check for existing
  queryResult = g.conn.execute("SELECT e.e_num FROM exhibitions_exhibited e WHERE e.e_num=%s", e_num)
  existing = queryResult.fetchall()
  if existing:
    return render_template("alreadyExists.html")
  queryResult.close()

  if e_num=="" or title=="" or startDate=="" or endDate=="" or url=="" or curator=="" or artist1=="":
    return render_template("dont.html")
  elif not_date(userStartDate) or not_date(userEndDate):
    return render_template("dateError.html")
  elif startDate >= endDate:
    return render_template("dateError.html")
  elif (artist2 != "" and artist1==artist2) or (artist3 != "" and artist1==artist3) or (artist2 !="" and artist3 != "" and (artist1==artist3 or artist1==artist2 or artist3==artist2)):
    return render_template("beGentle.html")
  else:
    try:
      intEnum = int(artist1)
    except ValueError:
      return render_template("invalidId.html")
    if artist2 != "":
      try:
        intEnum = int(artist2)
      except ValueError:
        return render_template("invalidId.html")
    if artist3 != "":
      try:
        intEnum = int(artist3)
      except ValueError:
        return render_template("invalidId.html")

    g.conn.execute('INSERT INTO durations (from_, to_) SELECT %s, %s WHERE NOT EXISTS (SELECT from_, to_ FROM durations WHERE from_=%s AND to_=%s)', userStartDate, userEndDate, userStartDate, userEndDate)
    g.conn.execute('INSERT INTO exhibitions_exhibited (e_num, title, url, from_, to_) SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT e_num FROM exhibitions_exhibited WHERE e_num=%s)', e_num, title, url, userStartDate, userEndDate, e_num)
    g.conn.execute('INSERT INTO directed (c_id, e_num) SELECT %s, %s WHERE EXISTS (SELECT c_id FROM curators_lived WHERE c_id=%s) AND NOT EXISTS (SELECT c_id, e_num FROM directed d WHERE d.c_id=%s AND d.e_num=%s)', curator, e_num, curator, curator, e_num)
    g.conn.execute('INSERT INTO featured_in (a_id, e_num) SELECT %s, %s WHERE EXISTS (SELECT a_id FROM artists_lived WHERE a_id=%s) AND NOT EXISTS (SELECT a_id, e_num FROM featured_in f WHERE f.a_id=%s AND f.e_num=%s)', artist1, e_num, artist1, artist1, e_num)
    if artist2 != "":
     g.conn.execute('INSERT INTO featured_in (a_id, e_num) SELECT %s, %s WHERE EXISTS (SELECT a_id FROM artists_lived WHERE a_id=%s) AND NOT EXISTS (SELECT a_id, e_num FROM featured_in f WHERE f.a_id=%s AND f.e_num=%s)', artist2, e_num, artist1, artist2, e_num)
    if artist3 != "":
     g.conn.execute('INSERT INTO featured_in (a_id, e_num) SELECT %s, %s WHERE EXISTS (SELECT a_id FROM artists_lived WHERE a_id=%s) AND NOT EXISTS (SELECT a_id, e_num FROM featured_in f WHERE f.a_id=%s AND f.e_num=%s)', artist3, e_num, artist3, artist1, e_num)

  return render_template("createExhibitionDone.html")


@app.route('/addArtist', methods=['POST'])
def addArtist():  
  a_id = request.form['a_id']
  name = request.form['name']
  birth = request.form['birth']
  death = request.form['death']
  gender = request.form['gender']
  nationality = request.form['nationality']
  try:
<<<<<<< HEAD
      intEnum = int(a_id)
  except ValueError:
      return render_template("invalidId.html")
=======
    intEnum = int(a_id)
  except ValueError:
    return render_template("invalidId.html")
  
>>>>>>> 709535df39a9d12e8af9cc5539bc6428491868cb
  try:
    endDate = datetime.strptime(death, "%Y-%m-%d").date()
  except ValueError:
    return render_template("dateError.html")
  try:
    startDate = datetime.strptime(birth, "%Y-%m-%d").date()
  except ValueError:
    return render_template("dateError.html")
  momaurl = request.form['momaurl']
  ulanid = request.form['ulanid']
  wikidataid = request.form['wikidataid']
  viafid = request.form['viafid']
  
  try: 
    intEnum = int(ulanid)
  except ValueError:
    return render_template("invalidulanid.html")
  try:
    intEnum = int(viafid)
  except ValueError:
    return render_template("invalidviafid.html")

  #check for existing
  queryResult = g.conn.execute("SELECT a.a_id FROM artists_lived a WHERE a.a_id=%s", a_id)
  existing = queryResult.fetchall()
  if existing:
    return render_template("alreadyExists.html")
  queryResult.close()

  if a_id=="" or name=="" or birth=="" or death=="" or momaurl=="" or ulanid=="" or wikidataid=="" or viafid=="":
    return render_template("dont.html")
  elif not_date(birth) or not_date(death):
    return render_template("dont.html")
  elif startDate >= endDate:
    return render_template("dont.html")
  elif gender!="male" and gender!="female":
    return render_template("genderError.html")
  else:
    g.conn.execute('INSERT INTO durations (from_, to_) SELECT %s, %s WHERE NOT EXISTS (SELECT from_, to_ FROM durations d WHERE d.from_=%s AND d.to_=%s)', birth, death, birth, death)
    g.conn.execute('INSERT INTO artists_lived (a_id, name, gender, nationality, from_, to_) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT a_id FROM artists_lived a WHERE a.a_id=%s)', a_id, name, gender, nationality, birth, death, a_id)
    g.conn.execute('INSERT INTO artistprofiles_isrec (momaurl, ulanid, wikidataid, viafid, a_id) SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT a_id FROM artistprofiles_isrec WHERE a_id=%s)', momaurl, ulanid, wikidataid, viafid, a_id, a_id)
  return render_template("addArtistDone.html")

# delete artist
@app.route('/deleteArtist', methods=['POST'])
def deleteArtist():
  a_id = request.form['a_id']

  #check for existing
 # pdb.set_trace()
  queryResult = g.conn.execute("SELECT a.a_id FROM artists_lived a WHERE a.a_id=%s", a_id)
  existing = queryResult.fetchall()
  if not existing:
    return render_template("doesnotExist.html")
  queryResult.close()

  queryResult = g.conn.execute("SELECT from_, to_ FROM artists_lived a WHERE a.a_id=%s", a_id)
  artistDates = queryResult.fetchall()
  birthdateObject = artistDates[0][0]
  deathdateObject = artistDates[0][1]
  birthdate = birthdateObject.strftime("%Y-%m-%d")
  deathdate = deathdateObject.strftime("%Y-%m-%d")
  queryResult.close()

  try:
    intAid = int(a_id)
  except ValueError:
    return render_template("invalidId.html")

  #if a_id=="" or birthdate=="" or deathdate=="":
  if a_id=="":
    return render_template("dont.html")
  #elif not_date(birthdate) or not_date(deathdate):
  #   return render_template("dateError.html")
  else:
   g.conn.execute('DELETE FROM featured_in WHERE EXISTS (SELECT a_id FROM featured_in f WHERE f.a_id=%s) AND a_id=%s', a_id, a_id)
   g.conn.execute('DELETE FROM artistprofiles_isrec WHERE a_id=%s AND EXISTS (SELECT a_id FROM artistprofiles_isrec a WHERE a.a_id=%s)', a_id, a_id)
   g.conn.execute('DELETE FROM artists_lived WHERE a_id=%s AND EXISTS (SELECT a_id FROM artists_lived a WHERE a.a_id=%s)', a_id, a_id)
   g.conn.execute('DELETE FROM durations WHERE from_=%s AND to_=%s AND EXISTS (SELECT from_, to_ FROM artists_lived a WHERE a.from_=%s AND a.to_=%s)', birthdate, deathdate, birthdate, deathdate)
   return render_template("deleteArtistDone.html")

# add curator
@app.route('/addCurator', methods=['POST'])
def addCurator():  
  c_id = request.form['c_id']
  name = request.form['name']
  birth = request.form['birth']
  death = request.form['death']
  gender = request.form['gender']
  nationality = request.form['nationality']

  try:
<<<<<<< HEAD
      intEnum = int(c_id)
  except ValueError:
      return render_template("invalidId.html")
=======
    intEnum = int(c_id)
  except ValueError:
    return render_template("invalidId.html")

>>>>>>> 709535df39a9d12e8af9cc5539bc6428491868cb
  try:
    endDate = datetime.strptime(death, "%Y-%m-%d").date()
  except ValueError:
    return render_template("dateError.html")
  try:
    startDate = datetime.strptime(birth, "%Y-%m-%d").date()
  except ValueError:
    return render_template("dateError.html")

  #check for existing
  queryResult = g.conn.execute("SELECT c.c_id FROM curators_lived c WHERE c.c_id=%s", c_id)
  existing = queryResult.fetchall()
  if existing:
    return render_template("alreadyExists.html")
  queryResult.close()

  if c_id=="" or name=="" or birth=="" or death=="":
    return render_template("dont.html")
  elif not_date(birth) or not_date(death):
    return render_template("dont.html")
  elif startDate >= endDate:
    return render_template("dont.html")
  elif gender!="male" and gender!="female":
    return render_template("genderError.html")
  else:
    g.conn.execute('INSERT INTO durations (from_, to_) SELECT %s, %s WHERE NOT EXISTS (SELECT from_, to_ FROM durations d WHERE d.from_=%s AND d.to_=%s)', birth, death, birth, death)
    g.conn.execute('INSERT INTO curators_lived (c_id, name, gender, nationality, from_, to_) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT c_id FROM curators_lived c WHERE c.c_id=%s)', c_id, name, gender, nationality, birth, death, c_id)
  return render_template("addCuratorDone.html")

# delete curator
@app.route('/deleteCurator', methods=['POST'])
def deleteCurator():
  c_id = request.form['c_id']

  #check for existing
  queryResult = g.conn.execute("SELECT c.c_id FROM curators_lived c WHERE c.c_id=%s", c_id)
  existing = queryResult.fetchall()
  if not existing:
    return render_template("doesnotExist.html")
  queryResult.close()

  queryResult = g.conn.execute("SELECT from_, to_ FROM curators_lived c WHERE c.c_id=%s", c_id)
  curatorDates = queryResult.fetchall()
  birthdateObject = curatorDates[0][0]
  deathdateObject = curatorDates[0][1]
  birthdate = birthdateObject.strftime("%Y-%m-%d")
  deathdate = deathdateObject.strftime("%Y-%m-%d")
  queryResult.close()

  try:
    intCid = int(c_id)
  except ValueError:
    return render_template("invalidId.html")


  if c_id=="":
    return render_template("dont.html")
  else:
   g.conn.execute('DELETE FROM directed WHERE c_id=%s', c_id)
   g.conn.execute('DELETE FROM curators_lived WHERE c_id=%s', c_id)
   g.conn.execute('DELETE FROM durations WHERE from_=%s AND to_=%s', birthdate, deathdate)
   return render_template("deleteCuratorDone.html")

# @app.route('/addArtistProfile', methods=['POST'])
# def addArtistProfile():
#   a_id = request.form['a_id']
#   momaurl = request.form['momaurl']
#   ulanid = request.form['ulanid']
#   wikidataid = request.form['wikidataid']
#   viafid = request.form['viafid']

#   if momaurl =="" or a_id=="":
#      return render_template("dont.html")
#   else: 
#     cursor = g.conn.execute(
#      "SELECT * FROM artistprofiles_isrec p WHERE p.a_id=%s", 
#      a_id)
#     profilesExist = []
#     profilesExist = cursor.fetchall()
#     if not profilesExist:
#       g.conn.execute('INSERT INTO artistprofiles_isrec (momaurl, ulanid, wikidataid, viafid, a_id) SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT a_id FROM artistprofiles_isrec WHERE a_id=%s)', momaurl, ulanid, wikidataid, viafid, a_id, a_id)
#     cursor.close()
#   return render_template("updateDone.html")

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
