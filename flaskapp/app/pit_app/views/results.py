import re
import json
import numpy as np

from pit_app import db
from pit_app.models import *
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask.ext.login import login_required, current_user
from sqlalchemy.sql import func, distinct


results = Blueprint('results',  __name__)


@results.route('/tge/<tge_id>')
def tge(tge_id):
  tge    = TGE.query.filter_by(id=tge_id).first_or_404()
  print(tge)
  tgeObs = TGEobservation.query.filter_by(tge_id=tge_id).all()
  avgPeptNum = TGEobservation.query.with_entities(func.avg(TGEobservation.peptide_num).label('average')).first()

  results  = []
  organism = set()

  for obs in tgeObs: 
  	sample = Sample.query.filter_by(id=obs.sample_id).first()
  	exp    = Experiment.query.filter_by(id=sample.exp_id).first()
  	#transc = Transcript.query.filter_by(obs_id=obs.id).first()
  	tgePep = TgeToPeptide.query.filter_by(obs_id=obs.id).all()

  	tgeType    = re.search("(?<=type:).*?(?=\s)", obs.description).group(0)
  	tgeLength  = re.search("(?<=len:).*?(?=\s)",  obs.description).group(0)
  	tgeStrand  = re.search("(?<=\().*?(?=\))",    obs.description).group(0)

  	peptides = set()
  	organism.add(obs.organism)
  	
  	for peptide in tgePep: 
  		pept = Peptide.query.filter_by(id=peptide.peptide_id).first()
  		peptides.add(pept.aa_seq)

  	results.append({'observation': obs.name, 'sample': sample.name, 'experiment': exp.name, 
      'type': tgeType, 'length': tgeLength, 'strand':tgeStrand, 'organism': obs.organism, 
  		'peptide_num': obs.peptide_num, 'peptides': ', '.join(peptides)})

      #'dna_seq':transc.dna_seq, 

  return render_template('results/tge.html', tge = tge, tgeObs = obs, organisms= list(organism), 
  	avgPeptNum = avgPeptNum, results=results) 


@results.route('/organism/<organism>')
def organism(organism):

  # results = []
  # orgs = exps = set()
  #org  = request.args['org']
  # num = session.query(func.count(TGE.id))
  obs       = TGEobservation.query.filter_by(organism=organism)
  obsNum    = obs.count()
  tgeNum    = obs.distinct(TGEobservation.tge_id).count()
  sampleNum = obs.join(Sample).distinct(Sample.id).count()
  expNum    = obs.join(Sample).join(Experiment).distinct(Experiment.id).count()

  trnNum = Transcript.query.join(TGEobservation, Transcript.obs_id == TGEobservation.id).\
        filter(TGEobservation.organism==organism).distinct().count()

  #tgeObs = TGEobservation.query.filter_by(organism=user_url_slug).all()

  sumPepNum = TGEobservation.query.with_entities(func.sum(TGEobservation.peptide_num)).filter_by(organism=organism).scalar()


  return render_template('results/organism.html', organism = organism, obsNum = obsNum, 
    tgeNum = tgeNum, sampleNum = sampleNum, expNum = expNum, trnNum = trnNum, sumPepNum = sumPepNum)


@results.route('/experiment/<experiment>')
def experiment(experiment):
  exps = set()

  exp       = Experiment.query.filter_by(id=experiment).one()
  user      = User.query.filter_by(id=exp.user_id).one()
  samples   = Sample.query.filter_by(exp_id=experiment).all()
  sampleNum = Sample.query.filter_by(exp_id=experiment).distinct().count()
  tgeObsNum = TGEobservation.query.join(Sample, TGEobservation.sample_id==Sample.id).\
        join(Experiment, Experiment.id==Sample.exp_id ).\
        filter(Experiment.id==experiment).distinct().count()

  tgeNum = TGE.query.join(TGEobservation, TGE.id == TGEobservation.tge_id).\
        join(Sample, TGEobservation.sample_id==Sample.id).\
        join(Experiment, Experiment.id==Sample.exp_id ).\
        filter(Experiment.id==experiment).distinct().count()

  trnNum = Transcript.query.join(TGEobservation, Transcript.obs_id == TGEobservation.id).\
        join(Sample, TGEobservation.sample_id==Sample.id).\
        join(Experiment, Experiment.id==Sample.exp_id ).\
        filter(Experiment.id==experiment).distinct().count()

  #tgeNum    = exp.join(Sample).join(TGEobservation).distinct(TGEobservation.tge_id).count()
  
  return render_template('results/experiment.html', exp = exp, user=user, sampleNum = sampleNum, 
    tgeNum = tgeNum, tgeObsNum = tgeObsNum, trnNum = trnNum, samples = samples)



@results.route('/protein/<protein>')
def protein(protein):
  return render_template('results/protein.html')

@results.route('/peptide/<peptide>')
def peptide(peptide):
  return render_template('results/peptide.html')

@results.route('/transcript/<transcript>')
def transcript(transcript):
  return render_template('results/transcript.html')
