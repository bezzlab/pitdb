#This script insert data in the database.
import os
import numpy as np
import pandas as pd
import psycopg2
import yaml
import sys
import json
import csv
import re
import argparse
import site
site.addsitedir('/home/btw796/anaconda2/pkgs/biopython-1.68-np112py27_0/lib/python2.7/site-packages/')
from Bio import SeqIO

def readInfo(infoFile, sep):
	infoObj = pd.read_table(infoFile, sep=sep, keep_default_na=False, na_values=[''])
	return infoObj

def vcfVarReader(filename):
	vcf=readInfo(filename, '\t')
	info=pd.DataFrame(vcf.INFO.str.split(';').tolist(),columns=['SubjectID','QueryID','QueryLength','QueryStart','QueryEnd','SubjectLength','SubjectStart','SubjectEnd','Type','QPOS','PeptideCount','UniquePeptideCount','Peptides','Score'])
	vcf=vcf.drop('INFO',1)
	vcf=vcf.join(info)
	vcf.SubjectID=vcf.SubjectID.str.replace('SubjectId=','')
	vcf.QueryID=vcf.QueryID.str.replace('QueryId=','')
	vcf.QueryLength=vcf.QueryLength.str.replace('QueryLength=','')
	vcf.QueryStart=vcf.QueryStart.str.replace('QueryStart=','')
	vcf.QueryEnd=vcf.QueryEnd.str.replace('QueryEnd=','')
	vcf.SubjectLength=vcf.SubjectLength.str.replace('SubjectLength=','')
	vcf.SubjectStart=vcf.SubjectStart.str.replace('SubjectStart=','')
	vcf.SubjectEnd=vcf.SubjectEnd.str.replace('SubjectEnd=','')
	vcf.Type=vcf.Type.str.replace('Type=','')
	vcf.QPOS=vcf.QPOS.str.replace('QPOS=','')
	vcf.PeptideCount=vcf.PeptideCount.str.replace('PeptideCount=','')
	vcf.UniquePeptideCount=vcf.UniquePeptideCount.str.replace('UniquePeptideCount=','')
	vcf.Peptides=vcf.Peptides.str.replace('Peptides=','')
	vcf.Score=vcf.Score.str.replace('Score=','')
	return vcf

parser = argparse.ArgumentParser(description='PITDB data import')
parser.add_argument("--experimentInfo", required=True, help="Project information file")
parser.add_argument("--sampleInfo", required=True, help="Sample information file")
parser.add_argument("--data", required=True, help="Data folder path")

args = parser.parse_args()
dataPath = args.data
#Change following. We no longer have db.yml
#stream = open("db.yml", "r")
#db = yaml.load(stream)
#stream.close()

#change following. Make it command line arguments.
#expName  = "Bat"
#dataPath = "Data/"+ expName
#print (dataPath)
##Comment Following
#experimentInfo="/home/btw796/Data/HumanAdeno/experimentInfo.tsv"
#sampleInfo="/home/btw796/Data/HumanAdeno/sampleInfo.tsv"
#expInfo=readInfo(experimentInfo,'\t')
#sampleInfo=readInfo(sampleInfo,'\t')
#dataPath='/home/btw796/Data/HumanAdeno/'
#Uncomment following
expInfo=readInfo(args.experimentInfo,'\t')
sampleInfo=readInfo(args.sampleInfo,'\t')

#Insert into the experiment table:
if expInfo.shape[0]==1:
	try:
		con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
		cur = con.cursor()
		expINS = "INSERT INTO experiment (title, description, publication) VALUES (%s, %s, %s) " 
		cur.execute(expINS, (expInfo.iloc[0]['Title'], expInfo.iloc[0]['Description'], expInfo.iloc[0]['Publication']))
		con.commit()     
	except psycopg2.DatabaseError:
		if con:
			con.rollback()
		print('DatabaseError')    
		sys.exit(1)
	finally:
		if con:
			con.close()
			print("Connection closed")
else:
	print("Experiment Info size:"+str(expInfo.shape[0]))
	sys.exit(1)
##Update Experiment and insert accession number, user id.
#update experiment set accession = concat('EXP',repeat('0',6-length(id::char(9))),id);
#Insert into the sample table:
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	
	# We cannot have a duplicate name and exp_id ( AND exp_id = %)
	smpINS = 'INSERT INTO sample (name, exp_id, description) SELECT %s, %s, %s WHERE NOT EXISTS (SELECT id FROM sample WHERE name = %s AND exp_id = %s);' 
	for i in sampleInfo.index.values:
		sampleName = sampleInfo.loc[i]['SampleName']
		#check with sampleInfo dataframe and insert
		query = "SELECT id FROM experiment WHERE title = '"+expInfo.iloc[0]['Title']+"'"
		cur.execute(query)
		expID = cur.fetchone()[0]
