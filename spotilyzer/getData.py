import requests
import base64
import pdb
import psycopg2
from psycopg2 import connect
import sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DBUSER = "spotilyzer"
DBPASS = "spotipass"
DBNAME = "spotilyzerdb"

def getSongs(songList, **kwargs):
	#INPUT: takes a list of song id's, kwargs: accessToken, userID
	#OUTPUT: returns a list
	con = None
	try:
		con = connect(dbname=DBNAME, user=DBUSER, host='localhost', password=DBPASS)
	except:
		createDB()
		createSongsTable()
		createArtistsTable()
		createAlbumsTable()
	
	access_header = getAccessHeader()
	if con:
		featureData = []
		for songID in songList:
			if dbHasSong(con, songID):
				 featureData.append({}) #append the feature dctionary for the song
			else:
				songFeatures = getSongFeatures(songID, access_header)
				featureData.append({})
				#insert data into db
	else:
		print("No connection to database")

	return featureData

def getAccessHeader():
	TOKEN_URL = "https://accounts.spotify.com/api/token"
	CLIENT_ID = "fa7e7c8d114a487c81a31a32dd0c0ef5"
	CLIENT_SECRET = "7df74727c0a846b1ba7bf042f9421f6c"
	DATA = {"grant_type":"client_credentials"}
	temp1 = CLIENT_ID+":"+CLIENT_SECRET
	temp2 = temp1.encode('utf-8','strict')
	HEADER_64_STRING = base64.b64encode(temp2)
	HEADERS = {"Authorization":b"Basic "+HEADER_64_STRING}
	response = requests.post(TOKEN_URL, data=DATA, headers=HEADERS)
	response.content
	access_token = response.json()['access_token']
	access_header = {"Authorization":"Bearer "+access_token}
	return access_header

def getSongFeatures(sid, access_header):
	url = "https://api.spotify.com/v1/audio-features/"
	resp = requests.get(url+sid, headers=access_header)
	return resp.json()
	
def dbHasSong(con, sid):
	cur = con.cursor()
	con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur.execute("SELECT * FROM songs WHERE songid='" + sid + "';")
	row = cur.fetchone()
	return row is not None

def createDB():
	con = connect(dbname='postgres', user=DBUSER, host='localhost', password=DBPASS)
	con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur = con.cursor()
	cur.execute('CREATE DATABASE ' + DBNAME)
	cur.close()
	con.close()

def createSongsTable():
	con = connect(dbname=DBNAME, user=DBUSER, host='localhost', password=DBPASS)
	con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur = con.cursor()
	query = """CREATE TABLE songs(songID char(22) PRIMARY KEY NOT NULL,
			artistIDs char(22) NOT NULL,
			albumID char(22) NOT NULL,
			song_title text NOT NULL,
			available_markets char(2)[],
			duration int,
			popularity int,
			danceability double precision,
			energy double precision,
			key int,
			loudness double precision,
			mode int,
			speechiness double precision,
			acousticness double precision,
			instrumentalness double precision,
			liveness double precision,
			valence double precision,
			tempo double precision,time_signature int)"""
	cur.execute(query)
	cur.close()
	con.close()

def createArtistsTable():
	con = connect(dbname=DBNAME, user=DBUSER, host='localhost', password=DBPASS)
	con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur = con.cursor()
	query = """CREATE TABLE artists(
    	ArtistID char[22] NOT NULL PRIMARY KEY,
    	followers int,
    	genres text[],
    	name text,
    	popularity int)"""
	cur.execute(query)
	cur.close()
	con.close()
	return

def createAlbumsTable():
	con = connect(dbname=DBNAME, user=DBUSER, host='localhost', password=DBPASS)
	con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur = con.cursor()
	query = """CREATE TABLE albums(
  		albumID char(22) PRIMARY KEY NOT NULL,
  		artistIDs char(22)[] NOT NULL,
  		songIDs char(22)[] NOT NULL,
   		album_title text NOT NULL,
  		available_markets char(2)[],
   		popularity int,
  		genres text[],
  		release_date text,
  	 	release_date_precision text,
   		label text);"""
	cur.execute(query)
	cur.close()
	con.close()
	return
