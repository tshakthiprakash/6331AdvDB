from flask import *
import sqlite3 as sql
import pandas as pd
application = app = Flask(__name__)
import os
import time
import redis
import pickle as pickle
import random

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
	start_time = time.time()
	for i in range(100):
		val = str(random.uniform(2,5))
		#print(val)
		query = "select * from Earthquake where mag > "+val
		if rd.get("result"+str(i)):
			#print("cached if")
			t =  "with"
			rows = pickle.loads(rd.get("result"+str(i)))
		else :
			#print("else")
			con = sql.connect("database.db")
			cur = con.cursor()
			cur.execute(query)
			rows = cur.fetchall()
			rd.set("result"+str(i),pickle.dumps(rows))
			t="without"
	end_time = time.time()
	act_time = end_time - start_time
	return render_template("home.html",time = act_time,t = t)



if __name__ == '__main__':
   app.run()
