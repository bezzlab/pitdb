import re
import simplejson as json

from flask import Blueprint
from sqlalchemy.sql import func, distinct
from pit_app.models import *
from pit_app import db


plots = Blueprint('plots',  __name__)

@plots.route('/tge/<accession>.json')
def tgeJSON(accession):
  obsList = []

  # Get the TGE id for this particular accession 
  tge  = TGE.query.with_entities(TGE.id).filter_by(accession=accession).one()
  
  # Get all the Observations for this accession ID
  obs  = Observation.query.with_entities(Observation.organism, func.count(Observation.organism).label('obsCount')).\
              filter_by(tge_id=tge.id).\
              group_by(Observation.organism)

  # We are looping through the distinct organisms
  for ob in obs.all(): 
    pepNumList = []


    pepNum = Observation.query.with_entities(func.sum(Observation.peptide_num).label('pepSum')).\
                    filter_by(organism=ob.organism, tge_id=tge.id).all() 
    
    for num in pepNum:
      pepList = []

      # Find the number of peptides for this TGE observation and category of organism
      peptides = Peptide.query.with_entities(Peptide.aa_seq, func.count(Peptide.aa_seq).label('pepCount')).\
                    join(TgeToPeptide, Peptide.id == TgeToPeptide.peptide_id).\
                    join(Observation,  Observation.id == TgeToPeptide.obs_id).\
                    filter_by(organism=ob.organism, tge_id=tge.id).\
                    group_by(Peptide.aa_seq).distinct(Peptide.aa_seq).all() 
      
      for pep in peptides:
        sampleList = []

        samples = Sample.query.with_entities(Sample.name, func.count(Sample.name).label('smplCount')).\
                    join(Observation, Observation.sample_id==Sample.id).\
                    join(TgeToPeptide, Observation.id == TgeToPeptide.obs_id).\
                    join(Peptide, Peptide.id == TgeToPeptide.peptide_id).\
                    filter(Observation.organism == ob.organism, Observation.tge_id == tge.id, Peptide.aa_seq == pep.aa_seq).\
                    group_by(Sample.name).all()

        for smpl in samples:
          # expList = []

          # exps = Experiment.query.with_entities(Experiment.title, func.count(Experiment.title).label('expCount')).\
          #           join(Sample, Experiment.id == Sample.exp_id).\
          #           join(Observation, Observation.sample_id==Sample.id).\
          #           join(TgeToPeptide, Observation.id == TgeToPeptide.obs_id).\
          #           join(Peptide, Peptide.id == TgeToPeptide.peptide_id).\
          #           filter(Observation.organism == ob.organism, Observation.tge_id == tge.id, Peptide.aa_seq == pep.aa_seq, Sample.name == smpl.name).\
          #           group_by(Experiment.title).all()

          # for exp in exps:
          #   expList.append({ "name": "Expertiments "+exp.title, "size": exp.expCount, "type":"experiments"})

          sampleList.append({ "name": "Samples "+smpl.name, "size": smpl.smplCount, "type":"samples" })

        pepList.append({ "name": 'Peptides "'+pep.aa_seq+"'", "size": pep.pepCount, "type":"peptides", "children": sampleList }) 

      pepNumList.append({ "name": "Identified peptides in "+ob.organism, "size": num.pepSum, "type":"PeptCount", "children": pepList }) 

    obsList.append({ "name": ob.organism, "size": ob.obsCount, "type":"organisms", "children": pepNumList })

  test = {
    "name": "tgeBreakdown",
    "children": obsList
  }

  data = json.dumps(test)

  return data


@plots.route('/organism/<organism>.json')
def orgJSON(organism):
  orgList = []

  # Find the TGE observations with the given organism
  obs   = Observation.query.with_entities(Observation.tge_class, func.count(Observation.tge_class).label('obsCount')).\
            filter_by(organism=organism).\
            group_by(Observation.tge_class).all()

  # Loop through each available class
  for ob in obs: 
    pepList = []

    # Find the number of peptides for this TGE observation and category of organism
    pepNum = Observation.query.with_entities(Observation.tge_class, func.sum(Observation.peptide_num).label('pepSum')).\
                  filter_by(organism=organism, tge_class = ob.tge_class).\
                  group_by(Observation.tge_class).all() 
    
    for num in pepNum:
      sampleList = []

      samples = Sample.query.with_entities(Sample.name, func.count(Sample.name).label('smplCount')).\
                  join(Observation, Observation.sample_id==Sample.id).\
                  filter_by(organism=organism, tge_class=ob.tge_class).\
                  group_by(Sample.name).all()

      for smpl in samples:
    #   expList = []

    #   exps = Experiment.query.with_entities(Experiment.title, func.count(Experiment.title).label('expCount')).\
    #             join(Sample, Experiment.id==Sample.exp_id ).\
    #             join(Observation, Observation.sample_id==Sample.id).\
    #             filter(Observation.organism == organism, Observation.tge_class == ob.tge_class, Sample.name == smpl.name).\
    #             group_by(Experiment.title).all()

    #   for exp in exps:
    #     expList.append({ "name": exp.title, "size": exp.expCount, "type":"experiment" })

        sampleList.append({ "name": "observations belong to sample " + smpl.name, "size": smpl.smplCount, "type":"sample" })  
      pepList.append({ "name": 'Indentified peptides for "'+ob.tge_class+'"', "size": num.pepSum, "type":"peptides", "children": sampleList }) 
    orgList.append({ "name": 'observations with type "'+ob.tge_class+'"', "size": ob.obsCount, "children": pepList, "type":"TGE type" })

  test = {
    "name": "tgeBreakdown",
    "children": orgList
  }

  data = json.dumps(test)

  return data


@plots.route('/aminoseq/<amino_seq>.json')
def aminoseqJSON(amino_seq):
  obsList = []
  # Get the list of TGEs for the given amino acid sequence (partial or exact match)
  tges = TGE.query.with_entities(TGE.id).filter(TGE.amino_seq.like("%"+amino_seq+"%")).all()

  obs  = Observation.query.with_entities(Observation.organism, func.count(Observation.organism).label('obsCount')).\
              filter(Observation.tge_id.in_(tges)).\
              group_by(Observation.organism)

  for ob in obs: 
    print ob.organism
    obsList.append({ "name": ob.organism, "size": ob.obsCount })

  test = {
    "name": "tgeBreakdown",
    "children": obsList
  }

  data = json.dumps(test)

  return data



@plots.route('/experiment/<experiment>.json')
def expJSON(experiment):
  tgeList = []

  samples = Sample.query.filter_by(exp_id=experiment).all()

  tges  = Observation.query.with_entities(Observation.sample_id, func.count(Observation.sample_id).label('tgeCount')).\
              join(Sample, Observation.sample_id == Sample.id ).\
              filter(Sample.exp_id == experiment).\
              group_by(Observation.sample_id)

  for tge in tges:
    tgeList.append({ "name": tge.sample_id, "size": tge.tgeCount })

  test = {
    "name": "tgeBreakdown",
    "children": tgeList
  }

  data = json.dumps(test)

  return data

