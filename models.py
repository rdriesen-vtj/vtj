#!/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from run import db#, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
#from run import login_manager

#@login_manager.user_loader
#def load_user(user_id):
#    return Users.query.get(int(user_id)) 

OrgsUsers = db.Table('OrgsUsers',\
    db.Column('user_id', db.Integer, db.ForeignKey('users_table.id')),\
    db.Column('org_id', db.Integer, db.ForeignKey('orgs_table.id')),\
    db.Column('id', db.Integer, primary_key=True))

UsersProjs = db.Table('UsersProjs',\
    db.Column('user_id', db.Integer, db.ForeignKey('users_table.id')),\
    db.Column('proj_id', db.Integer, db.ForeignKey('projs_table.id')),\
    db.Column('id', db.Integer, primary_key=True))
    
OrgsProjs = db.Table('OrgsProjs',\
    db.Column('org_id', db.Integer, db.ForeignKey('orgs_table.id')),\
    db.Column('proj_id', db.Integer, db.ForeignKey('projs_table.id')),\
    db.Column('id', db.Integer, primary_key=True))
 
UsersTasks = db.Table('UsersTasks',\
    db.Column('user_id', db.Integer, db.ForeignKey('users_table.id')),\
    db.Column('task_id', db.Integer, db.ForeignKey('tasks_table.id')),\
    db.Column('id', db.Integer, primary_key=True))

class ProjsUsers(db.Model):
    __tablename__ = 'projsusers_table'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #proj_id = db.Column(db.Integer, db.ForeignKey('projs_table.id'), primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    proj_id = db.Column(db.Integer, db.ForeignKey('projs_table.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    status = db.Column(db.String(32))
    proj = db.relationship("Projs", back_populates="userss")
    user = db.relationship("Users", back_populates="projss")
    
class UsersMsgs(db.Model):
    __tablename__ = 'usersmsgs_table'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    msg_id = db.Column(db.Integer, db.ForeignKey('msgs_table.id'), primary_key=True)
    status = db.Column(db.String(32))
    autor = db.Column(db.String(32))
    user = db.relationship("Users", back_populates="msgs")
    msg = db.relationship("Msgs", back_populates="users")
    
#UsersMsgs = db.Table('UsersMsgs',\
#    db.Column('user_id', db.Integer, db.ForeignKey('users_table.id')),\
#    db.Column('msg_id', db.Integer, db.ForeignKey('msgs_table.id')),\
#    db.Column('id', db.Integer, primary_key=True))

class Icons(db.Model):
    __tablename__ = 'icons_table'
    id = db.Column(db.Integer, primary_key=True)
    icon_url = db.Column(db.String(128))
    icon_name = db.Column(db.String(128))
    tipo = db.Column(db.String(32))
    users = db.relationship('Users',backref="avatar", lazy='dynamic')
    orgs = db.relationship('Orgs',backref="logo", lazy='dynamic')
    projs = db.relationship('Projs',backref="logo", lazy='dynamic')
    criador_id = db.Column(db.Integer)
    #etapa_id = db.Column(db.Integer, db.ForeignKey('etapas_table.id'), primary_key=True)
    
    def __repr__(self):
        return '<Icon {}>'.format(self.icon_name)

class Posts(db.Model):
    __tablename__ = 'posts_table'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    
    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
class Msgs(db.Model):
    __tablename__ = 'msgs_table'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text(65535))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tipo = db.Column(db.String(32))
    origin_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    users = db.relationship("UsersMsgs", back_populates="msg")

    def __repr__(self):
        return '<Msg {}>'.format(self.body)

