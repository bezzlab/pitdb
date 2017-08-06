import os
import re
# import urllib
import locale
import pandas  as pd

from pit_app import db
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.sql import func, distinct
from sqlalchemy import desc
from pit_app.models import *
from pit_app import db
from flask import Markup
#from sqlalchemy.dialects.postgresql import aggregate_order_by
results = Blueprint('results',  __name__)

@results.route('/tge')
def tge():
  # Get the argument - accession
  accession = request.args['accession']

  # Find the TGE for the given accession number
  tge        = TGE.query.filter_by(accession=accession).first_or_404()
  tgeObs     = Observation.query.filter_by(tge_id=tge.id).order_by(desc(Observation.peptide_num))
  obsCount   = tgeObs.count()

  pepLengths = Peptide.query.with_entities(func.length(Peptide.aa_seq).label('pepLength')).\
                    join(TgeToPeptide).join(Observation).join(TGE).\
                    filter_by(id=tge.id).group_by(Peptide.aa_seq).all() 
  peps = Peptide.query.with_entities(distinct(Peptide.aa_seq).label('pep')).join(TgeToPeptide).join(Observation).\
                    filter_by(tge_id=tge.id).all()
  #print(peps)
  query="SELECT p.aa_seq as aa_seq, count(distinct(psm.psm_id)) as psm_count, string_agg(distinct(psm.charge)::char,\',\') as charge, string_agg(distinct(nullif(psm.modifications,''))::char(400),\',\') as modifications, to_char(min(psm.pep_qvalue),'EEEE') AS pep_qvalue, to_char(min(psm.local_fdr),'EEEE') as local_fdr from psm JOIN peptide p ON psm.pep_id=p.id JOIN tge_peptide tp ON p.id=tp.peptide_id JOIN observation o ON tp.obs_id=o.id where o.tge_id="+str(tge.id)+" group by p.aa_seq;"
  pepInfo1 = db.engine.execute(query).fetchall()
  pepInfo = [pI for pI in pepInfo1]
  #print(pepInfo)
  varQuery = "SELECT v.ref_id as ref_id, v.pos as pos, v.ref_aa as ref_aa, v.alt_aa as alt_aa, v.var_type as var_type, count(distinct(vo.obs_id)) as obs_count, string_agg(distinct(vo.qpos)::char(10),\',\') as qpos, max(vo.peptide_num) as pep_evd, string_agg(distinct(vo.unique_peptides),\',\') AS unq_peptides from variation as v JOIN variation_observation vo ON v.id=vo.var_id JOIN observation o ON vo.obs_id=o.id where o.tge_id="+str(tge.id)+" group by v.ref_id, v.pos, v.ref_aa, v.alt_aa, v.var_type;"
  variations1 = db.engine.execute(varQuery).fetchall()
  if len(variations1)==0:
    variations = None
  else:
    variations = [v1 for v1 in variations1]
  print(variations)
  avgPeptNum = Observation.query.with_entities(func.avg(Observation.peptide_num).label('average')).\
                    filter_by(tge_id=tge.id).one()

  # Flatten out the list of lists to lists (to use in the for loops)
  pepLengths = [item for sublist in pepLengths for item in sublist]

  avgPeptCov = '-'
  
  if (sum(pepLengths)):
    avgPeptCov = float(len(tge.amino_seq))/sum(pepLengths)

  summary    = { 'tge' : tge, 'tgeObs' : tgeObs, 'organisms' : tge.organisms, 'avgPeptNum' : avgPeptNum.average, 
                  'tgeClasses' : tge.tge_class, 'obsCount' : obsCount, 'uniprotIDs': tge.uniprot_id, 
                  'genes': tge.gene_names, 'avgPeptCov': avgPeptCov };

  results  = []
  
  for obs in tgeObs:
    #correct following
    exp = Experiment.query.with_entities(Experiment.id, Experiment.accession, Sample.name, Sample.accession.label('saccession')).\
                    join(Sample).join(Observation).filter_by(id=obs.id).one()
    
    tgeType    = re.search("(?<=type:).*?(?=\s)", obs.long_description).group(0)
    tgeLength  = re.search("(?<=len:).*?(?=\s)",  obs.long_description).group(0)
    tgeStrand  = re.search("(?<=\().*?(?=\))",    obs.long_description).group(0)

    peptides = Peptide.query.with_entities(Peptide.aa_seq).join(TgeToPeptide).filter_by(obs_id=obs.id).order_by(Peptide.aa_seq).all()
    peptides = [item for sublist in peptides for item in sublist]
    
    results.append({'id': obs.id, 'observation': obs.name, 'sampleName': exp.saccession, 'expAccession': exp.accession, 
                    'expID': exp.id, 'tgeClass': obs.tge_class,'type': tgeType, 'length': tgeLength, 'strand':tgeStrand, 'organism': obs.organism, 
                    'uniprotID': obs.uniprot_id, 'peptide_num': obs.peptide_num, 'peptides': peptides, 'star':len(str(obs.star).replace('O','')), 'evidence':str(obs.star_str).upper(),'protein_name':obs.protein_name,'protein_desc': obs.protein_descr })

  return render_template('results/tge.html', summary = summary, results=results, pepInfo = pepInfo, variations = variations)


