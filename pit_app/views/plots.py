import re
import simplejson as json

from flask import Blueprint
from sqlalchemy.sql import func, distinct
from pit_app.models import *
from pit_app import db


plots = Blueprint('plots',  __name__)

@plots.route('/tge/<accession>.json')
def tgeJSON(accession):
  tgeList = []
  
  tge  = TGE.query.filter_by(accession=accession).one()
  obs  = Observation.query.with_entities(Observation.organism, func.count(Observation.organism).label('obsCount')).\
              join(TGE, TGE.id == Observation.tge_id).\
              filter_by(accession=accession).\
              group_by(Observation.organism)

  for ob in obs.all(): 
    pepList =[]

    peptides = Peptide.query.with_entities(Peptide.aa_seq, func.count(Peptide.aa_seq).label('pepCount')).\
                  join(TgeToPeptide, Peptide.id == TgeToPeptide.peptide_id).\
                  join(Observation,  Observation.id == TgeToPeptide.obs_id).\
                  filter_by(organism=ob.organism, tge_id=tge.id).\
                  group_by(Peptide.aa_seq).all()

    for pep in peptides:
      sampleList = []

      samples = Sample.query.with_entities(Sample.name, func.count(Sample.name).label('smplCount')).\
                join(Observation, Observation.sample_id==Sample.id).\
                join(TgeToPeptide, Observation.id == TgeToPeptide.obs_id).\
                join(Peptide, Peptide.id == TgeToPeptide.peptide_id).\
                filter_by(aa_seq = pep.aa_seq).\
                group_by(Sample.name).all()

      for smpl in samples:
        sampleList.append({ "name": smpl.name, "size": smpl.smplCount})

      # expList = []

      # exps = Experiment.query.with_entities(Experiment.title, func.count(Experiment.title).label('expCount')).\
      #           join(Sample, Experiment.id==Sample.exp_id ).\
      #           filter_by(name = smpl.name).\
      #           group_by(Experiment.title).all()

      #for exp in exps:

      pepList.append({ "name": pep.aa_seq, "size": pep.pepCount, "children": sampleList}) 

       # expList.append({ "name": exp.title, "size": exp.expCount})

      #  

    tgeList.append({ "name": ob.organism, "size": ob.obsCount, "children": pepList})

  test = {
    "name": "tgeBreakdown",
    "children": tgeList
  }

  data = json.dumps(test)

  return data


@plots.route('/organism/<organism>.json')
def orgJSON(organism):
  orgList = []

  obs   = Observation.query.with_entities(Observation.tge_class, func.count(Observation.tge_class).label('obsCount')).\
            filter_by(organism=organism).\
            group_by(Observation.tge_class).\
            order_by(Observation.tge_class).all()

  for ob in obs: 

    sampleList = []
    samples = Sample.query.with_entities(Sample.name, func.count(Sample.name).label('smplCount')).\
                join(Observation, Observation.sample_id==Sample.id).\
                filter_by(organism=organism, tge_class=ob.tge_class).\
                group_by(Sample.name).all()

    for smpl in samples:
      expList = []

      exps = Experiment.query.with_entities(Experiment.title, func.count(Experiment.title).label('expCount')).\
                join(Sample, Experiment.id==Sample.exp_id ).\
                filter_by(name = smpl.name).\
                group_by(Experiment.title).all()

      for exp in exps:
        pepList =[]

        peptides = TgeToPeptide.query.with_entities(TgeToPeptide.peptide_id, func.count(TgeToPeptide.peptide_id).label('pepCount')).\
                      join(Observation, Observation.id == TgeToPeptide.obs_id).\
                      filter_by(organism=organism, tge_class=ob.tge_class).\
                      group_by(TgeToPeptide.peptide_id).all()

        for pep in peptides:
          pepList.append({ "name": pep.peptide_id, "size": pep.pepCount}) 

        expList.append({ "name": exp.title, "size": exp.expCount, "children": pepList })

      sampleList.append({ "name": smpl.name, "size": smpl.smplCount, "children": expList })  


    orgList.append({ "name": ob.tge_class, "size": ob.obsCount, "children": sampleList})

  test = {
    "name": "tgeBreakdown",
    "children": orgList
  }

  data = json.dumps(test)

  return data


@plots.route('/experiment/<experiment>.json')
def expJSON(experiment):
  sampleList = []

  samples   = Sample.query.filter_by(exp_id=experiment).all()

  for sample in samples:
    tgePerSample = Observation.query.filter(Observation.sample_id==sample.id).\
                                distinct(Observation.tge_id).count()
    sampleList.append({'id':sample.id, 'name': sample.name, 'tgeNum':tgePerSample })

  data = json.dumps(sampleList)

  return data