#             print sampleName
		cur.execute(smpINS, (sampleName, expID, sampleInfo.loc[i]['Description'],sampleName, expID))
		con.commit()
	
except psycopg2.DatabaseError:
	if con:
		con.rollback()
	
	print('DatabaseError')    
	sys.exit(1)
	
finally:
	if con:
		con.close()
		print("Connection closed")
## Update sample accession
#update sample set accession = concat('SAMP',repeat('0',6-length(id::char(10))),id);
#Load the data into the tge table
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	
	# We cannot have duplicate TGE amino acid sequences 
	tgeINS = 'INSERT INTO tge (amino_seq) SELECT %s WHERE NOT EXISTS (SELECT id FROM tge WHERE amino_seq = %s);' 
	
	tgePath = dataPath + "AminoAcids-or-ORFs-orTGEs/"
	files = os.listdir(tgePath)
	for i in sampleInfo.index.values: #os.listdir(tgePath):
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		f=sampleName+".assemblies.fasta.transdecoder.pep.identified.fasta"
		if f not in files:
			##General
			f=sampleName+".fasta"
			if f not in files:
				print("Error amino acid fasta does not exist")
				sys.exit(1)
		for input in SeqIO.parse(tgePath+f, "fasta"):
			tgeSeq = input.seq
			tgeSeq = str(tgeSeq.strip(chars='*')) #str(tgeSeq[0:tgeSeq.find('*')])
			cur.execute(tgeINS, (tgeSeq, tgeSeq))
			con.commit()
except psycopg2.DatabaseError:
	if con:
		con.rollback()
	print('DatabaseError')    
	sys.exit(1)
	
finally:
	if con:
		con.close()
		print("Connection closed")

## Load the data into the <observation> table
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	
	tgeINS = 'INSERT INTO observation (tge_id, sample_id, name, description) SELECT %s , %s , %s, %s WHERE NOT EXISTS (SELECT id FROM observation WHERE description = %s AND sample_id = %s);' 
	
	tgePath = dataPath + "AminoAcids-or-ORFs-orTGEs/"
	files = os.listdir(tgePath)
	for i in sampleInfo.index.values: #os.listdir(tgePath):
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		f=sampleName+".assemblies.fasta.transdecoder.pep.identified.fasta"
		if f not in files:
			##General
			f=sampleName+".fasta"
			if f not in files:
				print("Error amino acid fasta does not exist")
				sys.exit(1)
		query = "SELECT id FROM experiment WHERE title = '"+expInfo.iloc[0]['Title']+"'"
		cur.execute(query)
		expID = cur.fetchone()[0]
		for input in SeqIO.parse(tgePath+f, "fasta"):
			# WE SHOULD TAKE THE EXPERIMENT NAME TOO
			query = ("SELECT id FROM sample WHERE name = %s AND exp_id= %s")
			cur.execute(query, (sampleName, expID))
			sampleID = cur.fetchone()[0]            
			tgeName  = input.id
			tgeName  = tgeName[0:tgeName.find('|')]
			tgeSeq = input.seq
			tgeSeq = str(tgeSeq.strip(chars='*'))
			query = ("SELECT id FROM tge WHERE tge.amino_seq = '"+tgeSeq+"'")
			cur.execute(query)
			tgeID = cur.fetchone()[0]
			cur.execute(tgeINS, (tgeID, sampleID, tgeName, input.id, input.id, sampleID))
			con.commit()
except psycopg2.DatabaseError:
	if con:
		con.rollback()
	print('DatabaseError')    
	sys.exit(1)	
finally:
	if con:
		con.close()
		print("Connection closed")

## Load the data into the <transcript> table

try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	trsINS = 'INSERT INTO transcript (dna_seq) SELECT %s WHERE NOT EXISTS (SELECT id FROM transcript WHERE dna_seq  = %s);'
	trsPath = dataPath + "/transcripts/"
	trnFiles=os.listdir(trsPath)
	query = "SELECT id FROM experiment WHERE title = '"+expInfo.iloc[0]['Title']+"'"
	cur.execute(query)
	expID = cur.fetchone()[0]
	for i in sampleInfo.index.values: #os.listdir(tgePath):
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		f=sampleName+".assemblies.fasta.identified.fasta"
		if f not in trnFiles:
			##General
			f=sampleName+".fasta"
			if f not in trnFiles:
				print("Error amino acid fasta does not exist")
				sys.exit(1)
		for input in SeqIO.parse(trsPath+f, "fasta"):
			trsName = input.id
			trsSeq  = str(input.seq)
			cur.execute(trsINS, (trsSeq, trsSeq))
			con.commit()
