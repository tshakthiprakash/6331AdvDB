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
from sklearn.cluster import KMeans
from scipy.spatial import distance

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

@app.route('/list')
def list():
	start_time = time.time()
	query = "select * from Earthquake"
	if rd.get("result"):
		print("cached if")
		t =  "with"
		rows = pickle.loads(rd.get("result"))
	else :
		print("else")
		con = sql.connect("database.db")
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		rd.set("result",pickle.dumps(rows))
		t="without"
	end_time = time.time()
	act_time = end_time - start_time
	print(act_time)
	return render_template("results.html",row = rows,act_time=act_time,t=t)

analyseglobe = 0
	
@app.route('/analyse')
def analyse():
	countcache = 0 
	countwithoutcache = 0
	start_time = time.time()
	for i in range(100):
		val = str(round(random.uniform(2,5),2))
		print(val)
		query = "select * from Earthquake where mag > "+val
		if rd.get("result"+val):
			print("cached")
			countcache  = countcache + 1
			rows = pickle.loads(rd.get("result"+val))
		else :
			#print("else")
			con = sql.connect("database.db")
			print("without cached")
			cur = con.cursor()
			cur.execute(query)
			rows = cur.fetchall()
			rd.set("result"+val,pickle.dumps(rows))
			countwithoutcache = countwithoutcache + 1
	end_time = time.time()
	act_time = end_time - start_time
	return render_template("home.html",time = act_time,countwithoutcache = countwithoutcache,countcache = countcache)

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
	
@app.route('/clustering')
def clustering():	

	query = "SELECT latitude,longitude FROM Earthquake "
	con = sql.connect("database.db") 
	cur = con.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	y=pd.DataFrame(rows)
	k=KMeans(n_clusters=5,random_state=0).fit(y)
	X= y.dropna()
	print(X[0])
	fig=plt.figure()
	
	plt.scatter(X[0],X[1])
	#print(X[:,0])
	plt.show()
	#fig.savefig('static/img.png')
	#print(k.cluster_centers_)
	return render_template("clus_o.html",data=rows)


if __name__ == '__main__':
   app.run()
