import re
import os
import pandas as pd

from pit_app.models import *
from flask import Blueprint, send_file, request, Response, url_for

data = Blueprint('data',  __name__)

@data.route('/genoverse/<uniprot>')
def download_data(uniprot):
	result = pd.DataFrame()
	obj    = Experiment.query.with_entities(Experiment.title, Experiment.accession, Sample.name, Sample.id).\
						join(Sample).join(Observation).filter_by(uniprot_id=uniprot).\
						group_by(Experiment.title, Experiment.accession, Sample.name, Sample.id).all()
	
	for sample in obj:
		file = os.path.dirname(__file__)+"/../static/data/"+sample.accession+"/"+sample.name+".assemblies.fasta.transdecoder.genome.gff3_identified.gff3"
		df   = pd.read_table(file, sep="\t", index_col = None) 
		obs  = Observation.query.with_entities(Observation.long_description).\
									filter_by(uniprot_id=uniprot, sample_id=sample.id).all()

		print sample.name 

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
	obj    = Experiment.query.with_entities(Experiment.title, Experiment.accession, Sample.name, Sample.id).\
						join(Sample).join(Observation).\
						filter_by(uniprot_id=uniprot).group_by(Experiment.title, Experiment.accession, Sample.name, Sample.id).all()
	
	for sample in obj:
		# result = pd.concat([result, "##"+sample.name], axis=0)
		# file = url_for('static', filename="data/"+sample.title+"/"+sample.name+".assemblies.fasta.transdecoder.genome.gff3_identified.gff3")
	
		# df = pd.read_table(file, sep="\t", index_col = None) 
		file = os.path.dirname(__file__)+"/../static/data/"+sample.accession+"/"+sample.name+".assemblies.fasta.transdecoder.genome.gff3_identified_peptide.gff3"
		
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
	fileType = str(request.form['fileType'])
	selected = request.form.getlist('check')
	nested   = request.form.getlist('check_nested')
	#print(request.form)
	if 'organism' in request.form:
		organism = str(request.form['organism'])
		print "\n\n\n\nOrganism:"+organism
		# tges = TGE.query.filter(TGE.organisms.like("%"+organism+"%")).distinct(TGE.id).all()
		tges = db.engine.execute("SELECT tge.accession, tge.amino_seq, string_agg(distinct(observation.tge_class), ', ') AS tge_class, string_agg(distinct(observation.uniprot_id), ', ') AS uniprot_id "+ 
                      " FROM tge JOIN observation ON tge.id = observation.tge_id WHERE observation.organism LIKE '%%"+organism+"%%' "+
                      " GROUP BY tge.accession, tge.amino_seq ORDER BY tge.accession").fetchall(); 
	elif 'sample' in request.form:
		sample = str(request.form['sample'])
		print "\n\n\n\nsample:"+sample
		tges = db.engine.execute("SELECT tge.accession, tge.amino_seq, string_agg(distinct(observation.tge_class), ', ') AS tge_class, string_agg(distinct(observation.uniprot_id), ', ') AS uniprot_id "+ 
                      " FROM tge JOIN observation ON tge.id = observation.tge_id WHERE observation.sample_id="+sample+" "+
                      " GROUP BY tge.accession, tge.amino_seq ORDER BY tge.accession").fetchall();
	elif 'experimentTge' in request.form:
		exp = str(request.form['experimentTge'])
		print "\n\n\n\nExperiment:"+exp
		tges = db.engine.execute("SELECT tge.accession, tge.amino_seq, string_agg(distinct(observation.tge_class), ', ') AS tge_class, string_agg(distinct(observation.uniprot_id), ', ') AS uniprot_id "+ 
                      " FROM tge JOIN observation ON tge.id = observation.tge_id JOIN sample ON observation.sample_id = sample.id JOIN experiment ON sample.exp_id = experiment.id WHERE experiment.accession = \'"+exp+
                      "\' GROUP BY tge.accession, tge.amino_seq ORDER BY tge.accession").fetchall();
		print "tge count:"+str(len(tges))
	else:
		print "ERROR"
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
						yield "TGEClass=" + classStr + sep
						if ('protName' in selected):
							yield "Protein=" + tge.uniprot_id + sep 
						if ('aminoSeq' in selected):
							#print(aminoSeq)
							if (fileType == 'fasta'):
								yield '\n'+tge.amino_seq
							else: 
								yield tge.amino_seq + ','
						yield '\n'

	return Response(generate(), mimetype='text/'+fileType, headers={"Content-disposition":"attachment; filename=tges."+fileType})


