import re
import pandas as pd

from pit_app.models import *
from flask import Blueprint, send_file, request, Response

# app = Flask(__name__, static_folder='data/GFF3')
# app = Flask(__name__, static_url_path='/data')

data = Blueprint('data',  __name__)

@data.route('/data/<uniprot>')
def download_data(uniprot):
	data = pd.DataFrame()
	obj  = Experiment.query.with_entities(Experiment.title, Sample.name, Sample.id).\
					join(Sample).join(Observation).\
					filter_by(uniprot_id=uniprot).group_by(Experiment.title, Sample.name, Sample.id).all()
	
	for sample in obj:
		df = pd.read_table("/Users/elena/Desktop/aws_pit/eb-pitdb/pit_app/static/data/"+sample.title+"/"+sample.name+".assemblies.fasta.transdecoder.genome.gff3_identified.gff3", sep="\t", index_col = None) 
		
		obs  = Observation.query.with_entities(Observation.long_description).\
						filter_by(uniprot_id=uniprot, sample_id=sample.id).all()

		for ob in obs: 
			arr  = ob.long_description.split(" ")
			mRNA = arr[0]
			gene = arr[1]
			subset = df[df['attributes'].str.contains(re.escape("ID="+gene+";")+"|"+re.escape(mRNA)+"[;.]")]
			data = pd.concat([data, subset], axis=0)
			
	data = data.to_csv(None, sep='\t', index = False)

	return data 
	

@data.route('/download', methods=['POST'])
def download():
	organism = str(request.form['organism'])
	selected = request.form.getlist('check')
	nested   = request.form.getlist('check_nested')

	tges = TGE.query.join(Observation).filter_by(organism=organism).distinct(Observation.tge_id).all()

	def generate():
		i = 0
		for tge in tges:
			# Filter rows (based on tge_class)
			if (len(nested) != 0): 
				classes = (tge.tge_class).split(",")

				# For every selected class by the user filter the rows
				for elem in nested:
					if (elem in classes):
						# print accession number
						if ('tgeAcc' in selected):
							yield tge.accession + ','
						# print the tge class 
						yield tge.tge_class + ','
						# print protName
						if ('protName' in selected):
							yield tge.uniprot_id + ',' 
						# print amino acid seq
						if ('aminoSeq' in selected):
							yield tge.amino_seq + ','
						yield '\n'

	return Response(generate(), mimetype='text/csv', headers={"Content-disposition":"attachment; filename=output.csv"})
