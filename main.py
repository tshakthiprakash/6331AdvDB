from flask import Flask, render_template, request
application = app = Flask(__name__)
import os

@app.route('/')
def home():
   return "Hello World"

@app.route('/first')
def first():
   return "Hello First"

if __name__ == '__main__':
   app.run()