@results.route('/organism')
def organism():
  tgeList = []

  organism   = request.args['organism']
  obs        = Observation.query.filter(Observation.organism.like("%"+organism+"%"))
  tgeClasses = Observation.query.with_entities(Observation.tge_class).\
                  filter(Observation.organism.like("%"+organism+"%")).group_by(Observation.tge_class).all()

  tgeClasses = [item for sublist in tgeClasses for item in sublist]

  tges = db.engine.execute("SELECT tge.accession, string_agg(distinct(observation.tge_class), ', ') AS tge_class, string_agg(distinct(observation.uniprot_id), ', ') AS uniprot_id "+ 
                      " FROM tge JOIN observation ON tge.id = observation.tge_id WHERE observation.organism LIKE '%%"+organism+"%%' "+
                      " GROUP BY tge.accession ORDER BY tge.accession").fetchall(); 

  tgeNum     = separators(obs.distinct(Observation.tge_id).count())
  sampleNum  = separators(obs.join(Sample).distinct(Sample.id).count())
  expNum     = separators(obs.join(Sample).join(Experiment).distinct(Experiment.id).count())

  trnNum    = separators(Transcript.query.with_entities(distinct(Transcript.dna_seq)).\
                join(TranscriptToObservation).join(Observation).filter(Observation.organism.like("%"+organism+"%")).count())

  pepNum    = separators(Observation.query.with_entities(func.sum(Observation.peptide_num)).\
                    filter(Observation.organism.like("%"+organism+"%")).scalar())

  summary  = {'organism': organism,'tgeNum': tgeNum, 'sampleNum': sampleNum, 'expNum': expNum, 'trnNum': trnNum, 'pepNum' : pepNum };
  
  # for tge in tges: 
  #   tgeList.append({'accession': tge[0], 'tgeClasses': tge[1], 'uniprotIDs': tge[2] }) #  })
  
  return render_template('results/organism.html', summary = summary, tges = tges, tgeClasses = tgeClasses)


