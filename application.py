from flask import Flask

api = Flask(__name__)

from api import controller

if __name__ == "__main__":
    api.run(host='0.0.0.0', port=5000, debug=True)