except psycopg2.DatabaseError:
	if con:
		con.rollback()
	print('DatabaseError')    
	sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")

## Load the data into the <transcript_observation> table

try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	trsObsINS = 'INSERT INTO transcript_observation (obs_id, transcript_id) SELECT %s , %s WHERE NOT EXISTS (SELECT id FROM transcript_observation WHERE obs_id = %s AND transcript_id  = %s);'
	trsPath = dataPath + "/transcripts/"
	trnFiles=os.listdir(trsPath)
	query = "SELECT id FROM experiment WHERE title = '"+expInfo.iloc[0]['Title']+"'"
	cur.execute(query)
	expID = cur.fetchone()[0]
	for i in sampleInfo.index.values: #os.listdir(tgePath):
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		f=sampleName+".assemblies.fasta.identified.fasta"
		if f not in trnFiles:
			##General
			f=sampleName+".fasta"
			if f not in trnFiles:
				print("Error amino acid fasta does not exist")
				sys.exit(1)
		query = ("SELECT id FROM sample WHERE name = %s AND exp_id= %s")
		cur.execute(query, (sampleName, expID))
		sampleID = cur.fetchone()[0]
		for input in SeqIO.parse(trsPath+f, "fasta"):
			trsName = input.id
			trsSeq  = str(input.seq)
			trnQuery = "SELECT id FROM transcript WHERE dna_seq = '"+trsSeq+"'"
			cur.execute(trnQuery)
			trnID = cur.fetchone()[0]
			obsQuery = ("SELECT id FROM observation WHERE name = %s AND sample_id= %s")
			cur.execute(obsQuery, (trsName, sampleID))
			obsIDs = cur.fetchall()
			for obsID in obsIDs:
				cur.execute(trsObsINS, (obsID[0], trnID, obsID[0], trnID))
				con.commit()
except psycopg2.DatabaseError:
	if con:
		con.rollback()
	print('DatabaseError')    
	sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")

