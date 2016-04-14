import re
import json
# import simplejson as json
import numpy as np
import locale

from pit_app import db
from pit_app.models import *
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask.ext.login import login_required, current_user
from sqlalchemy.sql import func, distinct


results = Blueprint('results',  __name__)


@results.route('/tge/<accession>')
def tge(accession):
  tge        = TGE.query.filter_by(accession=accession).one()
  tgeObs     = Observation.query.filter_by(tge_id=tge.id)
  obsCount   = tgeObs.count()
  #organisms  = Observation.query.with_entities(Observation.organism).filter_by(tge_id=tge.id).distinct(Observation.organism)
  tgeClass   = tgeObs.distinct(Observation.tge_class).all()
  avgPeptNum = Observation.query.with_entities(func.avg(Observation.peptide_num).label('average')).one()

  results  = []
  organism = set()

  for obs in tgeObs: 
  	sample = Sample.query.filter_by(id=obs.sample_id).first()
  	exp    = Experiment.query.filter_by(id=sample.exp_id).first()
  	#transc = Transcript.query.filter_by(obs_id=obs.id).first()
  	tgePep = TgeToPeptide.query.filter_by(obs_id=obs.id).all()

  	tgeType    = re.search("(?<=type:).*?(?=\s)", obs.long_description).group(0)
  	tgeLength  = re.search("(?<=len:).*?(?=\s)",  obs.long_description).group(0)
  	tgeStrand  = re.search("(?<=\().*?(?=\))",    obs.long_description).group(0)

  	peptides = set()
  	organism.add(obs.organism)
  	
  	for peptide in tgePep: 
  		pept = Peptide.query.filter_by(id=peptide.peptide_id).first()
  		peptides.add(pept.aa_seq)

  	results.append({'id': obs.id, 'observation': obs.name, 'sample': sample.name, 'experiment': exp.title, 
      'type': tgeType, 'length': tgeLength, 'strand':tgeStrand, 'organism': obs.organism, 
  		'peptide_num': obs.peptide_num, 'peptides': list(peptides)})


  summary = { 'tge' : tge, 'tgeObs' : obs, 'organisms' : list(organism), 'avgPeptNum' : avgPeptNum, 'tgeClass' : list(tgeClass), 'obsCount' : obsCount};

  return render_template('results/tge.html', summary = summary, results=results, jsonDump = {'homoSapiens' : 3, 'monkey':5 })


@results.route('/tge/<accession>/tge.json')
def tgeJSON(accession):
  #data = json.dumps([{'organism': 'HomoSapiens' , 'num': 3}, {'organism': 'Monkey' , 'num': 10}])

  tgeList = []
  tge     = TGE.query.filter_by(accession=accession).one()
  obs     = Observation.query.\
                        with_entities(Observation.organism, func.count(Observation.organism)).\
                        group_by(Observation.organism).\
                        filter_by(tge_id=tge.id).all()
  
  for ob in obs: 
    tgeList.append({'organism': ob[0] , 'count': ob[1] })

  data = json.dumps(tgeList)

  print data
  return data

@results.route('/tge/<accession>/experiment.json')
def tgeJSON2(accession):
  #data = json.dumps([{'organism': 'HomoSapiens' , 'num': 3}, {'organism': 'Monkey' , 'num': 10}])

  expList = []
  tge     = TGE.query.filter_by(accession=accession).one()
  tgeObs  = Observation.query.filter_by(tge_id=tge.id)
  
  for ob in tgeObs: 
    sample = Sample.query.filter_by(id=ob.sample_id).first()
    exp    = Experiment.query.with_entities(Experiment.title, func.count(Experiment.title)).\
                        group_by(Experiment.title).\
                        filter_by(id=sample.exp_id).all()

    expList.append({'experiment': exp[0] , 'count': exp[1] })

  data = json.dumps(expList)

  print data
  return data

@results.route('/organism/<organism>')
def organism(organism):
  tgeList = []

  obs       = Observation.query.filter_by(organism=organism)
  tgeClass  = obs.distinct(Observation.tge_class).first()
  tges      = TGE.query.join(Observation).filter_by(organism=organism).distinct(Observation.tge_id)
  tgeNum    = separators(obs.distinct(Observation.tge_id).count())
  sampleNum = separators(obs.join(Sample).distinct(Sample.id).count())
  expNum    = separators(obs.join(Sample).join(Experiment).distinct(Experiment.id).count())
  uniprotID = obs.distinct(Observation.uniprot_id).all()

  trnNum    = separators(Transcript.query.join(Observation, Transcript.obs_id == Observation.id).\
                    filter(Observation.organism==organism).distinct().count())
  pepNum    = separators(Observation.query.with_entities(func.sum(Observation.peptide_num)).\
                    filter_by(organism=organism).scalar())

  summary = {'organism': organism,'tgeNum': tgeNum, 'sampleNum': sampleNum, 'expNum': expNum, 'trnNum': trnNum, 'pepNum' : pepNum};
  
  for tge in tges: 
    tgeList.append({'accession': tge.accession, 'class': tge.tge_class, 'uniprotID': tge.uniprot_id})

  return render_template('results/organism.html', summary = summary, tgeList= tgeList)

