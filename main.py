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

	query = "SELECT latitude,longitude FROM Earthquake "
	con = sql.connect("database.db") 
	cur = con.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	y=pd.DataFrame(rows)
	X= y.dropna()
	print(X)
	k=KMeans(n_clusters=5,random_state=0).fit(X)
	c=k.cluster_centers_
	l=k.labels_
	fig=plt.figure()
	m=[]
	plt.scatter(X[0],X[1],c=l)
	plt.scatter(c[:,0],c[:,1],c='r',s=100,marker='x')
	for i in  range(len(c)):
		temp=[]
		t = "c"+str(i)
		m.append(t)
		for j in range(0,len(c)):
			if i!=j :
				temp.append(distance.euclidean(c[i],c[j]))
		m.append(temp)
	plot = convert_fig_to_html(fig)
	return render_template("clus_o.html",data=plot.decode('utf8'),distance = m)

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
