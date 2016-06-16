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
          sampleList.append({ "name": "Samples "+smpl.name, "size": smpl.smplCount, "type":"samples" })

        pepList.append({ "name": 'Peptides "'+pep.aa_seq+'"', "size": pep.pepCount, "type":"peptides", "children": sampleList }) 

      pepNumList.append({ "name": "Identified peptides in "+ob.organism, "size": num.pepSum, "type":"peptide count", "children": pepList }) 

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
  obs   = Observation.query.with_entities(Observation.tge_class, func.count(distinct(Observation.tge_id)).label('obsCount')).\
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

        sampleList.append({ "name": "TGEs belong to sample " + smpl.name, "size": smpl.smplCount, "type":"samples" })  
      pepList.append({ "name": 'Peptide count for "'+ob.tge_class+'"', "size": num.pepSum, "type":"peptides", "children": sampleList }) 
    orgList.append({ "name": 'TGE type "'+ob.tge_class+'"', "size": ob.obsCount, "children": pepList, "type":"TGE type" })

  test = {
    "name": "tgeBreakdown",
    "children": orgList
  }

  data = json.dumps(test)

  return data


@plots.route('/aminoseq/<aminoSeq>.json')
def aminoseqJSON(aminoSeq):
  tgeList = []
  # Get the list of TGEs for the given amino acid sequence (partial or exact match)
  #tges = TGE.query.with_entities(TGE.id).filter(TGE.amino_seq.like("%"+amino_seq+"%")).all()

  tges  = Observation.query.with_entities(Observation.organism, func.count(distinct(Observation.tge_id)).label('orgCount')).\
              join(TGE).filter(TGE.amino_seq.like("%"+aminoSeq+"%")).\
              group_by(Observation.organism).all()

  for tge in tges: 
    obsList = []

    obs = Observation.query.with_entities(Observation.organism, func.count(Observation.organism).label('obsCount')).\
              join(TGE).filter(TGE.amino_seq.like("%"+aminoSeq+"%"), Observation.organism == tge.organism).\
              group_by(Observation.organism).all()

    for ob in obs:
      classList = []

      classes = Observation.query.with_entities(Observation.tge_class, func.count(Observation.tge_class).label('classCount')).\
                  join(TGE).filter(TGE.amino_seq.like("%"+aminoSeq+"%"), Observation.organism == tge.organism).\
                  group_by(Observation.tge_class).all()

      for tgeClass in classes:
        sampleList = []

        samples = Sample.query.with_entities(Sample.name, func.count(Observation.tge_id).label('sampleCount')).\
                  join(Observation).join(TGE).filter(TGE.amino_seq.like("%"+aminoSeq+"%"), Observation.organism == tge.organism, Observation.tge_class == tgeClass.tge_class).\
                  group_by(Sample.name).all()

        for sample in samples:
          sampleList.append({ "name": 'TGE observations from sample "' + sample.name +'"', "size": sample.sampleCount, "type": "samples" })

        classList.append({ "name": 'TGE observations with type "' + tgeClass.tge_class+'"', "size": tgeClass.classCount, "type": "classes", "children": sampleList })

      obsList.append({ "name": "TGE Observations in " + ob.organism, "size": ob.obsCount, "type": "observations", "children": classList })

    tgeList.append({ "name": "TGEs in " + tge.organism, "size": tge.orgCount, "type": "organism", "children": obsList })

  test = {
    "name": "tgeBreakdown",
    "children": tgeList
  }

  data = json.dumps(test)

  return data



