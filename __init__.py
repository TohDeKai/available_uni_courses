from flask import Flask
from app import app
app = Flask(__name__)

flaskapp = Flask(__name__)
if __name__ == '__main__':
    flaskapp.run(debug=True)