@results.route('/experiment')
def experiment():
  experiment  = request.args['experiment']
  exp  = Experiment.query.filter_by(accession=experiment).first_or_404()
  user = User.query.with_entities(User.fullname).filter_by(id=exp.user_id).one()
  print("EXP:"+str(exp.id))
  print("User:"+str(exp.user_id))

  samples = Sample.query.with_entities(Sample.id, Sample.name).\
              filter_by(exp_id=exp.id).\
              group_by(Sample.id, Sample.name).all()

  tges = TGE.query.join(Observation).join(Sample).filter_by(exp_id=exp.id).all()
  query="SELECT ot.transcript_id as tid, string_agg(distinct(s.exp_id)::char,\',\') as sample_exp, string_agg(distinct(t.accession),\',\') as tge_acc,string_agg(distinct(ot.obs_id)::char,\',\') as obs_id, string_agg(distinct(o.gene_name),\',\') AS genes, string_agg(distinct(s.accession),\',\') as sample_acc from transcript_observation ot JOIN observation o ON ot.obs_id=o.id JOIN tge t ON t.id=o.tge_id JOIN sample s ON o.sample_id=s.id where s.exp_id="+str(exp.id)+" group by ot.transcript_id;"
  #query="SELECT ot.transcript_id, string_agg(distinct(ot.obs_id)::char,\',\') as obs_id, string_agg(distinct(o.gene_name),\',\') AS genes, string_agg(distinct(o.sample_id)::char,\',\') as sample_acc from transcript_observation ot JOIN observation o ON ot.obs_id=o.id JOIN sample s ON o.sample_id=s.id where s.exp_id="+str(exp.id)+" group by ot.transcript_id;"
  trns = db.engine.execute(query)
  #TranscriptToObservation.query.join(Observation).join(Sample).filter(Sample.exp_id==exp.id).with_entities(TranscriptToObservation.transcript_id, func.string_agg(TranscriptToObservation.obs_id, ','), Observation.gene_name, Observation.sample_id).group_by(TranscriptToObservation.transcript_id).all()
  # tgeExp = func.string_agg(Observation.tge_id, aggregate_order_by(literal_column("','")))
  # genes = func.string_agg(Observation.gene_name, aggregate_order_by(literal_column("','")))
  # sampleAcc = func.string_agg(Sample.accession, aggregate_order_by(literal_column("','")))
  # trns = db.session.query(TranscriptToObservation.transcript_id, tgeExp.label('tge_acc'), genes.label('genes'), sampleAcc.label('sample_acc')).filter( TranscriptToObservation.obs_id==Observation.id, Observation.sample_id==Sample.id, Sample.exp_id==exp.id).group_by(TranscriptToObservation.transcript_id, Observation.tge_id).all()
  print("Total transcript")
  print(trns)
  #print()

  # organisms  = [item for sublist in organisms for item in sublist]
  # sampleNum = Sample.query.filter_by(exp_id=experiment).distinct().count()

  obsNum = Observation.query.join(Sample).join(Experiment).\
              filter_by(id=exp.id).distinct().count()

  tgeNum = TGE.query.join(Observation).join(Sample).join(Experiment).\
              filter_by(id=exp.id).distinct(Observation.tge_id).count()
  tgeObs = Observation.query.join(Sample).join(Experiment).\
              filter_by(id=exp.id).distinct(Observation.tge_class).all()
  tgeClasses = list(set([t.tge_class for t in tgeObs]))
  trnNum = Transcript.query.with_entities(distinct(Transcript.dna_seq)).\
              join(TranscriptToObservation).join(Observation).join(Sample).\
              filter_by(exp_id=exp.id).count()

  peptAll  = Observation.query.with_entities(func.sum(Observation.peptide_num).label("pepNum")).\
              join(Sample).join(Experiment).\
              filter_by(id=exp.id).one()

  # unique peptide count
  # peptUniq = TgeToPeptide.query.with_entities(distinct(TgeToPeptide.peptide_id)).\
  #             join(Observation).join(Sample).\
  #             filter(Sample.exp_id==exp.id).count()

  # sum of unique peptide counts
  peptUniq = TgeToPeptide.query.with_entities(func.count(distinct(TgeToPeptide.peptide_id))).\
              join(Observation).join(Sample).group_by(Observation.sample_id).\
              filter(Sample.exp_id==exp.id).all()

  peptUniq = [item for sublist in peptUniq for item in sublist]

  summary = {'accession': experiment,'title': exp.title, 'description': exp.description, 'publication':exp.publication, 'user': user.fullname, 'sampleNum': len(samples), 
            'tgeNum' : separators(tgeNum), 'obsNum' : separators(obsNum), 'trnNum' : separators(trnNum), 
            'peptAll' : separators(peptAll), 'peptUniq' : separators(sum(peptUniq)) };
   
  sampleList = []

  for sample in samples:
    tgePerSample = Observation.query.filter(Observation.sample_id==sample.id).distinct(Observation.tge_id).count()
    pepPerSample = TgeToPeptide.query.with_entities(distinct(TgeToPeptide.peptide_id)).\
                      join(Observation).join(Sample).filter(Observation.sample_id==sample.id).count()

    sampleList.append({'id':sample.id, 'name': sample.name, 'tgeNum': separators(tgePerSample), 'pepNum': separators(pepPerSample)})

  return render_template('results/experiment.html', summary = summary, sampleList = sampleList, tges = tges, tgeClasses = tgeClasses, trns = trns)