## update annotation in observation
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	tgeALT = 'UPDATE observation SET organism = %s, uniprot_id = %s, protein_name= %s, protein_descr = %s, gene_name = %s, tge_class = %s, variation = %s, long_description = %s, score = %s, ref_score = %s, score_annot = %s, star = %s, star_str = %s  WHERE description = %s AND sample_id = %s;'
	sumPath = dataPath + "/Summary/"
	sumFiles=os.listdir(sumPath)
	prtPath = dataPath + "/PSMs-Peptides-ORFs/"
	prtFiles = os.listdir(prtPath)
	query = "SELECT id FROM experiment WHERE title = '"+expInfo.iloc[0]['Title']+"'"
	cur.execute(query)
	expID = cur.fetchone()[0]
	nc=0
	for i in sampleInfo.index.values:
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		f=sampleName+".summary.tsv"
		prtF=sampleName+"+fdr+th+grouping+prt_filtered.csv"
		if f not in sumFiles and prtF not in prtFiles:
			##General
			f=sampleName+".tsv"
			prtF=sampleName+"+prt.csv"
			if f not in sumFiles and prtF not in prtFiles:
				print("Error summary tsv or protein csv or both does not exist")
				sys.exit(1)
		query = ("SELECT id FROM sample WHERE name = %s AND exp_id= %s")
		cur.execute(query, (sampleName, expID))
		sampleID = cur.fetchone()[0]
		
		summary = readInfo(sumPath+f,'\t')
		summary['Score'] = summary['Score'].fillna(0)
		summary['RefScore'] = summary['RefScore'].fillna(0)
		proteins = readInfo(prtPath+prtF,',')
		proteins['unique peptides'].fillna(0,inplace=True)
		for j in range(summary.shape[0]): 
			descr  = summary.iloc[j]['ORF Id']
			tgeDescr  = descr[0:descr.find(' ')]
			uniprotID = summary.iloc[j]['Protein ID']
			if uniprotID is None:
				uniprotID = '-'
			proteinName  = str(summary.iloc[j]['Protein Name'])
			geneName     = str(summary.iloc[j]['Gene Name'])
			proteinDescr = str(summary.iloc[j]['Protein description'])
			tgeClass  = str(summary.iloc[j]['Class'])
			variation = int(summary.iloc[j]['Variation'])
			species   = str(summary.iloc[j]['Species'])
			score = float(summary.iloc[j]['Score'])
			refScore = float(summary.iloc[j]['RefScore'])
			scoreAnnot = 'Ref'
			if summary.iloc[j]['Decision'] == 'Iso':
				scoreAnnot = 'Var'
			star_str = ''
			star = '*' * 5
			##discuss class associated variation peptide check. Add novel class case
			if summary.iloc[j]['Class']=='known variation' or summary.iloc[j]['Class']=='ALT_SPLICE':
				if summary.iloc[j]['UnqVarPeptide'] == 'Yes':
					if summary.iloc[j]['Decision'] == 'Iso':
						if 'type:complete' in summary.iloc[j]['ORF Id']:
							star = '*' * 5 
							star_str = 'uscv'
						else:
							star = '*' * 3 + 'O' * 2
							star_str = 'usv'
					else:
						if 'type:complete' in summary.iloc[j]['ORF Id']:
							star = '*' * 4 + 'O' * 1
							star_str = 'ucv'
						else:
							star = '*' * 3 + 'O' * 2
							star_str = 'uv'
				else:
					if summary.iloc[j]['VarPeptide'] == 'Yes':
						if summary.iloc[j]['Decision'] == 'Iso':
							if 'type:complete' in summary.iloc[j]['ORF Id']:
								star = '*' * 4 + 'O' * 1
								star_str = 'scv'
							else:
								star = '*' * 2 + 'O' * 3
								star_str = 'sv'
						else:
							if 'type:complete' in summary.iloc[j]['ORF Id']:
								star = '*' * 3 + 'O' * 2
								star_str = 'cv'
							else:
								star = '*' * 2 + 'O' * 3
								star_str = 'v'
					else:
						if summary.iloc[j]['Decision'] == 'Iso':
							if 'type:complete' in summary.iloc[j]['ORF Id']:
								star = '*' * 2 + 'O' * 3
								star_str = 'sc'
							else:
								star = '*' * 1 + 'O' * 4
								star_str = 's'
						else:
							if 'type:complete' in summary.iloc[j]['ORF Id']:
								star = '*' * 1 + 'O' * 4
								star_str = 'c'
							else:
								star = 'O' * 5
								star_str = ''
			else:
				if 'prime' in summary.iloc[j]['Class']:
					if summary.iloc[j]['IsoUnqPeptide'] == 'Yes':
						if summary.iloc[j]['Decision'] == 'Iso':
							if 'type:complete' in summary.iloc[j]['ORF Id']:
								star = '*' * 5
								star_str = 'uscv'
							else:
								star = '*' * 3 + 'O' * 2
								star_str = 'usv'
						else:
							if 'type:complete' in summary.iloc[j]['ORF Id']:
								star = '*' * 4 + 'O' * 1
								star_str = 'ucv'
							else:
								star = '*' * 3 + 'O' * 2
								star_str = 'uv'
					else:
						if summary.iloc[j]['IsoPeptide'] == 'Yes':
							if summary.iloc[j]['Decision'] == 'Iso':
								if 'type:complete' in summary.iloc[j]['ORF Id']:
									star = '*' * 4 + 'O' * 1
									star_str = 'scv'
								else:
									star = '*' * 2 + 'O' * 3
									star_str = 'sv'
							else:
								if 'type:complete' in summary.iloc[j]['ORF Id']:
									star = '*' * 3 + 'O' * 2
									star_str = 'cv'
								else:
									star = '*' * 2 + 'O' * 3
									star_str = 'v'
						else:
							if summary.iloc[j]['Decision'] == 'Iso':
								if 'type:complete' in summary.iloc[j]['ORF Id']:
									star = '*' * 2 + 'O' * 3
									star_str = 'sc'
								else:
									star = '*' * 1 + 'O' * 4
									star_str = 's'
							else:
								if 'type:complete' in summary.iloc[j]['ORF Id']:
									star = '*' * 1 + 'O' * 4
									star_str = 'c'
								else:
									star = 'O' * 5
									star_str = ''
				elif summary.iloc[j]['Class'] == 'novel':
					nc=nc+1
					geneName =''
					##Check if this TGE observation had any unique peptide.
					star = 'O' * 5
					##REad protein export csv and see if it has unique protein and whether its an anchor protein. If all of these are true, and its a complete ORF that will be 4 *.
					star_str=''
					novelPrt=proteins[proteins['description']==summary.iloc[j]['ORF Id']]
					if novelPrt.shape[0]==1:
						#print "noverprt unq:"+str(novelPrt['unique peptides'])
						if novelPrt.iloc[0]['unique peptides']>0:
							if novelPrt.iloc[0]['group membership']=='anchor protein':
								if 'type:complete' in novelPrt.iloc[0]['description']:
									star = '*' * 4
									star_str = 'uac'
								else:
									star = '*' * 3
									star_str = 'ua'
							elif 'type:complete' in novelPrt.iloc[0]['description']:
								star = '*' * 3
								star_str = 'uc'
							else:
								star = '*' * 2
								star_str = 'u'
						elif novelPrt.iloc[0]['group membership']=='anchor protein':
							if 'type:complete' in novelPrt.iloc[0]['description']:
								star = '*' * 2
								star_str = 'ac'
							else:
								star = '*' * 1
								star_str = 'a'
						else:
							if 'type:complete' in novelPrt.iloc[0]['description']:
								star = '*' * 1
								star_str = 'c'
							else:
								star = '*' * 0
								star_str = ''
					else:
						print "Novel protein was not found in protein DF or multiple found"+str(summary.iloc[j]['ORF Id'])
			#print (species, uniprotID, proteinName, proteinDescr, geneName, tgeClass, variation, descr, score, refScore, scoreAnnot, star, star_str, tgeDescr, sampleID)
			cur.execute(tgeALT, (species, uniprotID, proteinName, proteinDescr, geneName, tgeClass, variation, descr, score, refScore, scoreAnnot, star, star_str, tgeDescr, sampleID))
			con.commit()
