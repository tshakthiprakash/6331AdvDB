from flask import Flask, render_template, request
application = app = Flask(__name__)
import os

port = int(os.getenv('PORT', 8000))
@app.route('/')
def home():
   return render_template('home.html')

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=port,debug = False)
