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
 

class User(Base):
  __tablename__ = 'user'
  
  email     = db.Column(db.String(255), nullable=False, unique=True)
  password  = db.Column(db.String(255), nullable=False)
  fullname  = db.Column(db.String(255), nullable=False)
  #address   = db.Column(db.String(255), nullable=False)
  
  # New instance instantiation procedure
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


class TGE(Base):
  __tablename__ = 'tge'
  
  name        = db.Column(db.String(255)) # unique=True
  description = db.Column(db.String(255))
  amino_seq   = db.Column(db.LargeBinary, nullable=False) # unique=True
  
  # New instance instantiation procedure
  def __init__(self, name, description, amino_seq):
    self.name        = name
    self.description = description
    self.amino_seq   = amino_seq

  def __repr__(self):
    return '<TGE %r>' % (self.name)


class Peptide(Base):
  __tablename__ = 'peptide'
  
  aa_seq = db.Column(db.String(255), nullable=False) # unique=True
  
  # New instance instantiation procedure
  def __init__(self, amino_seq):
    self.aa_seq = aa_seq

  def __repr__(self):
    return '<Peptide %r>' % (self.aa_seq)


class Experiment(Base):
  __tablename__ = 'experiment'
  
  test = db.Column(db.String(255), nullable=False) # unique=True
  
  # New instance instantiation procedure
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
  
  # New instance instantiation procedure
  def __init__(self, sample_id, transc_path, msms_path, user_id):
    self.sample_id   = sample_id
    self.transc_path = transc_path
    self.msms_path   = msms_path
    self.user_id     = user_id

  def __repr__(self):
    return '<Test %r>' % (self.sample_id)


class Transcript(Base):
  __tablename__ = 'transcript'
  
  tge_id   = db.Column('tge_id', db.Integer, db.ForeignKey("tge.id"))
  dna_seq  = db.Column(db.LargeBinary, nullable=False)
  ensemble = db.Column(db.String(255)) # unique=True
  species  = db.Column(db.String(255))
  chr      = db.Column(db.String(255)) # unique=True
  start    = db.Column(db.Integer)
  end      = db.Column(db.Integer)
  assembly = db.Column(db.String(255))
  amino_seq   = db.Column(db.LargeBinary, nullable=False)

  # New instance instantiation procedure
  def __init__(self, dna_seq, ensemble, species, chr, start, end, assembly, amino_seq):
    self.dna_seq  = dna_seq
    self.ensemble = ensemble
    self.species  = species
    self.chr      = chr
    self.start    = start
    self.end      = end
    sef.assembly  = assembly
    sef.amino_seq = amino_seq

  def __repr__(self):
    return '<Transcript %r>' % (self.dna_seq)

db.create_all()