except psycopg2.DatabaseError:
	if con:
		con.rollback()
	print('DatabaseError')    
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")
## update observation table with peptide number 

try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	tgeALT = 'UPDATE observation SET peptide_num = %s WHERE description = %s AND sample_id = %s'
	
	prtPath = dataPath + "/PSMs-Peptides-ORFs/"
	prtFiles = os.listdir(prtPath)
	query = "SELECT id FROM experiment WHERE title = '"+expInfo.iloc[0]['Title']+"'"
	cur.execute(query)
	expID = cur.fetchone()[0]
	for i in sampleInfo.index.values:
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		prtF=sampleName+"+fdr+th+grouping+prt_filtered.csv"
		if prtF not in prtFiles:
			##General
			prtF=sampleName+"+prt.csv"
			if prtF not in prtFiles:
				print("Error protein csv or both does not exist")
				sys.exit(1)
		query = ("SELECT id FROM sample WHERE name = %s AND exp_id= %s")
		cur.execute(query, (sampleName, expID))
		sampleID = cur.fetchone()[0]		
		tge = readInfo(prtPath+prtF,sep=',')
		for j in range(len(tge)): 
			descr  = str(tge.iloc[j]['description'])
			tgeID  = descr[0:descr.find(' ')]
			pepNum = int(tge.iloc[j]['distinct peptide sequences'])
			cur.execute(tgeALT, (pepNum, tgeID, sampleID))
			con.commit()
except (psycopg2.DatabaseError, e):
	if con:
		con.rollback()
	
	print('Error %s' % e)    
	#sys.exit(1)
	
finally:
	if con:
		con.close()
		print("Connection closed")

## Insert into peptide 

try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insPep = 'INSERT INTO peptide (aa_seq) SELECT %s WHERE NOT EXISTS (SELECT id FROM peptide WHERE aa_seq = %s);'
	
	prtPath = dataPath + "/PSMs-Peptides-ORFs/"
	prtFiles = os.listdir(prtPath)
	query = "SELECT id FROM experiment WHERE title = '"+expInfo.iloc[0]['Title']+"'"
	cur.execute(query)
	expID = cur.fetchone()[0]
	for i in sampleInfo.index.values:
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		pepF=sampleName+"+fdr+th+grouping_filtered.csv"
		if pepF not in prtFiles:
			##General
			pepF=sampleName+".csv"
			if pepF not in prtFiles:
				print("Error protein csv or both does not exist")
				sys.exit(1)
		query = ("SELECT id FROM sample WHERE name = %s AND exp_id= %s")
		cur.execute(query, (sampleName, expID))
		sampleID = cur.fetchone()[0]		
		peptides = readInfo(prtPath+pepF,sep=',')
		for j in range(len(peptides)):
			#m = re.search("(?<=index=).*?$", peptides.iloc[j]['Spectrum ID'])
			#specID = m.group(0)			
			amino   = peptides.iloc[j]['Sequence']		
			cur.execute(insPep, (amino, amino))
			con.commit()	