@results.route('/organism/<organism>/organism.json')
def orgJSON(organism):
  orgList = []

  obs = Observation.query.with_entities(Observation.tge_class, func.count(Observation.tge_class)).\
                          group_by(Observation.tge_class).\
                          filter_by(organism=organism).all()
  
  for ob in obs: 
    orgList.append({'tgeClass': ob[0], 'count': ob[1]})

  data = json.dumps(orgList)

  print data
  return data


@results.route('/experiment/<experiment>')
def experiment(experiment):
  exp  = Experiment.query.filter_by(id=experiment).first_or_404()
  user = User.query.with_entities(User.fullname).filter_by(id=exp.user_id).one()

  samples   = Sample.query.filter_by(exp_id=experiment).all()
  sampleNum = Sample.query.filter_by(exp_id=experiment).distinct().count()

  obsNum = separators(Observation.query.join(Sample, Observation.sample_id==Sample.id).\
        join(Experiment, Experiment.id==Sample.exp_id ).\
        filter(Experiment.id==experiment).distinct().count())

  tgeNum = separators(TGE.query.join(Observation, TGE.id == Observation.tge_id).\
        join(Sample, Observation.sample_id==Sample.id).\
        join(Experiment, Experiment.id==Sample.exp_id ).\
        filter(Experiment.id==experiment).distinct(Observation.tge_id).count()) #distinct() -- removed distinct for now

  trnNum = separators(Transcript.query.join(Observation, Transcript.obs_id == Observation.id).\
        join(Sample, Observation.sample_id==Sample.id).\
        join(Experiment, Experiment.id==Sample.exp_id ).\
        filter(Experiment.id==experiment).distinct().count())

  pepNum = separators(Observation.query.with_entities(func.sum(Observation.peptide_num)).\
        join(Sample, Observation.sample_id==Sample.id).\
        join(Experiment, Experiment.id==Sample.exp_id ).\
        filter(Experiment.id==experiment).scalar())

  summary = {'id': experiment,'title': exp.title, 'user': user.fullname, 'sampleNum': sampleNum, 'tgeNum' : tgeNum, 'obsNum' : obsNum, 'trnNum' : trnNum, 'pepNum' : pepNum};
   
  sampleList = []

  for sample in samples:
    tgePerSample = Observation.query.filter(Observation.sample_id==sample.id).distinct(Observation.tge_id).count()
    sampleList.append({'id':sample.id, 'name': sample.name, 'tgeNum':tgePerSample })

  return render_template('results/experiment.html', summary = summary, sampleList = sampleList)


@results.route('/experiment/<experiment>/experiment.json')
def expJSON(experiment):
  sampleList = []

  samples   = Sample.query.filter_by(exp_id=experiment).all()

  for sample in samples:
    tgePerSample = Observation.query.filter(Observation.sample_id==sample.id).\
                                distinct(Observation.tge_id).count()
    sampleList.append({'id':sample.id, 'name': sample.name, 'tgeNum':tgePerSample })

  data = json.dumps(sampleList)

  return data

@results.route('/protein/<uniprot>')
def protein(uniprot):
  obs  = Observation.query.filter_by(uniprot_id=uniprot).all()
  
  tges = TGE.query.join(Observation).filter_by(uniprot_id=uniprot).\
              distinct(Observation.tge_id)

  tgeList = []

  # for tge in tges:
  #   tgePerSample = Observation.query.filter(Observation.tge_id==tge.id).all()
  
  #   tgeList.append({'accession':sample.id, 'name': sample.name, 'tgeNum':tgePerSample })

  return render_template('results/protein.html', tges = tges, uniprot = uniprot)

@results.route('/peptide/<peptide>')
def peptide(peptide):
  return render_template('results/peptide.html')

@results.route('/transcript/<transcript>')
def transcript(transcript):
  return render_template('results/transcript.html')

def separators( inputText ):
  locale.setlocale(locale.LC_ALL, 'en_US')
  newText = locale.format("%d", inputText, grouping=True)
  return newText
