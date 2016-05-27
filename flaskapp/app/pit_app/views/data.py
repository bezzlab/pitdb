import pandas
import re
from flask import Blueprint, send_file

# app = Flask(__name__, static_folder='data/GFF3')
# app = Flask(__name__, static_url_path='/data')

data = Blueprint('data',  __name__)

@data.route('/data/<filename>')
def download_data(filename):
	df = pandas.read_table("/Users/elena/Desktop/PITDB/pitProject/pitdb/flaskapp/app/pit_app/static/data/G10.assemblies.fasta.transdecoder.genome.gff3_identified.gff3", sep="\t", index_col = None) 
	
	subset = df[df['attributes'].str.contains("asmbl_66693\|m.1109188[;.]")]
	#data = subset.to_string(header = False, index = False)
	#subset.to_csv('/Users/elena/Desktop/PITDB/pitProject/pitdb/flaskapp/app/pit_app/static/data/test.gff3', sep='\t', index = False)

	#return data 
	return send_file('static/data/'+'test.gff3') 

	