except psycopg2.DatabaseError:
	if con:
		con.rollback()
	
	print('DataBaseError')    
	#sys.exit(1)
	
finally:
	if con:
		con.close()
		print("Connection closed")

## Peptides for each TGE

try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insTgePep = 'INSERT INTO tge_peptide (obs_id, peptide_id) SELECT %s , %s WHERE NOT EXISTS (SELECT id FROM tge_peptide WHERE obs_id = %s AND peptide_id  = %s);'
	prtPath = dataPath + "/PSMs-Peptides-ORFs/"
	prtFiles = os.listdir(prtPath)
	query = "SELECT id FROM experiment WHERE title = '"+expInfo.iloc[0]['Title']+"'"
	cur.execute(query)
	expID = cur.fetchone()[0]
	for i in sampleInfo.index.values:
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		pepF=sampleName+"+fdr+th+grouping_filtered.csv"
		if pepF not in prtFiles:
			##General
			pepF=sampleName+".csv"
			if pepF not in prtFiles:
				print("Error protein csv or both does not exist")
				sys.exit(1)
		query = ("SELECT id FROM sample WHERE name = %s AND exp_id= %s")
		cur.execute(query, (sampleName, expID))
		sampleID = cur.fetchone()[0]		
		peptides = readInfo(prtPath+pepF,sep=',')
		for j in range(len(peptides)):
			amino   = peptides.iloc[j]['Sequence']
			query = ("SELECT id FROM peptide WHERE aa_seq = '"+amino+"'") 
			cur.execute(query)
			pepID = cur.fetchone()[0]
			proteinacc = peptides.iloc[j]['proteinacc_start_stop_pre_post_;']
			arr =  proteinacc.split(';')
			for x in range(0, len(arr)):
				n=2
				tge = arr[x]                    
				m=re.match(r'^((?:[^_]*_){%d}[^_]*)_(.*)' % (n-1), tge)
				tgeDescr = m.groups()[0]
				query = ("SELECT id FROM observation WHERE description = '"+tgeDescr+"' AND sample_id = "+str(sampleID))
				cur.execute(query)
				tgeID = cur.fetchone()
				if tgeID:
					tgeID = tgeID[0]
					cur.execute(insTgePep, (tgeID, pepID,tgeID, pepID ))
					con.commit()
except psycopg2.DatabaseError:
	if con:
		con.rollback()
	print('Error %s' % e)    
#     sys.exit(1)
finally:
	if con:
		con.close()
	print("Connection closed")

## Insert into psm 

try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insSpec = 'INSERT INTO psm (pep_id, psm_id, spectrum_id, title, location, retention, calc_mz, exp_mz, charge, modifications, raw_score, denovo_score, spec_evalue, evalue, qvalue, pep_qvalue, local_fdr, q_value, fdr_score ) SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT id FROM psm WHERE spectrum_id = %s AND pep_id = %s AND modifications = %s and psm_id = %s);'
	prtPath = dataPath + "/PSMs-Peptides-ORFs/"
	prtFiles = os.listdir(prtPath)
	for i in sampleInfo.index.values:
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		pepF=sampleName+"+fdr+th+grouping_filtered.csv"
		if pepF not in prtFiles:
			##General
			pepF=sampleName+".csv"
			if pepF not in prtFiles:
				print("Error protein csv or both does not exist")
				sys.exit(1)
		psms = readInfo(prtPath+pepF,sep=',')
		psms['Modifications'].fillna("",inplace=True)
		for j in range(len(psms)):
			##star from here
			location  = psms.iloc[j]['Raw data location']
			m = re.search('^index=(.+?)$', psms.iloc[j]['Spectrum ID'])
			if m:
				specID = m.group(1)
			else:
				print("Spetra Index does not starts with index:"+psms.iloc[j]['Spectrum ID'])
			#specID = 
			specTitle = psms.iloc[j]['Spectrum Title']
			amino   = psms.iloc[j]['Sequence']
			query = ("SELECT id FROM peptide WHERE aa_seq = '"+amino+"'") 
			cur.execute(query)
			pepID = cur.fetchone()[0]
			cur.execute(insSpec, (pepID, psms.iloc[j]['PSM_ID'], specID, specTitle, location, psms.iloc[j]['Retention Time (s)'], psms.iloc[j]['Calc m/z'], psms.iloc[j]['Exp m/z'], psms.iloc[j]['Charge'], psms.iloc[j]['Modifications'], psms.iloc[j]['MS-GF:RawScore'], psms.iloc[j]['MS-GF:DeNovoScore'], psms.iloc[j]['MS-GF:SpecEValue'], psms.iloc[j]['MS-GF:EValue'], psms.iloc[j]['MS-GF:QValue'], psms.iloc[j]['MS-GF:PepQValue'], psms.iloc[j]['PSM-level local FDR'], psms.iloc[j]['PSM-level q-value'], psms.iloc[j]['PSM-level FDRScore'], specID, pepID, psms.iloc[j]['Modifications'], psms.iloc[j]['PSM_ID']))
			con.commit()