@results.route('/sample')
def sample():
  if 'experiment' in request.args:
    experiment = request.args['experiment']
    print("experiment:"+experiment)
    if "EXP" in experiment:
      exp  = Experiment.query.filter_by(accession=experiment).first_or_404()
    else:
      exp  = Experiment.query.filter_by(id=experiment).first_or_404()
    if 'sample' in request.args:
      sampleName  = request.args['sample']
      print("Sample"+sampleName)
      sample  = Sample.query.filter_by(name=sampleName).filter_by(exp_id=exp.id).first_or_404()
    elif 'accession' in request.args:
      sampleAccession = request.args['accession']
      print("Accession"+sampleAccession)
      sample  = Sample.query.filter_by(accession=sampleAccession).filter_by(exp_id=exp.id).first_or_404()
  else:
    if 'sample' in request.args:
      sampleName  = request.args['sample']
      print("Sample"+sampleName)
      sample  = Sample.query.filter_by(name=sampleName).first_or_404()
    elif 'accession' in request.args:
      sampleAccession = request.args['accession']
      print("Accession"+sampleAccession)
      sample  = Sample.query.filter_by(accession=sampleAccession).first_or_404()
    exp = Experiment.query.filter_by(id=sample.exp_id).first_or_404()
  user = User.query.with_entities(User.fullname).filter_by(id=exp.user_id).one()

  tges = TGE.query.join(Observation).filter(TGE.id==Observation.tge_id).filter(Observation.sample_id==sample.id).distinct(TGE.id).all()
  tgeClasses = Observation.query.with_entities(Observation.tge_class).\
                  filter(Observation.sample_id==sample.id).group_by(Observation.tge_class).all()
  tgeClasses = [item for sublist in tgeClasses for item in sublist]
  
  transcripts = db.session.query(Transcript.dna_seq, Transcript.id, Observation.tge_id, Observation.name, Observation.id,Observation.organism, Observation.gene_name, TGE.accession).filter(TGE.id==Observation.tge_id).filter(Observation.sample_id==sample.id).filter(TranscriptToObservation.obs_id==Observation.id).filter(Transcript.id==TranscriptToObservation.transcript_id).distinct(Transcript.id) #Transcript.query.join(Observation).filter(Observation.sample_id==sample.id).distinct(Transcript.id)
  results  = []
  #print "OBS Size "+str(tgeObs.count())
  for t in transcripts:
    #print t
    trnLength = len(t[0])
    chrom = 0;
    results.append({'id': t[1], 'tge_id': t[7], 'obsid' : t[4] ,'observation': t[3], 'sampleName': sample.name, 'expAccession': exp.accession, 
                    'expID': exp.id, 'length': trnLength, 'organism': t[5], 
                    'chr': chrom, 'gene': t[6] })
  #   print "result size "+str(len(results))
  print "result size "+str(len(results))
  obsNum = Observation.query.filter_by(sample_id=sample.id).distinct().count()

  tgeNum = TGE.query.join(Observation).filter(Observation.sample_id==sample.id).distinct(Observation.tge_id).count()

  trnNum = Transcript.query.join(TranscriptToObservation).join(Observation).filter(Observation.sample_id==sample.id).distinct(Observation.id).count()

  peptAll  = Observation.query.with_entities(func.sum(Observation.peptide_num).label("pepNum")).\
              join(Sample).filter_by(id=sample.id).one()

  # sum of unique peptide counts
  peptUniq = TgeToPeptide.query.with_entities(func.count(distinct(TgeToPeptide.peptide_id))).\
              join(Observation).group_by(Observation.sample_id).\
              filter(Observation.sample_id==sample.id).all()

  peptUniq = [item for sublist in peptUniq for item in sublist]

  summary = {'accession': sample.accession,'name': sample.name, 'user': user.fullname, 
            'tgeNum' : separators(tgeNum), 'obsNum' : separators(obsNum), 'trnNum' : separators(trnNum), 
            'peptAll' : separators(peptAll), 'peptUniq' : separators(sum(peptUniq)), 'description': sample.description };
  varQuery = "SELECT v.ref_id as ref_id, v.pos as pos, v.ref_aa as ref_aa, v.alt_aa as alt_aa, v.var_type as var_type, count(distinct(vo.obs_id)) as obs_count, string_agg(distinct(vo.qpos)::char(10),\',\') as qpos, max(vo.peptide_num) as pep_evd, string_agg(distinct(vo.unique_peptides),\',\') AS unq_peptides from variation as v JOIN variation_observation vo ON v.id=vo.var_id JOIN observation o ON vo.obs_id=o.id where o.sample_id="+str(sample.id)+" group by v.ref_id, v.pos, v.ref_aa, v.alt_aa, v.var_type;"
  variations = db.engine.execute(varQuery).fetchall()
  if len(variations)==0:
    variations = None
  #print(len(tges))
  print(variations)
  return render_template('results/sample.html', summary = summary, tges = tges, tgeClasses = tgeClasses, transcripts = results, variations = variations )


