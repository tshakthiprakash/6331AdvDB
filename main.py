from flask import Flask, render_template, request
application = app = Flask(__name__)
import os

port = int(os.getenv('PORT', 8000))
@app.route('/')
def home():
   return "Hello World"

if __name__ == '__main__':
   app.run()
