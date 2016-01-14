# This is where you define the models of your application. 
# This may be split into several modules in the same way as views.py.
# Import the database object (db) from the main application module

from . import db
from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash

# Define a base model for other database tables to inherit
class Base(db.Model):
  __abstract__  = True

  id      = db.Column(db.Integer,   primary_key=True, autoincrement=True)
  created = db.Column(db.DateTime,  default=datetime.utcnow())
  updated = db.Column(db.DateTime,  default=datetime.utcnow(), onupdate=datetime.utcnow())

  def __init__(self):
    self.created = datetime.utcnow()
    self.updated = datetime.utcnow()
 

class TGE(Base):
  __tablename__ = 'tge'
  
  amino_seq = db.Column(db.Text, nullable=False) # unique=True
  
  def __init__(self, amino_seq):
    self.amino_seq   = amino_seq

  def __repr__(self):
    return '<TGE %r>' % (self.amino_seq)



class TGEobservation(Base):
  __tablename__ = 'tge_observation'
  
  tge_id      = db.Column('tge_id',    db.Integer, db.ForeignKey("tge.id"))
  sample_id   = db.Column('sample_id', db.Integer, db.ForeignKey("sample.id"))
  name        = db.Column(db.String(255)) # unique=True
  description = db.Column(db.String(255))
  #uniprot_id  = db.Column(db.String(255))
  #membership  = db.Column(db.String(255))
  organism    = db.Column(db.String(255))
  peptide_num = db.Column(db.Integer)
  
  def __init__(self, name, description, peptide_num, peptide_acc, organism):
    self.name        = name
    self.description = description
    self.peptide_num = peptide_num
    self.peptide_acc = peptide_acc
    #self.uniprot_id  = uniprot_id
    #self.membership  = membership
    self.organism    = organism

  def __repr__(self):
    return '<TGE %r>' % (self.name)


class Transcript(Base):
  __tablename__ = 'transcript'
  
  obs_id    = db.Column('obs_id', db.Integer, db.ForeignKey("tge_observation.id"))
  # sample_id = db.Column('sample_id', db.Integer, db.ForeignKey("sample.id"))
  # name      = db.Column(db.String(255), nullable=False) # unique=True
  dna_seq   = db.Column(db.Text, nullable=False)
  # species   = db.Column(db.String(255))
  ensemble  = db.Column(db.String(255)) 
  chr       = db.Column(db.String(255)) 
  start     = db.Column(db.Integer)
  end       = db.Column(db.Integer)
  assembly  = db.Column(db.String(255))
  
  def __init__(self, dna_seq, ensemble, chr, start, end, assembly):
    self.dna_seq  = dna_seq
    self.ensemble = ensemble
    # self.species  = species
    self.chr      = chr
    self.start    = start
    self.end      = end
    sef.assembly  = assembly


class Sample(Base):
  __tablename__ = 'sample'
  
  name    = db.Column(db.String(255), unique=True)
  user_id = db.Column('user_id', db.Integer, db.ForeignKey("user.id")) # unique=True
  
  def __init__(self, name, user_id):
    self.name    = name
    self.user_id = user_id


class Peptide(Base):
  __tablename__ = 'peptide'
  
  # spectrum_id = db.Column('given_id', db.Integer, db.ForeignKey("spectrum.id"))
  aa_seq      = db.Column(db.String(255), nullable=False) # unique=True
  # calc_mz     = db.Column(db.Numeric)
  # exp_mz      = db.Column(db.Numeric)
  
  def __init__(self, amino_seq):
    self.aa_seq  = aa_seq
  #   self.calc_mz = calc_mz
  #   self.exp_mz  = exp_mz

  def __repr__(self):
    return '<Peptide %r>' % (self.aa_seq)


# TgeToPeptide = db.Table('tge_peptide', Base.metadata,
#     db.Column('tge_id',     db.Integer, db.ForeignKey("tge.id")),
#     db.Column('peptide_id', db.Integer, db.ForeignKey("peptide.id"))
# )

class TgeToPeptide(Base):
  __tablename__ = 'tge_peptide'
  
  obs_id     = db.Column('obs_id',     db.Integer, db.ForeignKey("tge_observation.id"), nullable=False)
  peptide_id = db.Column('peptide_id', db.Integer, db.ForeignKey("peptide.id"), nullable=False)

  def __init__(self, obs_id, peptide_id):
    self.obs_id     = obs_id
    self.peptide_id = peptide_id

  def __repr__(self):
    return '<Test %r>' % (self.obs_id)


class Experiment(Base):
  __tablename__ = 'experiment'
  
  test = db.Column(db.String(255), nullable=False) # unique=True
  
  def __init__(self, test):
    self.test = test

  def __repr__(self):
    return '<Test %r>' % (self.test)


class Run(Base):
  __tablename__ = 'run'
  
  sample_id   = db.Column(db.Integer, nullable=False) # unique=True
  transc_path = db.Column(db.String(255))
  msms_path   = db.Column(db.String(255), nullable=False)
  user_id     = db.Column(db.Integer)
  
  def __init__(self, sample_id, transc_path, msms_path, user_id):
    self.sample_id   = sample_id
    self.transc_path = transc_path
    self.msms_path   = msms_path
    self.user_id     = user_id

  def __repr__(self):
    return '<Test %r>' % (self.sample_id)


class Spectrum(Base):
  __tablename__ = 'spectrum'
  
  given_id = db.Column(db.Integer)
  title    = db.Column(db.String(255))
  location = db.Column(db.String(255))

  def __init__(self, given_id, title):
    self.given_id  = given_id
    self.title     = title
    self.location  = location

  def __repr__(self):
    return '<Spectrum %r>' % (self.title)


class User(Base):
  __tablename__ = 'user'
  
  email     = db.Column(db.String(255), nullable=False, unique=True)
  password  = db.Column(db.String(255), nullable=False)
  fullname  = db.Column(db.String(255), nullable=False)
  #address   = db.Column(db.String(255), nullable=False)
  
  def __init__(self, email, password, fullname):
    self.email    = email
    self.set_password(password)
    self.fullname = fullname
    #self.address  = address

  def set_password(self, password):
    self.password = generate_password_hash(password)
   
  def check_password(self, password):
    return check_password_hash(self.password, password)

  def __repr__(self):
    return '<User %r>' % (self.fullname)

db.create_all()