@results.route('/protein')
def protein():
  genoverse = summary = {}
  uniprot   = request.args['uniprot']
  organism  = Observation.query.with_entities(distinct(Observation.organism)).filter_by(uniprot_id=uniprot).first_or_404()

  protein = Observation.query.with_entities(Observation.organism, Observation.protein_name, Observation.protein_descr, Observation.gene_name).\
                filter_by(uniprot_id=uniprot).group_by(Observation.organism, Observation.protein_name, Observation.protein_descr, Observation.gene_name).one()

  summary = {'protein_name': protein.protein_name, 'gene_name': protein.gene_name, 'protein_descr': protein.protein_descr, 'organism': protein.organism }

  tges = TGE.query.with_entities(TGE.accession, TGE.tge_class, func.count(Observation.id).label('obsCount')).\
              join(Observation).filter_by(uniprot_id=uniprot).\
              group_by(TGE.accession, TGE.tge_class).all()

  obj  = Experiment.query.with_entities(Experiment.title, Experiment.accession, Sample.name, Sample.id).\
              join(Sample).join(Observation).filter_by(uniprot_id=uniprot).\
              group_by(Experiment.title, Experiment.accession, Sample.name, Sample.id).all()

  if (organism[0] == "Homo sapiens" or organism[0] == "Mus musculus"):
    for ob in obj: 
      file = os.path.dirname(__file__)+"/../static/data/"+ob.accession+"/"+ob.name+".assemblies.fasta.transdecoder.genome.gff3_identified.gff3"
      df   = pd.read_table(file, sep="\t", index_col = None) 

      obs  = Observation.query.with_entities(Observation.long_description).\
              filter_by(uniprot_id=uniprot, sample_id=ob.id).first()

      arr  = obs.long_description.split(" ")
      mRNA = arr[0]
      gene = arr[1]
    
      row   = df[df['attributes'].str.contains(re.escape("ID="+gene+";")+"|"+re.escape(mRNA)+"[;.]")]
      
      if (len(row['seqid'].iloc[0]) <= 5):
        chrom = re.search(r'(\d|[X]|[Y])+', row.iloc[0,0]).group()
        start = row.iloc[0,3]
        end   = row.iloc[0,4]
      else:
        chrom = row.iloc[0,0]
        start = row.iloc[0,3]
        end   = row.iloc[0,4]

      genoverse  = { 'uniprot': uniprot, 'chr': chrom, 'start': start, 'end': end }
      break
        
      #chrom = re.search(r'\d+', row.iloc[0,0]).group()
      
  return render_template('results/protein.html', tges = tges, genoverse = genoverse, uniprot = uniprot, summary=summary, organism = organism[0])