except psycopg2.DatabaseError as e:
	if con:
		con.rollback()
	print('DatabaseError')  
	print(e)  
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")

#Insert into variation
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insVar = 'INSERT INTO variation (ref_id, chrom, pos, ref_aa, alt_aa, var_type) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT id FROM variation WHERE ref_id = %s AND pos = %s AND ref_aa = %s and alt_aa = %s);'
	vcfPath = dataPath + "/Variations-proVCF/"
	vcfFiles = os.listdir(vcfPath)
	for i in sampleInfo.index.values:
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		vcfF=sampleName+".assemblies.fasta.transdecoder.pep_pepEvd.vcf"
		if vcfF not in vcfFiles:
			##General
			vcfF=sampleName+".vcf"
			if vcfF not in vcfFiles:
				print("Error vcf file does not exist")
				sys.exit(1)
		vcf = vcfVarReader(vcfPath+vcfF)
		for j in range(vcf.shape[0]):
			cur.execute(insVar, (vcf.iloc[j]['SubjectID'], vcf.iloc[j]['#CHROM'], vcf.iloc[j]['POS'], vcf.iloc[j]['REF'], vcf.iloc[j]['ALT'], vcf.iloc[j]['Type'], vcf.iloc[j]['SubjectID'], vcf.iloc[j]['POS'], vcf.iloc[j]['REF'], vcf.iloc[j]['ALT']))
			con.commit()
except psycopg2.DatabaseError as e:
	if con:
		con.rollback()
	print('DatabaseError') 
	print(e)   
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")


#Insert into variation_observation
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insVar = 'INSERT INTO variation_observation (obs_id, var_id, qual, qpos, peptide_num, unique_peptides) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT id FROM variation_observation WHERE obs_id = %s AND var_id = %s);'
	vcfPath = dataPath + "/Variations-proVCF/"
	vcfFiles = os.listdir(vcfPath)
	query = "SELECT id FROM experiment WHERE title = '"+expInfo.iloc[0]['Title']+"'"
	cur.execute(query)
	expID = cur.fetchone()[0]
	for i in sampleInfo.index.values:
		sampleName = sampleInfo.loc[i]['SampleName']
		##check which file has a file name containing the sample name
		##For our pipeline
		vcfF=sampleName+".assemblies.fasta.transdecoder.pep_pepEvd.vcf"
		if vcfF not in vcfFiles:
			##General
			vcfF=sampleName+".vcf"
			if vcfF not in vcfFiles:
				print("Error vcf file does not exist")
				sys.exit(1)
		query = ("SELECT id FROM sample WHERE name = %s AND exp_id= %s")
		cur.execute(query, (sampleName, expID))
		sampleID = cur.fetchone()[0]
		vcf = vcfVarReader(vcfPath+vcfF)
		for j in range(vcf.shape[0]):
			query = ("SELECT id FROM observation WHERE description = %s AND sample_id = %s")
			cur.execute(query, (vcf.iloc[j]['QueryID'], sampleID))
			obs_id = cur.fetchone()[0]
			query = ("SELECT id FROM variation WHERE ref_id = %s AND pos = %s AND ref_aa= %s and alt_aa=%s")
			cur.execute(query, (vcf.iloc[j]['SubjectID'], vcf.iloc[j]['POS'],vcf.iloc[j]['REF'],vcf.iloc[j]['ALT']))
			var_id = cur.fetchone()[0]
			cur.execute(insVar, (obs_id, var_id, vcf.iloc[j]['QUAL'], vcf.iloc[j]['QPOS'], vcf.iloc[j]['PeptideCount'], vcf.iloc[j]['Peptides'], obs_id, var_id))
			con.commit()
except psycopg2.DatabaseError as e:
	if con:
		con.rollback()
	print('DatabaseError') 
	print(e)   
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")

##Update TGE table, insert uniprot id

try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insVar = 'UPDATE tge SET uniprot_id = ( SELECT string_agg(distinct(observation.uniprot_id),\',\') from observation where observation.tge_id =tge.id);'
	cur.execute(insVar)
	con.commit()