class Users(UserMixin, db.Model):
    __tablename__ = 'users_table'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    nome = db.Column(db.String(64), index=True, unique=False)
    sobrenome = db.Column(db.String(64), index=True, unique=False)
    telefone = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(120), index=True, unique=False)
    password_hash = db.Column(db.String(128))
    avatar_id = db.Column(db.Integer, db.ForeignKey('icons_table.id'), primary_key=True)
    posts = db.relationship('Posts', backref='author', lazy='dynamic')
    msgs_sent = db.relationship('Msgs', backref='origin', lazy='dynamic')
    resp_orgs = db.relationship('Orgs', backref='responsavel', lazy='dynamic')
    resp_projs = db.relationship('Projs', backref='responsavel', lazy='dynamic')
    resp_tasks = db.relationship('Tasks', backref='responsavel', lazy='dynamic')
    orgs = db.relationship('Orgs', secondary=OrgsUsers, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    projs = db.relationship('Projs', secondary=UsersProjs, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    tasks = db.relationship('Tasks', secondary=UsersTasks, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    #msgs = db.relationship('Msgs', secondary=UsersMsgs, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    msgs = db.relationship("UsersMsgs", back_populates="user")
    projss = db.relationship("ProjsUsers", back_populates="user")
    #projss = db.relationship("ProjsUsers", backref='user', lazy='dynamic')
    #projss = db.relationship("ProjsUsers", secondary=ProjsUsers, backref=db.backref('usuario', lazy='dynamic'), lazy='dynamic')
    confirmed = db.Column(db.Boolean, default=False)
    genero = db.Column(db.String(32), index=True, unique=False)
    endereco1 = db.Column(db.String(128))
    endereco2 = db.Column(db.String(128))
    endereco3 = db.Column(db.String(128))
    cidade = db.Column(db.String(64))
    estado = db.Column(db.String(64))
    pais = db.Column(db.String(64))
    cep = db.Column(db.String(32))
    dia = db.Column(db.Integer)
    mes = db.Column(db.Integer)
    ano = db.Column(db.Integer)
    sobre_mim = db.Column(db.Text(5000))
 
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
   
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')
    
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')
    
    #@staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = Users.query.get(data.get('reset'))
        if user is None:
            return False
        user.set_password(new_password)
        
        db.session.add(user)
        return True

    def __repr__(self):
        return '<User %r>' % self.username

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Orgs(UserMixin,db.Model):
    __tablename__ = 'orgs_table'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(140))
    contato = db.Column(db.String(140))
    descricao = db.Column(db.Text(65535))
    logo_id = db.Column(db.Integer, db.ForeignKey('icons_table.id'), primary_key=True)
    projs = db.relationship('Projs', secondary=OrgsProjs, backref=db.backref('orgs', lazy='dynamic'), lazy='dynamic')
    visibilidade = db.Column(db.String(32))
    #responsavel_id = db.Column(db.Integer, db.ForeignKey('users_table.id'))
    status = db.Column(db.String(32))
    
    def __repr__(self):
        return '<Org {}>'.format(self.titulo)

class Projs(UserMixin,db.Model):
    __tablename__ = 'projs_table'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(140))
    objetivo = db.Column(db.String(140))
    descricao = db.Column(db.Text(65535))
    status = db.Column(db.String(32))
    #responsavel_id = db.Column(db.Integer, db.ForeignKey('users_table.id'))
    icon_id = db.Column(db.Integer, db.ForeignKey('icons_table.id'), primary_key=True)
    visibilidade = db.Column(db.String(32))
    #tasks = db.relationship('Tasks', backref='projeto', lazy='dynamic')
    #etapas = db.relationship('Etapas', backref='projeto', lazy='dynamic')
    userss = db.relationship("ProjsUsers", back_populates="proj")
    ##userss = db.relationship("ProjsUsers", backref='proj', lazy='dynamic')
    ##userss = db.relationship("ProjsUsers", secondary=ProjsUsers, backref=db.backref('projeto', lazy='dynamic'), lazy='dynamic')
    
    def __repr__(self):
        return '<Projeto {}>'.format(self.titulo)
    
class Tasks(UserMixin,db.Model):
    __tablename__ = 'tasks_table'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(140))
    responsavel_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    descricao = db.Column(db.Text(65535))
    status = db.Column(db.String(32))
    proj_id = db.Column(db.Integer, db.ForeignKey('projs_table.id'), primary_key=True)
    progresso = db.Column(db.Integer)

    def __repr__(self):
        return '<Task {}>'.format(self.titulo)
    
class Etapas(db.Model):
    __tablename__ = 'etapas_table'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(140))
    body = db.Column(db.Text(5000))
    status = db.Column(db.String(32))
    visibilidade = db.Column(db.String(32))
    proj_id = db.Column(db.Integer, db.ForeignKey('projs_table.id'), primary_key=True)
    photos = db.relationship('Icons', backref='etapa', lazy='dynamic')
    
    def __repr__(self):
        return '<Etapa {}>'.format(self.body)
       
#@login_manager.user_loader
#def load_user(user_id):
#    return Users.query.get(int(user_id))
