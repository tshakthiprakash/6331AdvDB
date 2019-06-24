from flask import Flask,render_template
import sqlite3 as sql
import pandas as pd
import numpy as np
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
	result = []
	query = "SELECT * FROM voting where TotalPop between 500 and 1000 "
	con = sql.connect("database.db") 
	cur = con.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	query = "SELECT * FROM voting where TotalPop between 1000 and 5000 "
	con = sql.connect("database.db") 
	cur = con.cursor()
	cur.execute(query)
	result = cur.fetchall()
	return render_template('home.html',rows = rows,data = result)
  
@app.route('/enternew')
def upload_csv():
   return render_template('upload.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
	if request.method == 'POST':
	   con = sql.connect("database.db")
	   csv = request.files['myfile']
	   file = pd.read_csv(csv)
	   file.to_sql('voting', con, schema=None, if_exists='replace', index=True, index_label=None, chunksize=None, dtype=None)
	   con.close()
	   return render_template('home.html')

	


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
	
@app.route('/q3search')
def q3search():
	return render_template('q3search.html')
	
@app.route('/clustering',methods = ['POST', 'GET'])
def clustering():	
	count=[]
	labels_n=[]
	n = 5000
		
	for i in np.arange(1000,30000,n):
		t=[]
		val1=i
		val2=i+n
		query = "select count(*) from voting where  TotalPop BETWEEN ' " + str(val1)+ " 'and ' " + str(val2)+ " ' " 
		con = sql.connect("database.db") 
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchone()
		count.append(rows[0])
		t.append(str(val1)+"-"+str(val2))
		#t.append(str(val2))
		labels_n.append(t)
			
		
		fig=plt.figure()
		y_pos =np.arange(len(labels_n))
		#print(y_pos)
		color=['r','b','g','y','c','b']
		for i  in range(len(count)):
			plt.bar(y_pos[i] , count[i] , color=color[i], align ='center',label="{0}".format(labels_n[i]))
			
		plt.xticks(y_pos,labels_n)
		plt.xlabel('range')
		plt.title(' TotalPop')
		plt.ylabel('count')
		#plt.show()
		for i,v in enumerate(count):
			plt.text(i,v , str(v), color='r', fontweight='bold' , horizontalalignment='center') #vertical
			# plt.text(v,i , str(v), color='r', fontweight='bold') horizontal
			#print(v,i,str(v))
		
		plt.legend(numpoints=1)
		plot=convert_fig_to_html(fig)
	return render_template("clus_o.html",data=plot.decode('utf8'))

@app.route('/q1search')
def q1search():
	return render_template('q1search.html')
	
@app.route('/clustering_pie',methods = ['POST', 'GET'])
def clustering_pie():	
	n = int(request.form["num"])
	main_result = []
	result = []
	for i in range(40,80,n):
		query = "SELECT count(*) FROM voting where (Voted*1.0/TotalPop)*100 between "+str(i)+ " and "+str(i+n)
		con = sql.connect("database.db") 
		cur = con.cursor()
		cur.execute(query)
		rows = cur.fetchone()
		t = str(i)+ " - "+str(i+n)
		result.append(t)
		main_result.append(rows)
	y=pd.DataFrame(main_result)
	X= y.dropna()
	print(X)
	fig=plt.figure()
	plt.pie(X[0],labels = result,autopct='%1.0f%%')
	plt.legend()
	plot = convert_fig_to_html(fig)
	return render_template("clus_o.html",data=plot.decode('utf8'))
	
@app.route('/q2search')
def q2search():
	return render_template('q2search.html')
	
@app.route('/clustering_scatter',methods = ['POST', 'GET'])
def clustering_scatter():
	rows = []
	mainres = []
	n1  = int(request.form["n1"])
	n2  = int(request.form["n2"])
	x=[]
	y=[]
	i=n1
	for i in range (n2):

		t=(i*i)+1
		x.append(t)
		y.append(i)
		
		
	fig = plt.figure()
	plt.plot(y,x ,marker ='o',color='r',markeredgecolor='b')
	plt.title('x=(y*y)+1')
	plt.xlabel('y value')
	plt.ylabel('x value')
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