@data.route('/downloadTranscript', methods=['POST'])
def downloadTrn():
	print "request: downloadTrn"
	if 'asmbl' in request.form:
		asmbl   = str(request.form['asmbl'])
		dna_seq = str(request.form['dna_seq'])

		def generate():
			yield ">"
			yield asmbl + '\n'
			yield dna_seq + '\n' 
		return Response(generate(), mimetype='text/fasta', headers={"Content-disposition":"attachment; filename=transcript.fasta"})
	elif 'sampleT' in request.form:
		sample = str(request.form['sampleT'])
		fileType = str(request.form['fileType'])
		selected = request.form.getlist('check')
		#nested   = request.form.getlist('check_nested')
		print "Sample" + sample 
		print "\n\n\n\nsample:"+sample
		transcripts = db.engine.execute("SELECT transcript.id,transcript.dna_seq, observation.gene_name FROM transcript JOIN transcript_observation ON transcript.id = transcript_observation.transcript_id JOIN observation ON observation.id=transcript_observation.obs_id JOIN sample ON observation.sample_id=sample.id WHERE sample.accession=\'"+sample+"\' GROUP BY transcript.id, transcript.dna_seq, observation.gene_name ORDER BY transcript.id;").fetchall();
	elif 'experimentTrans' in request.form:
		expAcc = str(request.form['experimentTrans'])
		exp= Experiment.query.filter_by(accession=expAcc).first_or_404()
		fileType = str(request.form['fileType'])
		selected = request.form.getlist('check')
		print "Exp" + expAcc
		#print()
		#print "Exp id" +str(exp_id)
		#print "\n\n\n\nsample:"+sample
		transcripts = db.engine.execute("SELECT transcript.id,transcript.dna_seq, observation.gene_name FROM transcript JOIN transcript_observation ON transcript.id = transcript_observation.transcript_id JOIN observation ON observation.id=transcript_observation.obs_id JOIN sample ON observation.sample_id=sample.id WHERE sample.exp_id="+str(exp.id)+" GROUP BY transcript.id, transcript.dna_seq, observation.gene_name ORDER BY transcript.id;").fetchall();
	def generate():
		i = 0
		if (fileType == 'fasta'):
			sep = ' '
		else: 
			sep = ','
		for t in transcripts:
			# For every selected class by the user filter the rows
			if ('transId' in selected):
				if (fileType == 'fasta'):
					yield ">"
				yield "TID=" + str(t.id) + sep
			if ('geneName' in selected):
				yield "gene=" + t.gene_name + sep 
			if ('transSeq' in selected):
				if (fileType == 'fasta'):
					yield '\n'+t.dna_seq
				else: 
					yield t.dna_seq + ','
			yield '\n'
	return Response(generate(), mimetype='text/'+fileType, headers={"Content-disposition":"attachment; filename=transcripts."+fileType})

@data.route('/downloadVariations', methods=['POST'])
def downloadVariations():
	print "request: downloadVariations"
	if 'sampleV' in request.form:
		sample = str(request.form['sampleV'])
		fileType = str(request.form['fileType'])
		selected = request.form.getlist('check')
		#nested   = request.form.getlist('check_nested')
		print "Sample" + sample 
		print "\n\n\n\nsample:"+sample
		variations = db.engine.execute("SELECT variation.id,variation.ref_id, variation.pos, variation.ref_aa, variation.alt_aa, variation.chrom, variation.var_type"+ 
                      " FROM variation JOIN variation_observation ON variation_observation.var_id = variation.id JOIN observation ON observation.id=variation_observation.obs_id WHERE observation.sample_id="+sample+"; ").fetchall();
		print(variations)
		def generate():
			i = 0
			if (fileType == 'provcf'):
				sep = '\t'
			else: 
				sep = ','
			yield "#CHROM"+sep+"POS"+sep+"ID"+sep+"REF"+sep+"ALT"+sep+"Info\n"
			for v in variations:
				yield str(v.ref_id) + sep + str(v.pos) + sep + str(v.id) + sep + v.ref_aa + sep + v.alt_aa + sep
				# For every selected class by the user filter the rows
				
				if ('varType' in selected):
					yield 'Type='+v.var_type+";"
				yield 'chrom='+v.chrom
				yield '\n'
		return Response(generate(), mimetype='text/'+fileType, headers={"Content-disposition":"attachment; filename="+sample+"_variations."+fileType})
	
