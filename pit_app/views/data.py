import re
import os
import pandas as pd

from pit_app.models import *
from flask import Blueprint, send_file, request, Response, url_for

data = Blueprint('data',  __name__)

@data.route('/genoverse/<uniprot>')
def download_data(uniprot):
	result = pd.DataFrame()
	obj    = Experiment.query.with_entities(Experiment.title, Sample.name, Sample.id).\
						join(Sample).join(Observation).filter_by(uniprot_id=uniprot).\
						group_by(Experiment.title, Sample.name, Sample.id).all()
	
	for sample in obj:
		file = os.path.dirname(__file__)+"/../static/data/"+sample.title+"/"+sample.name+".assemblies.fasta.transdecoder.genome.gff3_identified.gff3"
		df   = pd.read_table(file, sep="\t", index_col = None) 
		obs  = Observation.query.with_entities(Observation.long_description).\
									filter_by(uniprot_id=uniprot, sample_id=sample.id).all()

		for ob in obs: 
			arr  = ob.long_description.split(" ")
			mRNA = arr[0]
			gene = arr[1]
			subset = df[df['attributes'].str.contains(re.escape("ID="+gene+";")+"|"+re.escape(mRNA)+"[;.]")]
			
			# if (len(subset['seqid'].iloc[0]) <= 5):
			result = pd.concat([result, subset], axis=0)
	
	result = result.to_csv(None, sep='\t', index = False)

	return result


@data.route('/genoverse/pep/<uniprot>')
def peptides(uniprot):
	result = pd.DataFrame()
	obj    = Experiment.query.with_entities(Experiment.title, Sample.name, Sample.id).\
						join(Sample).join(Observation).\
						filter_by(uniprot_id=uniprot).group_by(Experiment.title, Sample.name, Sample.id).all()
	
	for sample in obj:
		# result = pd.concat([result, "##"+sample.name], axis=0)
		# file = url_for('static', filename="data/"+sample.title+"/"+sample.name+".assemblies.fasta.transdecoder.genome.gff3_identified.gff3")
	
		# df = pd.read_table(file, sep="\t", index_col = None) 
		file = os.path.dirname(__file__)+"/../static/data/"+sample.title+"/"+sample.name+".assemblies.fasta.transdecoder.genome.gff3_identified_peptide.gff3"
		
		df = pd.read_table(file, sep="\t", index_col = None) 
		
		obs  = Observation.query.with_entities(Observation.long_description).\
						filter_by(uniprot_id=uniprot, sample_id=sample.id).all()

		for ob in obs: 
			arr  = ob.long_description.split(" ")
			mRNA = arr[0]

			subset = df[df['attributes'].str.contains(re.escape(mRNA)+"[;.]")]
			
			result = pd.concat([result, subset], axis=0)
			
	result = result.to_csv(None, sep='\t', index = False)

	return result


# @data.route('/chromosome/<uniprot>')
# def chrom(uniprot):
# 	obj    = Experiment.query.with_entities(Experiment.title, Sample.name, Sample.id).\
# 						join(Sample).join(Observation).\
# 						filter_by(uniprot_id=uniprot).group_by(Experiment.title, Sample.name, Sample.id).first()
	
# 	file = os.path.dirname(__file__)+"/../static/data/"+obj.title+"/"+obj.name+".assemblies.fasta.transdecoder.genome.gff3_identified.gff3"
# 	df   = pd.read_table(file, sep="\t", index_col = None) 
		
# 	obs  = Observation.query.with_entities(Observation.long_description).\
# 						filter_by(uniprot_id=uniprot, sample_id=obj.id).first()

# 	arr  = obs.long_description.split(" ")
# 	mRNA = arr[0]
# 	gene = arr[1]
	
# 	chromosome = df[df['attributes'].str.contains(re.escape("ID="+gene+";")+"|"+re.escape(mRNA)+"[;.]")].iloc[0,0]
# 	chromosome = re.search(r'\d+', chromosome).group()

# 	return chromosome


@data.route('/download', methods=['POST'])
def download():
	organism = str(request.form['organism'])
	fileType = str(request.form['fileType'])
	selected = request.form.getlist('check')
	nested   = request.form.getlist('check_nested')

	tges = TGE.query.join(Observation).filter_by(organism=organism).distinct(Observation.tge_id).all()

	def generate():
		i = 0

		if (fileType == 'fasta'):
			sep = ' '
		else: 
			sep = ','

		for tge in tges:
			# Filter rows (based on tge_class)
			if (len(nested) != 0): 
				classes  = (tge.tge_class).split(",")
				classStr = ' & '.join(classes)

				# For every selected class by the user filter the rows
				for elem in nested:
					if (elem in classes):
						if ('tgeAcc' in selected):
							if (fileType == 'fasta'):
								yield ">"
							yield tge.accession + sep
						yield classStr + sep
						if ('protName' in selected):
							yield tge.uniprot_id + sep 
						if ('aminoSeq' in selected):
							if (fileType == 'fasta'):
								yield '\n'+tge.amino_seq
							else: 
								yield tge.amino_seq + ','
						yield '\n'

	return Response(generate(), mimetype='text/'+fileType, headers={"Content-disposition":"attachment; filename=tges."+fileType})


@data.route('/downloadTranscript', methods=['POST'])
def downloadTrn():
	asmbl   = str(request.form['asmbl'])
	dna_seq = str(request.form['dna_seq'])

	def generate():
		yield ">"
		yield asmbl + '\n'
		yield dna_seq + '\n' 

	return Response(generate(), mimetype='text/fasta', headers={"Content-disposition":"attachment; filename=transcript.fasta"})
