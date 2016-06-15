import re
import pandas as pd

from pit_app.models import TGE, Observation
from flask import Blueprint, send_file, request, Response

# app = Flask(__name__, static_folder='data/GFF3')
# app = Flask(__name__, static_url_path='/data')

data = Blueprint('data',  __name__)

@data.route('/data/<filename>')
def download_data(filename):
	df = pd.read_table("/Users/elena/Desktop/aws_pit/eb-pitdb/pit_app/static/data/G10.assemblies.fasta.transdecoder.genome.gff3_identified.gff3", sep="\t", index_col = None) 
	
	subset = df[df['attributes'].str.contains("asmbl_66693\|m.1109188[;.]")]
	#data = subset.to_string(header = False, index = False)
	#subset.to_csv('/Users/elena/Desktop/PITDB/pitProject/pitdb/flaskapp/app/pit_app/static/data/test.gff3', sep='\t', index = False)

	#return data 
	return send_file('static/data/'+'test.gff3') 

@data.route('/download', methods=['POST'])
def download():
	organism = str(request.form['organism'])
	print organism
	selected = request.form.getlist('check')
	print selected
	nested   = request.form.getlist('check_nested')
	print nested

	tges = TGE.query.join(Observation).filter_by(organism=organism).distinct(Observation.tge_id)

	def generate():
		for tge in tges:
			if ('tgeAcc' in selected): 
				yield tge.accession + ',' 
			if ('tgeType' in selected): 
				yield tge.tge_class + ',' 
			if ('protName' in selected): 
				yield tge.uniprot_id + ',' 
			if ('aminoSeq' in selected): 
				yield tge.amino_seq + ','
			yield '\n'

	return Response(generate(), mimetype='text/csv', headers={"Content-disposition":"attachment; filename=output.csv"})