@results.route('/gene')
def gene():
  genoverse = summary = {}
  gene      = request.args['gene']
  
  protList  = Observation.query.with_entities(Observation.organism, Observation.uniprot_id, Observation.protein_name, Observation.protein_descr).\
                  filter(Observation.gene_name.ilike(gene)).\
                  group_by(Observation.organism, Observation.uniprot_id, Observation.protein_name, Observation.protein_descr).all()

  if (len(protList) == 1):
    return redirect(url_for('results.protein', uniprot = protList[0].uniprot_id))
  elif (len(protList) > 1): 
    return render_template('results/gene.html', gene = gene, protList = protList)
  else:
    return render_template('error/404.html')
  return render_template('error/404.html')


@results.route('/aminoseq')
def aminoseq():  
  tgeList = []
  
  # Get the two arguments searchData and searchType (exact or partial)
  searchData = request.args['searchData']
  searchType = request.args['searchType']

  if searchType == 'exact':
    # We expect only one match for one particular aminoseq
    tge = TGE.query.filter(TGE.amino_seq == searchData).first_or_404()
    return redirect(url_for('results.tge', accession = tge.accession))

  else:
    tges = TGE.query.filter(TGE.amino_seq.like("%"+searchData+"%")).all()

    if (tges):

      for tge in tges: 
        # For each TGE get the obs num, organisms, uniprotID and tgeClass
        obsNum     = Observation.query.filter_by(tge_id=tge.id).count()
        organisms  = Observation.query.with_entities(Observation.organism).filter_by(tge_id=tge.id).distinct(Observation.organism).all()
        tgeClasses = tge.tge_class
        uniprotIDs = tge.uniprot_id
        
        # Flatten out the list of lists to lists (to use in the for loops)
        organisms  = [item for sublist in organisms for item in sublist]
        
        sampleNum = Sample.query.with_entities(Sample.name).\
                        join(Observation, Observation.sample_id == Sample.id).\
                        filter_by(tge_id=tge.id).\
                        distinct(Sample.name).count()

        tgeList.append({ 'accession': tge.accession, 'length': len(tge.amino_seq), 'obsNum': obsNum, 
          'organisms': organisms, 'tgeClasses': tgeClasses,  'uniprotIDs': uniprotIDs, 'sampleNum': sampleNum })
      return render_template('search/results.html', tgeList = tgeList)
    else: 
      return render_template('error/404.html')


@results.route('/peptide')
def peptide():
  tgeList = []
  # Get the two arguments searchData and searchType (exact or partial)
  searchData = request.args['searchData']
  searchType = request.args['searchType']

  if searchType == 'exact':
    # We expect only one match for one particular aminoseq
    peptide = Peptide.query.filter(Peptide.aa_seq == searchData).first_or_404()
    tges = TGE.query.with_entities(TGE.accession, TGE.amino_seq).\
            join(Observation).join(TgeToPeptide).filter_by(peptide_id = peptide.id).all()

    for tge in tges:  
      tgeList.append({ 'accession': tge.accession, 'amino_seq': Markup((tge.amino_seq).replace(searchData, "<span style='color:red; font-weight: bold;'>"+searchData+"</span>")) }) 

    return render_template('results/peptide.html', peptide = peptide, tges = tgeList)

  else:
    pep = Peptide.query.filter(Peptide.aa_seq.like("%"+searchData+"%")).all()

  return render_template('results/peptide.html')

@results.route('/transcript')
def transcript():
  trns = Transcript.query.with_entities(Transcript.dna_seq, Observation.name).join(TranscriptToObservation).join(Observation).filter(Transcript.id==TranscriptToObservation.transcript_id).filter(TranscriptToObservation.obs_id == request.args['obsID']).first_or_404()

  return render_template('results/transcript.html', trns = trns, tge = request.args['accession'])

def separators( inputText ):
  locale.setlocale(locale.LC_ALL, 'en_US')
  newText = locale.format("%d", inputText, grouping=True)
  return newText