@plots.route('/experiment/<experiment>.json')
def expJSON(experiment):
  sampleList = []

  samples = Sample.query.filter_by(exp_id=experiment).all()

  for sample in samples:
    pepNumList = []

    obsNum = Observation.query.filter(Observation.sample_id==sample.id).distinct(Observation.tge_id).count()

    pepNum = Observation.query.with_entities(Observation.sample_id, func.sum(Observation.peptide_num).label('pepSum')).\
                    filter(Observation.sample_id==sample.id).\
                    group_by(Observation.sample_id).all() 
    
    for num in pepNum:
      tranNumList = []

      tranNum = Observation.query.with_entities(func.count(Observation.id).label('tranCount')).\
                    join(Transcript, Observation.id==Transcript.obs_id).\
                    filter(Observation.sample_id==sample.id).all() 

      for tran in tranNum: 
        orgList = []

        obs = Observation.query.with_entities(Observation.organism, func.count(distinct(Observation.tge_id)).label('orgCount')).\
                filter_by(sample_id=sample.id).\
                group_by(Observation.organism).all()

        for ob in obs:
          orgList.append({ "name": "TGEs in organism "+ob.organism, "size": ob.orgCount, "type":"organisms" })

        tranNumList.append({ "name": "Transcripts from sample "+sample.name, "size": tran.tranCount, "type":"transcripts",  "children":orgList }) 

      pepNumList.append({ "name": "Identified peptides from sample "+sample.name, "size": num.pepSum, "type":"peptides",  "children":tranNumList }) 

    sampleList.append({ "name": "TGEs from Sample "+ sample.name, "size": obsNum, "type":"samples" , "children":pepNumList })

  test = {
    "name": "tgeBreakdown",
    "children": sampleList
  }

  data = json.dumps(test)

  return data

@plots.route('/protein/<uniprotID>.json')
def protJSON(uniprotID):
  obsList = []

  obs  = Observation.query.with_entities(Observation.tge_class, func.count(distinct(Observation.tge_id)).label('obsCount')).\
                     filter_by(uniprot_id = uniprotID).group_by(Observation.tge_class).\
                     order_by(Observation.tge_class).all()

  for ob in obs:
    pepNumList = []


    pepNum = Observation.query.with_entities(Observation.tge_class, func.sum(Observation.peptide_num).label('pepSum')).\
                    filter_by(uniprot_id = uniprotID, tge_class=ob.tge_class).\
                    group_by(Observation.tge_class).\
                    order_by(Observation.tge_class).all() 
    
    for num in pepNum:
      pepList = []

      # Find the number of peptides for this TGE observation and category of organism
      peptides = Peptide.query.with_entities(Peptide.aa_seq, func.count(Peptide.aa_seq).label('pepCount')).\
                    join(TgeToPeptide, Peptide.id == TgeToPeptide.peptide_id).\
                    join(Observation,  Observation.id == TgeToPeptide.obs_id).\
                    filter_by(uniprot_id = uniprotID, tge_class=ob.tge_class).\
                    group_by(Peptide.aa_seq).distinct(Peptide.aa_seq).all() 
      
      for pep in peptides:
      #   sampleList = []

      #   samples = Sample.query.with_entities(Sample.name, func.count(Sample.name).label('smplCount')).\
      #               join(Observation, Observation.sample_id==Sample.id).\
      #               join(TgeToPeptide, Observation.id == TgeToPeptide.obs_id).\
      #               join(Peptide, Peptide.id == TgeToPeptide.peptide_id).\
      #               filter(Observation.organism == ob.organism, Observation.tge_id == tge.id, Peptide.aa_seq == pep.aa_seq).\
      #               group_by(Sample.name).all()

      #   for smpl in samples:
      #     sampleList.append({ "name": "Samples "+smpl.name, "size": smpl.smplCount, "type":"samples" })

        pepList.append({ "name": 'Peptides "'+pep.aa_seq+'"', "size": pep.pepCount, "type":"peptides" }) 

      pepNumList.append({ "name": 'Identified peptides of type "'+num.tge_class+'"', "size": num.pepSum, "type":"peptide count", "children": pepList }) 

    obsList.append({ "name": 'TGEs of type "'+ ob.tge_class+'"', "size": ob.obsCount, "type":"TGEs", "children":pepNumList })

  test = {
    "name": "tgeBreakdown",
    "children": obsList
  }

  data = json.dumps(test)

  return data