except psycopg2.DatabaseError as e:
	if con:
		con.rollback()
	print('DatabaseError') 
	print(e)   
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")

#Update TGE organisms
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insVar = 'UPDATE tge SET organisms = (SELECT string_agg(distinct(observation.organism),\',\') from observation where observation.tge_id =tge.id);'
	cur.execute(insVar)
	con.commit()
except psycopg2.DatabaseError as e:
	if con:
		con.rollback()
	print('DatabaseError') 
	print(e)   
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")

#Update TGE star
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insVar = 'UPDATE tge SET star = (SELECT repeat(\'*\',max(array_length(string_to_array(star, \'*\'), 1) - 1)) from observation where observation.tge_id =tge.id);'
	cur.execute(insVar)
	con.commit()
except psycopg2.DatabaseError as e:
	if con:
		con.rollback()
	print('DatabaseError') 
	print(e)   
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")

##UPDATE TGE ACCESSION
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insVar = 'UPDATE tge SET accession = concat(\'TGE\',repeat(\'0\',7-length(id::char(10))),id);'
	cur.execute(insVar)
	con.commit()
except psycopg2.DatabaseError as e:
	if con:
		con.rollback()
	print('DatabaseError') 
	print(e)   
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")


#Update TGE tge_class
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insVar = 'UPDATE tge SET tge_class = (SELECT string_agg(distinct(observation.tge_class),\',\') from observation where observation.tge_id =tge.id);'
	cur.execute(insVar)
	con.commit()
except psycopg2.DatabaseError as e:
	if con:
		con.rollback()
	print('DatabaseError') 
	print(e)   
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")


#Update TGE genes
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	insVar = 'UPDATE tge SET gene_names = (SELECT string_agg(distinct(observation.gene_name),\',\') from observation where observation.tge_id =tge.id);'
	cur.execute(insVar)
	con.commit()
except psycopg2.DatabaseError as e:
	if con:
		con.rollback()
	print('DatabaseError') 
	print(e)   
	#sys.exit(1)
finally:
	if con:
		con.close()
		print("Connection closed")

##Insert into table exp_stat
try:
	con = psycopg2.connect(database=os.environ['RDS_DB_NAME'], user=os.environ['RDS_USERNAME'], host=os.environ['RDS_HOSTNAME'], password=os.environ['RDS_PASSWORD'])
	cur = con.cursor()
	expStatINS = 'INSERT INTO exp_stat (exp_id, sample_id, tge_num, trn_num, pep_num, psms_num, var_num) SELECT %s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT id FROM exp_stat WHERE exp_id = %s AND sample_id = %s);' 
	cur.execute("SELECT id from experiment;")
	expIDs = cur.fetchall()
	for exp in expIDs:
		query = "SELECT id FROM sample WHERE exp_id = "+str(exp[0])+";"
		cur.execute(query)
		sampleIDs = cur.fetchall()
		for s in sampleIDs:
			query = "SELECT count(distinct(tge_id)) from observation where sample_id="+str(s[0])+";"
			cur.execute(query)
			tge_num = int(cur.fetchone()[0])
			query = "SELECT count(distinct(ot.transcript_id)) from transcript_observation as ot, observation as o where ot.obs_id=o.id AND o.sample_id="+str(s[0])+";"
			cur.execute(query)
			trn_num = int(cur.fetchone()[0])
			query = "SELECT count(distinct(tp.peptide_id)) from tge_peptide as tp, observation as o where tp.obs_id=o.id AND o.sample_id="+str(s[0])+";"
			cur.execute(query)
			pep_num = int(cur.fetchone()[0])
			query = "SELECT count(distinct(p.psm_id)) from psm as p, tge_peptide as tp, observation as o where p.pep_id=tp.peptide_id AND tp.obs_id=o.id AND o.sample_id="+str(s[0])+";"
			cur.execute(query)
			psms_num = int(cur.fetchone()[0])
			query = "SELECT count(distinct(v.var_id)) from variation_observation as v, observation as o where v.obs_id=o.id AND o.sample_id="+str(s[0])+";"
			cur.execute(query)
			var_num = int(cur.fetchone()[0])			
			cur.execute(expStatINS, (exp[0], s[0], tge_num, trn_num, pep_num, psms_num, var_num, exp[0], s[0]))
			con.commit()
	
except psycopg2.DatabaseError:
	if con:
		con.rollback()
	
	print('DatabaseError')    
	sys.exit(1)
	
finally:
	if con:
		con.close()
		print("Connection closed")
