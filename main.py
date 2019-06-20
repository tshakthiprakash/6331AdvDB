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
	lat1 = float(request.form['lat1'])
	lat2 = float(request.form['lat2'])
	num = int(request.form['num'])
	result = []
	for i in range(num):
		start_t = time.time()
		lat1_random = round(random.uniform(lat1,lat2),2)
		lat2_random = round(random.uniform(lat1,lat2),2)
		query = "select count(*) from Earthquake where latitude between '"+str(lat1_random)+"' and '"+str(lat2_random)+"'"
		if rd.get(query):
			start_t = time.time()
			rowsx = rd.get(query)
			end_time = time.time()-start_t
			result.append(rowsx)
			result.append(lat1_random)
			result.append(lat2_random)
			result.append(end_time)
			t = "with cache"
			result.append(t)
		else:
			start_t = time.time()
			con = sql.connect("database.db")
			cur = con.cursor()
			cur.execute(query)
			rows = cur.fetchone()
			rd.set(query,float(rows[0]))
			end_time = time.time()-start_t
			result.append(rows)
			result.append(lat1_random)
			result.append(lat2_random)
			result.append(end_time)
			t = "without cache"
			result.append(t)
	return render_template("q1result.html",row = result)
	
@app.route('/analyse',methods = ['POST', 'GET'])
def analyse():
	countcache = 0 
	countwithoutcache = 0
	time_with = 0
	time_without = 0
	lat1 = float(request.form['lat1'])
	lat2 = float(request.form['lat2'])
	num = int(request.form['num'])
	for i in range(num):
		lat1_random = round(random.uniform(lat1,lat2),2)
		lat2_random = round(random.uniform(lat1,lat2),2)
		query = "select count(*) from Earthquake where latitude between '"+str(lat1_random)+"' and '"+str(lat2_random)+"'"
		if rd.get(str(i)):
			start_t = time.time()
			#print("cached")
			countcache  = countcache + 1
			r = rd.get(str(i))
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
			rd.set(str(i),1)
			end_t = time.time() - start_t
			time_without = time_without + end_t
			countwithoutcache = countwithoutcache + 1
	return render_template("q8results.html",timewith = time_with,timewithout = time_without,countwithoutcache = countwithoutcache,countcache = countcache,total_time = time_with+time_without )

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

def convert_fig_to_html(fig):
	from io import BytesIO
	figfile = BytesIO()
	plt.savefig(figfile, format='png')
	figfile.seek(0)  # rewind to beginning of file
	import base64
	#figdata_png = base64.b64encode(figfile.read())
	figdata_png = base64.b64encode(figfile.getvalue())
	return figdata_png
	
	
@app.route('/clustering')
def clustering():	
	main_result = []
	for i in range(0,10,2):
		result = []
		query = "SELECT count(*) FROM Earthquake where mag between "+str(i)+" and "+str(i+2)
		con = sql.connect("database.db") 
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchone()
		t = str(i)+ "-" + str(i+2)
		result.append(t)
		result.append(rows[0])
		main_result.append(result)
		print(main_result)
	y=pd.DataFrame(main_result)
	X= y.dropna()
	fig=plt.figure()
	for i in range(len(X[0])):
		plt.bar(X[0][i],X[1][i],label=X[0][i])
	#plt.bar(X[0],X[1],color=['r','y','b','g'],align='center')
	for i,v in enumerate(X[1]):
		plt.text(i, v, str(v), fontweight='bold',horizontalalignment='center')
	plt.legend()
	plt.xlabel('Range', fontsize=15)
	plt.ylabel('No of Eq', fontsize=15)
	plot = convert_fig_to_html(fig)
	return render_template("clus_o.html",data=plot.decode('utf8'))
	
@app.route('/clustering_pie')
def clustering_pie():	
	main_result = []
	for i in range(0,10,2):
		result = []
		query = "SELECT count(*) FROM Earthquake where mag between "+str(i)+" and "+str(i+2)
		con = sql.connect("database.db") 
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchone()
		t = str(i)+ "-" + str(i+2)
		result.append(t)
		result.append(rows[0])
		main_result.append(result)
		#print(main_result)
	y=pd.DataFrame(main_result)
	X= y.dropna()
	fig=plt.figure()
	plt.pie(X[1],labels = X[0],autopct='%1.0f%%')
	plt.legend()
	plot = convert_fig_to_html(fig)
	return render_template("clus_o.html",data=plot.decode('utf8'))
	
@app.route('/clustering_scatter')
def clustering_scatter():

	query = "SELECT survived,fare FROM Titanic "
	con = sql.connect("database.db") 
	cur = con.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	y=pd.DataFrame(rows)
	X= y.dropna()
	print(X)
	k=KMeans(n_clusters=20,random_state=0).fit(X)
	c=k.cluster_centers_
	l=k.labels_
	fig=plt.figure()
	plt.scatter(X[0],X[1],c=l)
	plt.scatter(c[:,0],c[:,1],c='r',s=100,marker='x')
	plot = convert_fig_to_html(fig)
	return render_template("clus_o.html",data=plot.decode('utf8'))

@app.route('/plot_line',methods=['GET','POST'])
def plot_line():
    l=[]
    l1=[]
    mlist=[]
    query='SELECT latitude,longitude FROM Earthquake'
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    df=pd.DataFrame(rows)
    fig=plt.figure()
    plt.plot(df[0],df[1],marker='o',markerfacecolor='red',markersize=6,color='blue',linewidth=1,linestyle='dashed')
    plot=convert_fig_to_html(fig)
    return render_template("clus_o.html", data=plot.decode('utf8'))



if __name__ == '__main__':
   app.run()
