from flask import Flask
application = app = Flask(__name__)
import os

@app.route('/')
def home():
   return "Hello Flask"

if __name__ == '__main__':
   app.run()
