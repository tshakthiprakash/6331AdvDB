from flask import *
import sqlite3 as sql
import pandas as pd
import numpy as nd
application = app = Flask(__name__)
import os
import time
import redis
import pickle as pickle
import random
from sklearn.cluster import KMeans
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import pyplot as mpld3
from sklearn.cluster import KMeans
from scipy.spatial import distance
from geopy import distance

con = sql.connect("database.db")
rd = redis.StrictRedis(host='shakthi8112.redis.cache.windows.net', port=6380, db=0,password='ncP8NFImWyXmxKjo1MOVoAmJg7KRFX7511MbiSFHR9k=',ssl=True)
@app.route('/')
def home():
   return render_template('home.html')
  
@app.route('/enternew')
def upload_csv():
   return render_template('upload.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
	if request.method == 'POST':
	   con = sql.connect("database.db")
	   csv = request.files['myfile']
	   file = pd.read_csv(csv)
	   file.to_sql('Earthquake', con, schema=None, if_exists='replace', index=True, index_label=None, chunksize=None, dtype=None)
	   con.close()
	   return render_template('home.html')

@app.route('/list',methods = ['POST', 'GET'])
def list():
	lat1 = request.form['lat1']
	lat2 = request.form['lat2']
	print(lat1)
	print(lat2)
	query = "select * from Earthquake where latitude between '"+lat1+"' and '"+lat2+"'"
	con = sql.connect("database.db")
	cur = con.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	print(rows)
	return render_template("results.html",row = rows)
	
@app.route('/q1search')
def q1search():
	return render_template('q1search.html')

@app.route('/q1',methods = ['POST', 'GET'])
def q1():
	start_time = time.time()
	val=0
	num = int(request.form['num'])
	for i in range(num):
		val = val + 0.01
		query = "select * from Earthquake where mag > "+str(val)
		if rd.get("result"+str(i)):
			t = "with"
			#print("cached")
			rows =rd.get("result"+str(i))
		else:
			t = "without"
			con = sql.connect("database.db")
			#print("without cached")
			cur = con.cursor()
			cur.execute(query)
			#rows = cur.fetchall()
			rd.set("result"+str(i),1)
	end_time = time.time()
	act_time = end_time - start_time
	return render_template("q1result.html",time = act_time,t=t)
	
@app.route('/analyse')
def analyse():
	countcache = 0 
	countwithoutcache = 0
	time_with = 0
	time_without = 0
	for i in range(100):
		val = str(round(random.uniform(1,5),2))
		#print(val)
		query = "select * from Earthquake where mag > "+val
		if rd.get("result"+val):
			start_t = time.time()
			#print("cached")
			countcache  = countcache + 1
			r = rd.get("result"+val)
			end_t = time.time() - start_t
			print(end_t)
			time_with = time_with + end_t
			#print(time_with)
		else :
			#print("else")
			start_t = time.time()
			con = sql.connect("database.db")
			#print("without cached")
			cur = con.cursor()
			cur.execute(query)
			rd.set("result"+val,1)
			end_t = time.time() - start_t
			time_without = time_without + end_t
			countwithoutcache = countwithoutcache + 1
	return render_template("results.html",timewith = time_with/countcache,timewithout = time_without/countwithoutcache,countwithoutcache = countwithoutcache,countcache = countcache)

@app.route('/sample')
def sample():
	countcache = 0 
	countwithoutcache = 0
	query = "select distinct net from Earthquake where net like 'n%'"
	con = sql.connect("database.db")
	cur = con.cursor()
	cur.execute(query)
	resultnet = cur.fetchall()
	print(resultnet)
	start_time = time.time()
	for i in range(100):
		val = random.randint(0,len(resultnet)-1)
		print(val)
		strr = str(resultnet[val])
		query  = "select * from Earthquake where net = '"+strr[2:4]+"'"
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		rd.set(query,pickle.dumps(rows))
	end_time = time.time()
	act_time = end_time - start_time
	return render_template("home.html",time = act_time)

@app.route('/samples')
def samples():
	countcache = 0 
	countwithoutcache = 0
	query = "select net from Earthquake where net like 'n%'"
	con = sql.connect("database.db")
	cur = con.cursor()
	cur.execute(query)
	resultnet = cur.fetchall()
	start_time = time.time()
	for i in range(100):
		val = random.randint(0,len(resultnet))
		strr = str(resultnet[val])
		query  = "select * from Earthquake where net = '"+strr[2:4]+"'"
		if rd.get(query):
			print("cached")
	end_time = time.time()
	act_time = end_time - start_time
	return render_template("home.html",time = act_time)
	
@app.route('/select_lat')
def select_lat():
    #for i in range(100):
		start_t = time.time()
		lat=32
		lon=-117
		dist = 100
		query  = "select * from Earthquake "
		cache_name = 'result'+str(lat)+str(lon)+str(dist)
		if rd.get(cache_name):
			results = pickle.loads(rd.get(cache_name))
		else :
			con = sql.connect("database.db")
			cur = con.cursor()
			cur.execute(query)
			rows = cur.fetchall()
			i=0
			results = []
			while(i< len(rows)):
				dest_lat = rows[i][2]
				dest_lon = rows[i][3]
				distan  = distance.distance((lat,lon), (dest_lat,dest_lon)).km
				if(distan < dist):
					results.append(rows[i])
				i=i+1
			rd.set(cache_name,pickle.dumps(results))
		end_t = time.time() - start_t
		print(end_t)
		return render_template("home.html",time = results,pro_time = end_t )


if __name__ == '__main__':
   app.run()
