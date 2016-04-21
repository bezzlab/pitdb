from flask import Blueprint, send_file

# app = Flask(__name__, static_folder='data/GFF3')
# app = Flask(__name__, static_url_path='/data')

data = Blueprint('data',  __name__)

@data.route('/data/<filename>')
def download_data(filename):
  return send_file('static/data/'+filename)
