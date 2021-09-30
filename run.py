#!/bin/python
# -*- coding: utf-8 -*-
import os
import base64
import json
import string
import logging
from time import sleep, gmtime, strftime
from datetime import datetime
from flask import Flask, render_template, flash, redirect, request, url_for, jsonify, logging as flog
#from config import Config
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_mail import Mail, Message
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
#from wtforms import SubmitField
from threading import Thread
from werkzeug.urls import url_parse
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from random import randint
from faker import Faker

##### IMPORTS PARA PARA FORMs #####

#from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField, TextAreaField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
#from models import Users, Orgs, Posts, Projs, Tasks, Etapas
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed

##### FIM DE IMPORTS PARA FORMs #####

##### IMPORTS PARA MODELs #####

#from datetime import datetime
#from run import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from sqlalchemy.orm import relationship

##### FIM DE IMPORTS PARA MODELs #####

#app = Flask(__name__)
#app.config.from_object(Config)
#login_manager = LoginManager(app)
#login_manager.login_view = 'login'
#DEBUG = True

#def create_app(config_name):
#    login_manager.init_app(app)
#    moment.init_app(app)

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads') # you'll need to create a folder named uploads
 
app.config['SECRET_KEY'] = 'you-will-never-never-guess'
#SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
dbmysql = "vamostrabalhar"
usermysql = "admin"
senhamysql = "S3nhaADMIN#"
hostmysql = "127.0.0.1"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+usermysql+':'+senhamysql+'@'+hostmysql+'/'+dbmysql
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads') # you'll need to create a folder named upload
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'contato.vtj@gmail.com'
app.config['MAIL_PASSWORD'] = 'Rtdqxj00'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Vamos Trabalhar Juntos]'
app.config['FLASKY_MAIL_SENDER'] = 'contato.vtj@gmail.com'
app.config['FLASKY_ADMIN'] = 'contato.vtj@gmail.com' 

#app.config['MAIL_SERVER'] = 'smtp.gmail.com'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USERNAME'] = 'contato.vtj@gmail.com'
#app.config['MAIL_PASSWORD'] = 'Rtdqxj00'
#app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
#app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
#app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Vamos Trabalhar Juntos]'
#app.config['FLASKY_MAIL_SENDER'] = 'contato.vtj@gmail.com'
#app.config['FLASKY_ADMIN'] = 'contato.vtj@gmail.com'   
#app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

mail = Mail(app)
db = SQLAlchemy(app)

db.create_all()

migrate = Migrate(app, db)
moment = Moment(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    print("load_user id:"+str(user_id))
    
    return Users.query.filter(Users.id == int(user_id)).first()

#return Users.query.get(int(user_id))

#from forms import LoginForm, RegistrationForm, Registration2Form, NewprojForm, EditprojForm, OrgusersForm, ProjusersForm,\
#                  NewtaskForm, EdittaskForm, ProfileForm, OrgcreateForm, EditorgForm, UploadForm, MsgForm,\
#                  PasswordResetRequestForm, PasswordResetForm, ChangePasswordForm, EnderecoForm, TestForm, NewstageForm

##### FORMs #####

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Senha antiga', validators=[DataRequired()])
    password = PasswordField('Senha Nova ', validators=[DataRequired(), EqualTo('password2', message='As senhas precisam ser iguais.')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update Password')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Reset de senha')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Senha Nova', validators=[DataRequired(), EqualTo('password2', message='As senhas precisam ser iguais.')])
    password2 = PasswordField('Confirmação da Senha Nova', validators=[DataRequired()])
    submit = SubmitField('Reset de senha')

class TestForm(FlaskForm):
    campo1 = StringField('Campo1')
    submit = SubmitField('ok')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class NewprojForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', render_kw={"rows": 70, "cols": 11}, validators=[DataRequired()])
    objetivo = StringField('Objetivo', validators=[DataRequired()])
    organizacao = SelectField('Organização',coerce=int, validators=[DataRequired()])
    responsavel = SelectField('Responsável',coerce=int)
    status= RadioField('Status', choices=[('ATIVO','ATIVO'),('FINALIZADO','FINALIZADO'),('INATIVO','INATIVO')], validate_choice=False)
    visibilidade = RadioField('Visibilidade', choices=[('PÚBLICO','PÚBLICO'),('PRIVADO','PRIVADO'),('SECRETO','SECRETO')])
    icon = StringField('Icon', validators=[])
    logo_url = StringField('LogoUrl', validators=[])
    submit = SubmitField('Register')
    
class EditprojForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', render_kw={"rows": 70, "cols": 11}, validators=[DataRequired()])
    objetivo = StringField('Objetivo', validators=[DataRequired()])
    organizacao = SelectField('Organização', validate_choice=False)
    responsavel = SelectField('Responsável', validate_choice=False)
    status= RadioField('Status', choices=[('ATIVO','ATIVO'),('FINALIZADO','FINALIZADO'),('INATIVO','INATIVO')], validate_choice=False)
    visibilidade = RadioField('Visibilidade', choices=[('PÚBLICO','PÚBLICO'),('PRIVADO','PRIVADO'),('SECRETO','SECRETO')], validate_choice=False)
    icon = StringField('Icon', validators=[])
    submit = SubmitField('SALVAR')

class NewstageForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    body = TextAreaField('Texto', render_kw={"rows": 70, "cols": 11}, validators=[DataRequired()])
    visibilidade = RadioField('Visibilidade', choices=[('RASCUNHO','RASCUNHO'),('VISÍVEL','VISÍVEL')], validate_choice=False)
    imagens = StringField('Imagens')
    submit = SubmitField('SALVAR')  
    
class NewtaskForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', render_kw={"rows": 70, "cols": 11}, validators=[DataRequired()])
    responsavel = SelectField('Responsável',coerce=int)
    submit = SubmitField('SALVAR')     

class EdittaskForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', render_kw={"rows": 70, "cols": 11}, validators=[DataRequired()])
    responsavel = SelectField('Responsável', validate_choice=False)
    #progresso = StringField('Progresso', validators=[DataRequired()])
    prog = RadioField('Progresso', choices=[('0','0%'),('10','10%'),('20','20%'),('30','30%'),('40','40%'),\
                                               ('50','50%'),('60','60%'),('70','70%'),('80','80%'),\
                                               ('90','90%'),('100','100%')], validate_choice=False)
    submit = SubmitField('SALVAR') 

class MsgForm(FlaskForm):
    body = TextAreaField('Mensagem', render_kw={"rows": 70, "cols": 11}, validators=[DataRequired()])
    destination = SelectMultipleField('Destino', validate_choice=False, coerce= int)
    submit = SubmitField('ENVIAR')
    
class OrgusersForm(FlaskForm):
    nome_convidado = StringField('Nome', validators=[])
    sobrenome_convidado = StringField('Sobrenome', validators=[])
    excluidos = SelectMultipleField('Membros', validate_choice=False, coerce= int)
    submit = SubmitField('SALVAR')
    
class ProjusersForm(FlaskForm):
    incluidos = SelectMultipleField('Membros', validate_choice=False, coerce= int)
    excluidos = SelectMultipleField('Participantes', validate_choice=False, coerce= int)
    editados = SelectMultipleField('Participantes', validate_choice=False, coerce= int)
    editadosresp = SelectField('Participantes', validate_choice=False, coerce= int)
    status = RadioField('Status', choices=[('participante','participante'),('editor','editor'),\
                                           ('administrador','administrador')],\
                                          validate_choice=False)
    statusresp = RadioField('Status', choices=[('participante','participante'),('editor','editor'),\
                                           ('administrador','administrador'),('responsável','responsável')],\
                                          validate_choice=False)
    submit = SubmitField('SUBMETER') 
    
class ProfileForm(FlaskForm):
    nome = StringField('Nome', validators=[])
    sobrenome = StringField('Sobrenome', validators=[])
    #username = StringField('Username', validators=[])
    email = StringField('Email', validators=[])
    telefone = StringField('Telefone', validators=[])
    avatar = StringField('Avatar', validators=[])
    photo = FileField('photo', validators=[FileAllowed(['png', 'jpg'], "wrong format!")])
    genero = RadioField('Gênero', choices=[('Masculino','Masculino'),('Feminino','Feminino')])
    endereco1 = StringField('Endereço (Rua e Número)', validators=[])
    endereco2 = StringField('Complemento (Apt,bloco,casa...)', validators=[])
    endereco3 = StringField('Bairro', validators=[])
    cep = StringField('CEP', validators=[])
    cidade = StringField('Cidade', validators=[])
    estado = StringField('Estado', validators=[])
    pais = StringField('País', validators=[])
    dia = StringField('Dia', validators=[])
    mes = StringField('Mês', validators=[])
    ano = StringField('Ano', validators=[])
    sobre_mim = TextAreaField('Sobre mim...', render_kw={"rows": 70, "cols": 11}, validators=[])
    #password = PasswordField('Password', validators=[])    
    #org = SelectField('Organização',choices=[],validators=[])
    #acao_org = RadioField('Ação', choices=[('manter','MANTER'),('entrar','ENTRAR'),('sair','SAIR')],validators=[])
    #proj = SelectField('Projeto',choices=[],validators=[])
    #acao_proj = RadioField('Ação', choices=[('manter','MANTER'),('entrar','ENTRAR'),('sair','SAIR')],validators=[])
    submit = SubmitField('SALVAR')

class EnderecoForm(FlaskForm):

    endereco1 = StringField('Endereço (Rua e Número)', validators=[])
    endereco2 = StringField('Complemento (Apt,bloco,casa...)', validators=[])
    endereco3 = StringField('Bairro', validators=[])
    cep = StringField('CEP', validators=[])
    cidade = StringField('Cidade', validators=[])
    estado = StringField('Estado', validators=[])
    pais = StringField('País', validators=[])
    txtEndereco = StringField('txtEndereco', validators=[])
    txtLatitude = StringField('txtLatitude', validators=[])
    txtLongitude = StringField('txtLongitude', validators=[])
    submit = SubmitField('SALVAR')
    
class UploadForm(FlaskForm):
    imagem = FileField('imagem', validators=[FileAllowed(['gif','png', 'jpg'], "wrong format!")])   
    submit = SubmitField('Upload')
   
    
class RegistrationForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[])
    avatar = StringField('Avatar',default="12", validators=[])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Continuar')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username existente. Por favor use um username diferente.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
class Registration2Form(FlaskForm):
    avatar = StringField('Avatar', validators=[])
    submit = SubmitField('Registrar')

        
class OrgcreateForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    contato = StringField('Contato', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', render_kw={"rows": 70, "cols": 11}, validators=[DataRequired()])
    logo = StringField('Logo',default="10", validators=[])
    #responsavel = SelectField('Responsável',choices=[])
    visibilidade = RadioField('Visibilidade', choices=[('PÚBLICO','PÚBLICO'),('PRIVADO','PRIVADO'),('SECRETO','SECRETO')])
    logo_url = StringField('LogoUrl', validators=[])
    submit = SubmitField('REGISTRAR')
        
class EditorgForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    contato = StringField('Contato', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', render_kw={"rows": 70, "cols": 11}, validators=[DataRequired()])
    logo = StringField('Logo',default="10", validators=[])
    responsavel = SelectField('Responsável', validate_choice=False)
    visibilidade = RadioField('Visibilidade', choices=[('PÚBLICO','PÚBLICO'),('PRIVADO','PRIVADO'),('SECRETO','SECRETO')])
    status = RadioField('Status', choices=[('ATIVO','ATIVO'),('DESATIVADO','DESATIVADO')])
    submit = SubmitField('SALVAR')

##### FIM DOS FORMs #####




#from models import Posts, Users, Orgs, Tasks, Projs, Icons, Msgs, UsersMsgs, Etapas, ProjsUsers

##### MODELs #####

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
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
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
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    
    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
class Msgs(db.Model):
    __tablename__ = 'msgs_table'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    body = db.Column(db.Text(65535))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tipo = db.Column(db.String(32))
    origin_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    users = db.relationship("UsersMsgs", back_populates="msg")

    def __repr__(self):
        return '<Msg {}>'.format(self.body)

class Users(UserMixin, db.Model):
    __tablename__ = 'users_table'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    nome = db.Column(db.String(64), index=True, unique=False)
    sobrenome = db.Column(db.String(64), index=True, unique=False)
    telefone = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(120), index=True, unique=False)
    password_hash = db.Column(db.String(128))
    avatar_id = db.Column(db.Integer, db.ForeignKey('icons_table.id'), primary_key=True)
    posts = db.relationship('Posts', backref='author', lazy='dynamic')
    msgs_sent = db.relationship('Msgs', backref='origin', lazy='dynamic')
    #resp_orgs = db.relationship('Orgs', backref='responsavel', lazy='dynamic')
    #resp_projs = db.relationship('Projs', backref='responsavel', lazy='dynamic')
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
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    titulo = db.Column(db.String(140))
    contato = db.Column(db.String(140))
    descricao = db.Column(db.Text(65535))
    logo_id = db.Column(db.Integer, db.ForeignKey('icons_table.id'), primary_key=True)
    projs = db.relationship('Projs', secondary=OrgsProjs, backref=db.backref('orgs', lazy='dynamic'), lazy='dynamic')
    visibilidade = db.Column(db.String(32))
    responsavel_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    status = db.Column(db.String(32))
    
    def __repr__(self):
        return '<Org {}>'.format(self.titulo)

class Projs(UserMixin,db.Model):
    __tablename__ = 'projs_table'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
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
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
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
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    titulo = db.Column(db.String(140))
    body = db.Column(db.Text(5000))
    status = db.Column(db.String(32))
    visibilidade = db.Column(db.String(32))
    proj_id = db.Column(db.Integer, db.ForeignKey('projs_table.id'), primary_key=True)
    #photos = db.relationship('Icons', backref='etapa', lazy='dynamic')
    
    def __repr__(self):
        return '<Etapa {}>'.format(self.body)
    
##### FIM DOS MODELs #####

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app, 5 * 1024 * 1024)  # set maximum file size 5 MB

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Users=Users, Posts=Posts, Orgs=Orgs, Projs=Projs, Icons=Icons, Tasks=Tasks, Msgs=Msgs, Etapas=Etapas)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()    
    return thr

user_atual=''

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

print()
print('---------------------------------------------------------')

def DadosIniciais():
    icon1= Icons.query.filter(Icons.id == '1').first()
    if icon1 == None:
        icon1 = Icons(
            id='1',
            icon_name='mangray',
            tipo='avatar',
            icon_url='https://vamostrabalharjuntos.com.br/static/mangray.png',
            criador_id=1)
        db.session.add(icon1)
        db.session.commit()
    icon2= Icons.query.filter(Icons.id == '2').first()
    if icon2 == None:
        icon2 = Icons(
            id='2',
            icon_name='no-icon',
            tipo='logo',
            icon_url='https://vamostrabalharjuntos.com.br/static/empty.png',
            criador_id=1)
        db.session.add(icon2)
        db.session.commit()
    user1 = Users.query.filter(Users.id == '1').first()
    if user1 == None:
        admin = Users(
            id='1',
            username='admin',
            nome='Administrador',
            sobrenome='1',
            telefone='-',
            email='contato.vtj@gmail.com',
            avatar_id = "1")
        user.set_password('1234')
        db.session.add(admin)
        db.session.commit()
 
        
    return    

DadosIniciais()
        
def takeSecond(elem):
    return elem[1]

def bigword(frase):
    big = False
    palavras = frase.split(" ")
    for palavra in palavras:
        if len(palavra) > 10:
            big = True
    return (big)

def get_responsavel(user,org=0):
    opcoes=[]
    opcao =(user.id,user.nome+' '+user.sobrenome)
    opcoes.append(opcao)
    if org!=0:
        try:
            q = org.users.all()
            #print("---get_responsavel---------------------------------------")
            #print (q)
            for user in q:
              if user.id != user.id:
                opcao =(int(user.id),user.nome+' '+user.sobrenome)  
                opcoes.append(opcao)  
                #print (str(opcoes))
                #print("---------------------------------------------------------")
        except:
            flash("A organização deste projeto está sem membros?")                                  

    return opcoes

def get_organizacao(user=current_user):
    #print("---get_organizacao---------------------------------------")
    #print ("current_user: "+str(current_user))
    #print ("current_user.nome: "+current_user.nome)
    q = user.orgs.all()
    #q = Orgs.query.all()
    opcoes=[]
    #opcao =(0,'ESCOLHA UMA ORGANIZAÇÃO ou CRIE UMA')
    #opcoes.append(opcao)
    #print ("q: "+str(q))
    for org in q:
      opcao =(int(org.id),org.titulo)  
      opcoes.append(opcao) 
    #print ("opcoes: "+str(opcoes))
    #print("---------------------------------------------------------")
    return opcoes

def split_lines(string):
    return string.split('\n')

app.jinja_env.filters['split_lines'] = split_lines

@app.route('/checknewmsgs')
@login_required
def checknewmsgs():
    user = Users.query.filter(Users.id == current_user.id).first()
    msgs = user.msgs
    new_count = 0
    for m in msgs:
        if m.status == "new":
            new_count = new_count  + 1
    resposta = jsonify ( new = new_count )
    print(resposta)
    return (resposta)

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = Users.query.filter(Users.id == current_user.id).first()
    msgs = user.msgs
    newmsgs = []
    for m in msgs:
        if m.status == "new":
            newmsgs.append(m)
            m.status = "old"
            db.session.add(m)
            db.session.commit()
    return render_template('index.html', msgs=msgs, newmsgs=newmsgs, user=user, hora=datetime.utcnow())

@app.route('/messages')
@login_required
def messages():
    user = Users.query.filter(Users.id == current_user.id).first()
    msgs = user.msgs
    newmsgs = []
    for m in msgs:
        if m.status == "new":
            newmsgs.append(m)
            m.status = "old"
            db.session.add(m)
            db.session.commit()
    return render_template('messages.html', msgs=msgs, user=user, hora=datetime.utcnow())
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_atual
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
   
@app.route('/logout')
def logout():
    logout_user()
    print (url_for('.index'))
    return redirect(url_for('.index'))
   
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data,
                     nome=form.nome.data,
                     sobrenome=form.sobrenome.data,
                     telefone=form.telefone.data,
                     email=form.email.data,
                     avatar_id = "1")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'Confirme sua conta',
                   'email/confirm', user=user, token=token)
        flash('Um email de confirmação foi enviado para seu email.')
        return redirect(url_for('.index'))        
        #return redirect(url_for('.register2', username=user.username))
    icons = Icons.query.filter_by(tipo='avatar').all()
    avatar = Icons.query.filter_by(id='1').first()
    return render_template('register.html', title='Register', form=form)
    #return render_template('register.html', title='Register', form=form)

@app.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('Sua conta foi confirmada.')
    else:
        flash('O link de confirmação é inválido ou expirou.')
    return redirect(url_for('.index'))

@app.route('/register2/<string:username>', methods=['GET', 'POST'])
def register2(username):
    form = Registration2Form()
    user = Users.query.filter_by(username=username).first()
    avatar_id = user.avatar.id
    if avatar_id == "":
        avata_id = 12
    if form.validate_on_submit():
        avatar_id = int(form.avatar.data)
        if (int(avatar_id) < 1) or (int(avatar_id) > 30):
            avatar_id = 12
        user.avatar_id = int(form.avatar.data)
        db.session.add(user)
        db.session.commit()
        flash('Parabéns, você agora é um usuário cadastrado!')
        return redirect(url_for('.login'))
    icons = Icons.query.filter( (Icons.criador_id=='0') & (Icons.tipo=='avatar'))
    photoicon = Icons.query.filter( (Icons.criador_id==user.id) & (Icons.tipo=='avatar')).first()
    if photoicon == None:
        print("photoicon: None")
    else:
        print("photoicon: "+str(photoicon.id)+" "+photoicon.icon_url )
    #icons = Icons.query.filter_by(tipo='avatar').all()
    return render_template('register2.html', title='Register(cont.)', form=form,\
            nome=user.nome, sobrenome=user.sobrenome, username=user.username, \
            icon_url=user.avatar.icon_url, icon_name=user.avatar.icon_name, avatar=user.avatar.id, icons=icons, photoicon=photoicon)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('.index'))
        else:
            flash('Senha inválida.')
    return render_template("change_password.html", form=form)

@app.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset de sua senha',
                       'email/reset_password',
                       user=user, token=token)
        flash('Enviamos um email com instruções para o reset de sua senha.')
        return redirect(url_for('.login'))
    return render_template('reset_password_request.html', form=form)

@app.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        #user = Users.query.filter_by(email=form.email.data.lower()).first()
        #user = Users.query.filter_by(Users.username==current_user.username).first()
        if Users.reset_password(token, form.password.data):
            db.session.commit()
            flash('Sua senha foi alterada.')
            return redirect(url_for('.login'))
        else:
            return redirect(url_for('.index'))
    return render_template('reset_password.html', form=form)

@app.route('/endereco', methods=['GET', 'POST'])
@login_required
def endereco():
    form = EnderecoForm()
    user = Users.query.filter_by(username=current_user.username).first()

    if form.validate_on_submit():
        user.endereco1 = form.endereco1.data
        user.endereco2 = form.endereco2.data
        user.endereco3 = form.endereco3.data
        user.cep = form.cep.data
        user.cidade = form.cidade.data
        user.estado = form.estado.data
        user.pais = form.pais.data
        
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you edited your profile! '+ form.avatar.data )
        return redirect(url_for('.profile'))
    else:
        file_url = None
    
    form.endereco1.default = user.endereco1
    form.endereco2.default = user.endereco2
    form.endereco3.default = user.endereco3
    form.cep.default = user.cep
    form.cidade.default = user.cidade
    form.estado.default = user.estado
    
    user = Users.query.filter_by(username=current_user.username).first()
    icons = Icons.query.filter( (Icons.criador_id=='0') & (Icons.tipo=='avatar'))
    photoicon = Icons.query.filter( (Icons.criador_id==current_user.id) & (Icons.tipo=='avatar')).first()
    if photoicon == None:
        photoicon = Icons.query.filter( (Icons.criador_id=='0') & (Icons.tipo=='avatar')).first()
    return render_template('endereco.html', title='Endereco', form=form, user=user, icons=icons, photoicon=photoicon)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    user = Users.query.filter_by(username=current_user.username).first()

    if form.validate_on_submit():
        user.nome = form.nome.data
        user.sobrenome = form.sobrenome.data
        user.telefone = form.telefone.data
        user.email = form.email.data
        user.genero = form.genero.data
        user.endereco1 = form.endereco1.data
        user.endereco2 = form.endereco2.data
        user.endereco3 = form.endereco3.data
        user.cep = form.cep.data
        user.cidade = form.cidade.data
        user.estado = form.estado.data
        user.pais = form.pais.data
        user.dia = form.dia.data
        user.mes = form.mes.data
        user.ano = form.ano.data
        user.sobre_mim = form.sobre_mim.data
        user.avatar_id = int(form.avatar.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you edited your profile! '+ form.avatar.data )
        return redirect(url_for('.profile'))
    else:
        file_url = None
    
        form.nome.default = user.nome
    form.sobrenome.default = user.sobrenome
    form.telefone.default = user.telefone
    form.email.default = user.email
    form.genero.default = user.genero
    #form.endereco1.default = user.endereco1
    form.endereco1.default = user.endereco1
    form.endereco2.default = user.endereco2
    form.endereco3.default = user.endereco3
    form.cep.default = user.cep
    form.cidade.default = user.cidade
    form.estado.default = user.estado
    form.dia.default = user.dia
    form.mes.default = user.mes
    form.ano.default = user.ano
    form.sobre_mim.data = user.sobre_mim
    form.avatar.default = str(user.avatar_id)
    
    form.genero.process_data(user.genero)
    user = Users.query.filter_by(username=current_user.username).first()
    icons = Icons.query.filter( (Icons.criador_id=='0') & (Icons.tipo=='avatar'))
    photoicon = Icons.query.filter( (Icons.criador_id==current_user.id) & (Icons.tipo=='avatar')).first()
    if photoicon == None:
        photoicon = Icons.query.filter( (Icons.criador_id=='0') & (Icons.tipo=='avatar')).first()
    return render_template('profile.html', title='Profile', form=form, user=user, icons=icons, photoicon=photoicon)

@app.route('/orgcreate', methods=['GET', 'POST'])
@login_required
def orgcreate():
    global user_atual
    if user_atual=="":
        user_atual=current_user
    responsavel = Users.query.filter(Users.username==current_user.username).first()
    nome_responsavel = responsavel.nome+' '+responsavel.sobrenome
    form = OrgcreateForm()
    id_list=['1']
    icons = Icons.query.filter(and_( Icons.criador_id.in_(id_list,) ,  Icons.tipo == 'icon')).all()
    icon = Icons.query.filter(Icons.id=='2').first()
    empty_orgs = Orgs.query.filter(Orgs.status=="INICIAL").all()
    
    for empty_org in empty_orgs:
        db.session.delete(empty_org)
        db.session.commit()    
    #neworg = Orgs(status="INICIAL",responsavel_id=current_user.id)
    #db.session.add(neworg)
    #neworg.users.append(responsavel)
    #db.session.commit()
    #db.session.flush()
    #org_id=neworg.id
    if form.validate_on_submit():    
        neworg = Orgs(titulo=form.titulo.data,
            descricao=form.descricao.data,
            contato=form.contato.data,
            status="ATIVO",
            visibilidade=form.visibilidade.data,
            logo_id=form.logo.data,
            responsavel_id=current_user.id)
        db.session.add(neworg)
        db.session.commit()
        db.session.flush()
        org_id=neworg.id
        newmember = Users.query.filter(Users.id == current_user.id).first()
        neworg.users.append(newmember)
        db.session.commit()
        if form.logo_url.data != "":
            newicon_url = form.logo_url.data
        else:
            newicon_url = icon.icon_url
        org_icon = Icons(icon_name = "org-"+str(org_id),
                         tipo = "logo",
                         criador_id = current_user.id,
                         icon_url = newicon_url)
        db.session.add(org_icon)
        db.session.commit()
        db.session.flush()
        neworg.logo_id = org_icon.id
        db.session.commit()
        flash('Congratulations, you have a new organization!')
        return redirect(url_for('.organizacao', orgname=str(neworg.titulo)))
    #photoicon = Icons.query.filter( (Icons.icon_name=="unnamed") & (Icons.tipo=='logo')).first()
    photoicon = 'https://www.vamostrabalharjuntos.com.br/projetos/static/images/unnamed.png'
    return render_template('orgcreate.html', title='Organização Nova', icons=icons, form=form, responsavel=responsavel,\
                           icon=icon, photoicon=photoicon)

@app.route('/editorg/<string:orgtit>', methods=['GET', 'POST'])
@login_required
def editorg(orgtit):
    org = Orgs.query.filter(Orgs.titulo==orgtit).first()
    form = EditorgForm()
    id_list=['1']
    icons = Icons.query.filter(and_( Icons.criador_id.in_(id_list,) ,  Icons.tipo == 'icon')).all()
    opcoes=[]
    opcao =(0,'Não Definido')
    opcoes.append(opcao)
    opcao =(org.responsavel.id,org.responsavel.nome+' '+org.responsavel.sobrenome)
    opcoes.append(opcao)
    for user in org.users:
      opcao =(user.id,user.nome+' '+user.sobrenome)  
      if not(opcao in opcoes):
        opcoes.append(opcao)
    form.responsavel.choices = opcoes
    form.visibilidade.default = org.visibilidade
    form.status.default = org.status
    id_list=['1']
    icons = Icons.query.filter(and_( Icons.criador_id.in_(id_list,) ,  Icons.tipo == 'logo')).all()
    if form.validate_on_submit():
        org.titulo=form.titulo.data
        org.descricao=form.descricao.data
        org.contato=form.contato.data
        org.status=form.status.data
        org.visibilidade=form.visibilidade.data
        org.logo_id=form.logo.data
        org.responsavel_id=request.form.get('responsavel')
        db.session.add(org)
        db.session.commit()
        flash('Congratulations, you edited your organization!')
        return redirect(url_for('.organizacao', orgname=str(org.titulo)))
    form.responsavel.process_data(org.responsavel.id)
    form.visibilidade.process_data(org.visibilidade)
    form.descricao.process_data(org.descricao)
    form.status.process_data(org.status)
    photoicon = Icons.query.filter( (Icons.icon_name=="org-"+str(org.id)) & (Icons.tipo=='logo')).first()
    return render_template('editorg.html', title='Editar Organização', form=form, photoicon=photoicon, org=org, icons=icons)

@app.route('/orgusers/<string:orgtit>', methods=['GET', 'POST'])
@login_required
def orgusers(orgtit):
    org = Orgs.query.filter(Orgs.titulo==orgtit).first()
    form = OrgusersForm()
    opcoes=[]
    for user in org.users:
        opcao =(user.id,user.nome+' '+user.sobrenome)  
        if user.id != org.responsavel:
            opcoes.append(opcao)
    #print(str(opcoes)+' com '+str(len(opcoes))+' itens')
    #if len(opcoes)==0:
    #    opcao =('0','Sem membros cadastrados')
    #    opcoes.append(opcao)
    form.excluidos.choices = opcoes
    if form.validate_on_submit():
        nome_conv=form.nome_convidado.data
        sobrenome_conv=form.sobrenome_convidado.data
        print ('valid')
        if nome_conv != "" or sobrenome_conv != "":
            newmember = Users.query.filter(and_(Users.nome == string.capwords(nome_conv), Users.sobrenome == string.capwords(sobrenome_conv))).first()
            if newmember == None:
                flash('Membro não encontrado no site!')
            else:
                if newmember in org.users:
                    flash('Usuário já é membro da '+{{ org.titulo }})
                else:
                    org.users.append(newmember)
                    db.session.commit()
                    flash( newmember.nome + ' ' +  newmember.sobrenome + ' cadastrado!')
                    form.nome_convidado.data = ''
                    form.sobrenome_convidado.data = ''
        excluir_ids = request.form.getlist('excluidos')
        #print('excluir_ids:'+ str(excluir_ids))
        if excluir_ids != []:
            for member_id in excluir_ids:
                member = Users.query.filter(Users.id == member_id).first()
                org.users.remove(member)
            db.session.commit()
        flash('Congratulations, you edited your organization!')
        opcoes=[]
        for user in org.users:
           opcao =(user.id,user.nome+' '+user.sobrenome)  
           if user.id != org.responsavel:
               opcoes.append(opcao)
        #if len(opcoes)==0:
        #   opcao =('0','Sem membros cadastrados')
        #   opcoes.append(opcao)
        form.excluidos.choices = opcoes
    return render_template('orgusers.html', title='Membros da Organização', form=form, org=org)

def permiteacesso(projid,permmin):
    proj = Projs.query.filter(Projs.id==projid).first()
    user = Users.query.filter(Users.username == current_user.username).first()
    reg = ProjsUsers.query.filter(and_(ProjsUsers.proj == proj,ProjsUsers.user == user)).first()
    #print ('reg:'+str(reg))
    if reg == None:
        flash('Acesso restrito. Status mínimo necessário: '+permmin)
        return(False)
    else:
        if permmin == 'responsável':
          if reg.status != 'responsável':
            return(False)
        if permmin == 'administrador':
            if reg.status != 'responsável' and reg.status != 'administrador':
                return(False)
        if permmin == 'editor':
            if reg.status != 'responsável' and reg.status != 'administrador' and reg.status != 'editor':
                return(False)   
    return(True)

def projuserlist(projid):
    lista0=[]
    lista1=[]
    opcao_resp=''
    print('projid:'+projid)
    proj = Projs.query.filter(Projs.id==projid).first()
    print('proj:'+str(proj))
    projusers = ProjsUsers.query.filter(ProjsUsers.proj == proj).all()
    print('projusers:'+str(projusers))
    for projuser in projusers:
        opcao0 =(projuser.user.id,projuser.user.nome+' '+projuser.user.sobrenome)
        opcao1 =(projuser.user.id, projuser.status+': '+projuser.user.nome+' '+projuser.user.sobrenome)
        if projuser.status == 'responsável':
            print('projuser.status:'+str(projuser.status))
            opcao_resp=opcao0
        else:
            lista0.append(opcao0)
            lista1.append(opcao1)
    lista0.sort(key=takeSecond)
    lista1.sort(key=takeSecond)
    print('lista0:'+str(lista0))
    print('lista1:'+str(lista1))
    print('opcao_resp:'+str(opcao_resp))
    return(lista0,lista1,opcao_resp)

@app.route('/projusers/<string:projid>', methods=['GET', 'POST'])
@login_required
def projusers(projid):
    if not(permiteacesso(projid,'administrador')):
        return redirect(url_for('.index'))
    #print ('user_status:'+str(user_status))
    user = Users.query.filter(Users.username == current_user.username).first()
    proj = Projs.query.filter(Projs.id == projid).first()
    projuser = ProjsUsers.query.filter(and_(ProjsUsers.proj == proj,ProjsUsers.user == user)).first()
    user_status = projuser.status
    form = ProjusersForm()
    opcoes_excluir=[]
    opcoes_editar=[]
    opcoes = projuserlist(projid)
    form.excluidos.choices = opcoes[0]
    form.editados.choices = opcoes[1]
    form.editadosresp.choices = opcoes[1]
    proj=Projs.query.filter(Projs.id==projid).first()
    opcoes_incluir=[]
    for org in proj.orgs:
        membros = org.users
        for membro in membros:
            opcao = (membro.id,org.titulo+': '+membro.nome+' '+membro.sobrenome)
            opcao_excluir = (membro.id,membro.nome+' '+membro.sobrenome)
            if membro != proj.responsavel:
                if not(opcao_excluir in opcoes_excluir):
                    opcoes_incluir.append(opcao)
            
    opcoes_incluir.sort(key=takeSecond)
    form.incluidos.choices = opcoes_incluir
    #form.incluidos.process_data(0)

    big = bigword(proj.titulo)
    if form.validate_on_submit():
        incluir_ids = request.form.getlist('incluidos')
        if incluir_ids != []:
            for newmember_id in incluir_ids:
                newmember = Users.query.filter(Users.id == newmember_id).first()
                oldmember= ProjsUsers.query.filter(and_(ProjsUsers.user == newmember,ProjsUsers.proj == proj)).first()
                if  oldmember == None:
                    a = ProjsUsers(status = "participante")
                    a.proj = proj
                    a.user = newmember
                    db.session.add(a) 
                    db.session.commit()
                    db.session.flush()
                    flash( newmember.nome + ' ' +  newmember.sobrenome + ' realmente incluido!')
                else:
                    flash(oldmember.user.nome + ' ' + oldmember.user.sobrenome +' realmente já participa do projeto')
        excluir_ids = request.form.getlist('excluidos')
        if excluir_ids != []:
            for member_id in excluir_ids:
                a = ProjsUsers.query.filter(and_(ProjsUsers.user_id == member_id,ProjsUsers.proj == proj)).first()
                db.session.delete(a)
                db.session.commit()
                excluido = Users.query.filter(Users.id == member_id).first()
                flash(excluido.nome + ' ' + excluido.sobrenome + ' excluido do projeto!')
        print ('user_status:'+user_status)
        if user_status == 'responsável':
            editar_ids = request.form.getlist('editadosresp')
        else:
            editar_ids = request.form.getlist('editados')
        print('editar_ids 1:'+str(editar_ids))
        lista=[]
        if editar_ids != []:
            if user_status == 'responsável' :
                newstatus = form.statusresp.data
            else:
                newstatus = form.status.data
            print ('newstatus:'+str(newstatus))
            if newstatus == None:
                flash ('Escolha um novo status para os participantes selecionados.')
            else:
                #Atualiza responsavel na tabela Projs
                if newstatus == 'responsável':
                    oldregstatus = reg.status
                    reg.status = 'administrador'
                    newuserresp = Users.query.filter(Users.id == editar_ids[0]).first()
                    proj.responsavel = newuserresp
                    db.session.add(proj)
                    db.session.add(reg)
                    db.session.commit()
                    flash (reg.user.nome+' '+reg.user.sobrenome+': '+oldregstatus+' -> '+reg.status)
                #Atualiza responsavel na tabela ProjsUSers
                print ('editar_ids:'+str(editar_ids))
                for member_id in editar_ids:
                    edituser = Users.query.filter(Users.id == member_id).first()
                    new = ProjsUsers.query.filter(and_(ProjsUsers.user == edituser,ProjsUsers.proj == proj)).first()
                    oldstatus = new.status
                    new.status = newstatus
                    flash (new.user.nome+' '+new.user.sobrenome+': '+oldstatus+' -> '+newstatus)
                    db.session.add(new)
                    lista.append(member_id)
                print('lista:'+str(lista))
                db.session.commit()
                #Atualiza opcoes do form select editados
        #nova_opcoes_editar=[]
        #for opcao in opcoes_editar:
        #    print('opcao[0]:'+str(opcao[0]))
        #    if str(opcao[0]) in lista:
        #        nova_opcoes_editar.append((opcao[0],newstatus+':'+opcao[1].split(':')[1]))
        #    else:
        #        nova_opcoes_editar.append(opcao)
        #print ('opcoes_editar:'+str(opcoes_editar))
        #print ('nova_opcoes_editar:'+str(nova_opcoes_editar))
        #opcoes_editar = nova_opcoes_editar
        #form.editados.choices = opcoes_editar
        #form.editadosresp.choices = opcoes_editar
        #return render_template('projusers.html', title='Membros da Organização', form=form, big=big, user_status=user_status, projeto=proj)
                   
    opcoes = projuserlist(projid)
    form.excluidos.choices = opcoes[0]
    form.editados.choices = opcoes[1]
    form.editadosresp.choices = opcoes[1]
    
    return render_template('projusers.html', title='Membros da Organização', form=form, big=big, user_status=user_status, projeto=proj)
    
@app.route('/organizacao/<string:orgname>', methods=['GET', 'POST'])
@login_required
def organizacao(orgname):
    org = Orgs.query.filter_by(titulo=orgname).first()
    if org:
        descricao = org.descricao
        if org.descricao:
            descricao = org.descricao.split('\n')
        else:
            descricao = " "
    else:
        flash('Organização não encontrada.')
        return redirect(url_for('.index'))
    return render_template('organizacao.html', title='Organização '+ org.titulo , org=org, \
                           descricao=descricao, icon_url=org.logo.icon_url, icon_name=org.logo.icon_name)

@app.route('/newtask/<string:proj>', methods=['GET', 'POST'])
@login_required
def newtask(proj):
    if not(permiteacesso(proj,'administrador')):
        return redirect(url_for('.index'))
    form = NewtaskForm()
    projeto = Projs.query.filter(Projs.id==proj).first()
    opcoes=[]
    opcao =(0,'Não Definido')
    opcoes.append(opcao)
    opcao =(projeto.responsavel.id,projeto.responsavel.nome+' '+projeto.responsavel.sobrenome)
    opcoes.append(opcao)
    for user in projeto.users:
      opcao =(user.id,user.nome+' '+user.sobrenome)  
      if not(opcao in opcoes):
        opcoes.append(opcao)
    form.responsavel.choices = opcoes
    form.responsavel.process_data(0)
    if form.validate_on_submit():
        newtask = Tasks(titulo=form.titulo.data,
                    descricao=form.descricao.data,
                    status="EM PROGRESSO",
                    proj_id = proj,
                    progresso = "0",
                    responsavel_id=request.form.get('responsavel'))
        db.session.add(newtask)
        db.session.commit()
        db.session.flush()
        proj_id=proj
        flash('Congratulations, your project has a new task.')
        #return redirect(url_for('.projeto/'+str(proj_id)))
        return redirect(url_for('.projeto', proj_id=str(proj_id)))
    
    return render_template('newtask.html', title='Nova Tarefa', projeto = projeto, form=form)


@app.route('/newstage/<string:proj>', methods=['GET', 'POST'])
@login_required
def newstage(proj):
    if not(permiteacesso(proj,'editor')):
        return redirect(url_for('.index'))
    form = NewstageForm()
    projeto = Projs.query.filter(Projs.id==proj).first()
    if form.validate_on_submit():
        newstage= Etapas(titulo=form.titulo.data,
                    body=form.body.data,
                    status="ATIVO",
                    proj_id = proj,
                    visibilidade=form.visibilidade.data)
        db.session.add(newstage)
        db.session.commit()
        db.session.flush()
        proj_id=proj
        flash('Congratulations, your project has a new stage.')
        #return redirect(url_for('.projeto/'+str(proj_id)))
        return redirect(url_for('.projeto', proj_id=str(proj_id)))
    form.visibilidade.default = 'RASCUNHO'
    form.visibilidade.process_data('RASCUNHO')
    
    return render_template('newstage.html', title='Nova Etapa', projeto = projeto, form=form)

@app.route('/editstage/<string:stage_id>', methods=['GET', 'POST'])
@login_required
def editstage(stage_id):

    form = NewstageForm()
    etapa = Etapas.query.filter(Etapas.id==stage_id).first()
    
    if etapa == None:
       flash('Etapa não localizada.')
       return redirect(url_for('.projeto', proj_id=str(projeto.id)))
    projeto = Projs.query.filter(Projs.id==etapa.proj_id).first()
    if not(permiteacesso(projeto.id,'editor')):
        return redirect(url_for('.index'))
    if form.validate_on_submit():
        etapa.titulo=form.titulo.data
        etapa.body=form.body.data
        etapa.visibilidade=form.visibilidade.data
        photo_ids = ""
        if form.imagens.data != "":
            photo_ids = form.imagens.data.strip().split(' ')
            for photo_id in photo_ids:
                photo = Icons.query.filter(Icons.id == photo_id).first()
                etapa.photos.append(photo)
        flash ('Etapa '+str(etapa.id)+' '+etapa.titulo)
        flash (etapa.body)
        flash (etapa.visibilidade)
        db.session.add(etapa) 
        db.session.commit()
        flash('Etapa editada.')
        #return redirect(url_for('.projeto/'+str(proj_id)))
        return redirect(url_for('.projeto', proj_id=str(projeto.id)))
        form.responsavel.process_data(org.responsavel.id)
    form.visibilidade.process_data(etapa.visibilidade)
    form.body.process_data(etapa.body)
    form.titulo.process_data(etapa.titulo)
    photos=etapa.photos
    contador = 0
    for p in photos:
        contador = contador + 1
    
    return render_template('editstage.html', title='Editar Etapa', projeto = projeto, form=form, etapa=etapa, photos=photos, contador=contador)

@app.route('/newmsg/<string:destid>', methods=['GET', 'POST'])
@login_required
def newmsg(destid=''):
    form = MsgForm()
    destinos = Users.query.all()
    user = Users.query.filter(Users.id == current_user.id).first()
    opcoes=[]
    if destid!='':
        destino1 = Users.query.filter(Users.id == destid).first()
        opcao =(destino1.id,destino1.nome+' '+destino1.sobrenome)
        opcoes.append(opcao)
    else:
        for destino in destinos:
          if (destino.id != user.id):  
            opcao =(destino.id,destino.nome+' '+destino.sobrenome)  
            if not(opcao in opcoes):
              opcoes.append(opcao)
    form.destination.choices = opcoes
    if destid!='':
        form.destination.process_data(str(destino1.id))
    else:
        form.destination.process_data(0)
    if form.validate_on_submit():
        destination_ids = request.form.getlist('destination')
        print('destination_ids:'+str(destination_ids))
        newmsg = Msgs(body = form.body.data,
                      tipo = 'USER_MSG',
                      origin_id = user.id)
        db.session.add(newmsg)
        db.session.commit()
        db.session.flush()
        a = UsersMsgs(status = "new", autor=user.username,msg = newmsg,user = user)
        db.session.add(a) 
        db.session.commit()
        db.session.flush()
        msg_id=newmsg.id
        for dst_id in destination_ids:
            destination = Users.query.filter(Users.id == dst_id).first()
            if destination != user:
                b = UsersMsgs(status = "new",
                          autor=user.username,
                          msg = newmsg,
                          user = destination)
                db.session.add(b) 
                db.session.commit()
                db.session.flush()
        print('Mensagem nova')
        print(str(newmsg.users))
        print(str(user.msgs))
        flash('Mensagem enviada.')
        #return redirect(url_for('.projeto/'+str(proj_id)))
        return redirect(url_for('.index'))
    
    return render_template('newmsg.html', title='Enviar Mensagem', form=form)

@app.route('/replymsg/<string:old_msg_id>', methods=['GET', 'POST'])
@login_required
def replymsg(old_msg_id):
    form = MsgForm()
    old_msg = Msgs.query.filter(Msgs.id == old_msg_id ).first()
    destination = Users.query.filter(Users.id == old_msg.origin_id).first()
    user = Users.query.filter(Users.id == current_user.id).first()
    if form.validate_on_submit():
        newmsg = Msgs(body = form.body.data,
                    tipo = 'USER_MSG',
                    origin_id = user.id)
        db.session.add(newmsg)
        db.session.commit()
        db.session.flush()
        
        a = UsersMsgs(status = "new", autor=user.username)
        a.msg = newmsg
        a.user = user
        db.session.add(a) 
        db.session.commit()
        msg_id=newmsg.id
        a = UsersMsgs(status = "new", autor=user.username)
        a.msg = newmsg
        a.user = destination
        db.session.add(a) 
        db.session.commit()
        flash('Mensagem enviada.')
        #return redirect(url_for('.projeto/'+str(proj_id)))
        return redirect(url_for('.index'))
    
    return render_template('replymsg.html', title='Enviar Mensagem', old_msg=old_msg, destination=destination, form=form)



@app.route('/edittask/<string:proj>/<string:task>', methods=['GET', 'POST'])
@login_required
def edittask(proj,task):
    if not(permiteacesso(proj,'participante')):
        return redirect(url_for('.index'))
    form = EdittaskForm()
    projeto = Projs.query.filter(Projs.id==proj).first()
    tarefa = Tasks.query.filter(Tasks.id==task).first()
    
    opcoesresp=[]
    opcao1 =(0,'Não Definido')
    opcoesresp.append(opcao1)
    opcoes = projuserlist(proj)
    opcoesresp.append(opcoes[2])
    opcoesresp = opcoesresp + opcoes[0]
    form.responsavel.choices = opcoesresp
    print ('opcoes:'+str(opcoesresp))
    #opcoes=[]
    #opcao =(0,'Não Definido')
    #opcoes.append(opcao)
    #opcao =(projeto.responsavel.id,projeto.responsavel.nome+' '+projeto.responsavel.sobrenome)
    #opcoes.append(opcao)    
    #for user in projeto.users:
    #  opcao =(user.id,user.nome+' '+user.sobrenome)  
    #  if not(opcao in opcoes):
    #    opcoes.append(opcao)
    #form.responsavel.choices = opcoes
    
    form.responsavel.process_data(tarefa.responsavel_id)
    
    if form.validate_on_submit():
        print("form.responsavel.data:"+form.responsavel.data)
        print("int(form.responsavel.data):"+str(int(form.responsavel.data)))
        tarefa.titulo=form.titulo.data
        tarefa.descricao=form.descricao.data
        tarefa.progresso=int(form.prog.data)
        tarefa.responsavel_id=request.form.get('responsavel')
        print ("tarefa.responsavel_id=request.form.get('responsavel') :"+tarefa.responsavel_id)
        if int(form.prog.data) >= 100:
            tarefa.status="COMPLETA"
        else:
            if tarefa.responsavel_id == "0":
                tarefa.status="NÃO ATRIBUIDA"
            else:
                if tarefa.progresso == 0:
                    tarefa.status="ATIVA"
                else:
                    tarefa.status="EM PROGRESSO"
        db.session.add(tarefa)
        db.session.commit()
        flash('Congratulations, your task was updated.')
        #return redirect(url_for('.projeto/'+str(proj_id)))
        return redirect(url_for('.task', proj=str(proj), task=str(task)))
    form.descricao.process_data(tarefa.descricao)
    form.prog.process_data(tarefa.progresso)
    return render_template('edittask.html', title='Editar Tarefa', projeto = projeto, tarefa=tarefa, form=form)

@app.route('/task/<string:proj>/<string:task>', methods=['GET', 'POST'])
@login_required
def task(proj,task):
    projeto = Projs.query.filter(Projs.id==proj).first()
    tarefa = Tasks.query.filter(Tasks.id==task).first()
    responsavel = Users.query.filter(Users.id==tarefa.responsavel_id).first()
    descricao = tarefa.descricao
    if tarefa.descricao:
        descricao = tarefa.descricao.split('\n')
    else:
        descricao = " "    
    return render_template('task.html', title='Tarefa', projeto = projeto, tarefa = tarefa, descricao=descricao, responsavel = responsavel)

@app.route('/deltask/<string:proj>/<string:task>', methods=['GET', 'POST'])
@login_required
def deltask(proj,task):
    if not(permiteacesso(proj,'administrador')):
        return redirect(url_for('.index'))
    projeto = Projs.query.filter(Projs.id==proj).first()
    tarefa = Tasks.query.filter(Tasks.id==task).first()
    responsavel = Users.query.filter(Users.id==tarefa.responsavel_id).first()
    descricao = tarefa.descricao
    if tarefa.descricao:
        descricao = tarefa.descricao.split('\n')
    else:
        descricao = " "    
    return render_template('deltask.html', title='Apagar Tarefa', projeto = projeto, tarefa = tarefa, descricao=descricao, responsavel = responsavel)

@app.route('/delstage/<string:stage_id>', methods=['GET', 'POST'])
@login_required
def delstage(stage_id):
    etapa = Etapas.query.filter(Etapas.id==stage_id).first()
    projeto = Projs.query.filter(Projs.id==etapa.proj_id).first()
    if not(permiteacesso(projeto.id,'editor')):
        return redirect(url_for('.index'))
    return render_template('delstage.html', title='Apagar Etapa', projeto = projeto, etapa = etapa)


@app.route('/delorg/<string:org_id>', methods=['GET', 'POST'])
@login_required
def delorg(org_id):
    org = Orgs.query.filter(Orgs.id==org_id).first()
    if org.responsavel.username != current_user.username:
        flash('Ação não autorizada.')
        return redirect(url_for('.index'))
    ativproj = False
    for orgproj in org.projs:
        print ('Projeto:'+str(orgproj.id))
        if orgproj.status == "ATIVO":
            ativproj = True
    if ativproj:
        flash('Existem projetos ativos nesta Organização.')
        return redirect(url_for('.index'))
    return render_template('delorg.html', title='Deletar Organização?', org = org)

@app.route('/delproj/<string:proj_id>', methods=['GET', 'POST'])
@login_required
def delproj(proj_id):
    if not(permiteacesso(proj_id,'responsável')):
        return redirect(url_for('.index'))
    proj = Projs.query.filter(Projs.id==proj_id).first()
    if proj.responsavel.username != current_user.username:
        flash('Ação não autorizada.')
        return redirect(url_for('.index'))
    if proj.status == "ATIVO":
        flash('Este projeto está com status ativo.')
        return redirect(url_for('.index'))
    return render_template('delproj.html', title='Deletar Projeto?', proj = proj)

@app.route('/deltaskconfirmed/<string:proj>/<string:task>', methods=['GET', 'POST'])
@login_required
def deltaskconfirmed(proj,task):
    if not(permiteacesso(proj,'administrador')):
        return redirect(url_for('.index'))
    tarefa = Tasks.query.filter(Tasks.id==task).first()
    db.session.delete(tarefa)
    db.session.commit() 
    flash('Tarefa apagada.')
    projeto = Projs.query.filter(Projs.id==proj).first()
    tasks = Tasks.query.filter(Tasks.proj_id==proj).all()
    descricao = projeto.descricao
    if projeto.descricao:
        descricao = projeto.descricao.split('\n')
    else:
        descricao = " "        
    return redirect(url_for('.projeto', proj_id=str(projeto.id)))

@app.route('/contribuicao', methods=['GET', 'POST'])
@login_required
def contribuicao():
    return render_template('contribuicao.html', title='contribuicao')

@app.route('/concluido', methods=['GET', 'POST'])
@login_required
def concluido():
    user = Users.query.filter(Users.id == current_user.id).first()
    msgs = user.msgs
    newmsgs = []
    for m in msgs:
        if m.status == "new":
            newmsgs.append(m)
            m.status = "old"
            db.session.add(m)
            db.session.commit()
    return render_template('concluido.html', title='concluido', msgs=msgs, newmsgs=newmsgs, user=user, hora=datetime.utcnow())

@app.route('/processando', methods=['GET', 'POST'])
@login_required
def processando():
    user = Users.query.filter(Users.id == current_user.id).first()
    msgs = user.msgs
    newmsgs = []
    for m in msgs:
        if m.status == "new":
            newmsgs.append(m)
            m.status = "old"
            db.session.add(m)
            db.session.commit()
    return render_template('processando.html', title='processando', msgs=msgs, newmsgs=newmsgs, user=user, hora=datetime.utcnow())

@app.route('/delimage/<string:etapaid>/<string:imageid>', methods=['GET', 'POST'])
@login_required
def delimage(etapaid,imageid):
    etapa = Etapas.query.filter(Etapas.id==etapaid).first()
    projeto = Projs.query.filter(Projs.id==etapa.proj_id).first()
    if not(permiteacesso(projeto.id,'editor')):
        return redirect(url_for('.index'))
    image = Icons.query.filter(Icons.id==imageid).first()
    if image:
        db.session.delete(image)
        db.session.commit()
        flash('Imagem apagada ('+str(imageid)+').')
    else:
        flash('Imagem não encontrada ('+str(imageid)+').')
     
    return redirect(url_for('.editstage', stage_id=etapaid))

@app.route('/delstageconfirmed/<string:stage_id>', methods=['GET', 'POST'])
@login_required
def delstageconfirmed(stage_id):

    etapa = Etapas.query.filter(Etapas.id==stage_id).first()
    projeto = Projs.query.filter(Projs.id==etapa.proj_id).first()
    if not(permiteacesso(projeto.id,'editor')):
        return redirect(url_for('.index'))
    db.session.delete(etapa)
    db.session.commit() 
    flash('Etapa apagada.')
    tasks = Tasks.query.filter(Tasks.proj_id==projeto.id).all()
    descricao = projeto.descricao
    if projeto.descricao:
        descricao = projeto.descricao.split('\n')
    else:
        descricao = " "        
    return redirect(url_for('.projeto', proj_id=str(projeto.id)))

@app.route('/delorgconfirmed/<string:org_id>', methods=['GET', 'POST'])
@login_required
def delorgconfirmed(org_id):
    org = Orgs.query.filter(Orgs.id==org_id).first()
    if org.responsavel.username != current_user.username:
        flash('Somente o responsável pela organização pode executar essa ação.')
        return redirect(url_for('.organizacao', orgname=str(org.titulo)))
    db.session.delete(org)
    db.session.commit() 
    flash('Organização apagada.')
    return redirect(url_for('.listorgs', orgname=str(org.titulo)))

@app.route('/delprojconfirmed/<string:proj_id>', methods=['GET', 'POST'])
@login_required
def delprojconfirmed(proj_id):
    if not(permiteacesso(proj_id,'responsável')):
        return redirect(url_for('.index'))
    print ('Del Projeto: Confirmado proj '+str(proj_id))
    proj = Projs.query.filter(Projs.id==proj_id).first()
    if proj.responsavel.username != current_user.username:
        flash('Somente o responsável pelo projeto pode executar essa ação.')
        return redirect(url_for('.projeto', proj_id=str(proj.id)))
    for etapa in proj.etapas:
        print ('Del Projeto: Excluindo etapa '+str(etapa.id))
        stage = Etapas.query.filter(Etapas.id==etapa.id).first()
        for photo in etapa.photos :
            print ('Del Projeto: Excluindo Foto '+str(photo.id))
            foto = Icons.query.filter(Icons.id==photo.id).first()
            db.session.delete(foto)
            db.session.commit()
        db.session.delete(etapa)
        db.session.commit()
    db.session.delete(proj)
    db.session.commit() 
    flash('Projeto apagado.')
    return redirect(url_for('.listproj'))

   
@app.route('/newproj', methods=['GET', 'POST'])
@login_required
def newproj():
    global user_atual
    proj_id="0"
    form = NewprojForm()
    user = Users.query.filter(Users.username == current_user.username).first()
    responsavel=user.nome+' '+user.sobrenome
    form.organizacao.choices = get_organizacao()
    msg="Escolha uma organização da qual você faz parte."
    if len(form.organizacao.choices)==1:
        msg="SEM ORGANIZAÇÕES"
    print("a:"+str(form.responsavel.data))
    choices = get_responsavel(user)
    form.responsavel.choices = choices
    form.responsavel.default = choices[0][0]
    form.responsavel.process_data(choices[0][0])
    print("b:"+str(form.responsavel.data))
    id_list=['1']
    icons = Icons.query.filter(and_( Icons.criador_id.in_(id_list,) ,  Icons.tipo == 'icon')).all()
    icon = Icons.query.filter(Icons.id=='10').first()
    if form.validate_on_submit():
        newp = Projs(status=form.status.data,
                     titulo=form.titulo.data,
                     descricao=form.descricao.data,
                     objetivo=form.objetivo.data,
                     visibilidade=form.visibilidade.data,
                     responsavel_id=form.responsavel.data,
                     icon_id=form.icon.data
                     )
        print("c:"+str(form.responsavel.data))
        db.session.add(newp)
        db.session.commit()
        db.session.flush()
        proj_id=newp.id
        user_resp = Users.query.filter(Users.id==form.responsavel.data).first()
        org_id = form.organizacao.data
        org = Orgs.query.filter(Orgs.id==org_id).first()
        newp.orgs.append(org)
        newp.users.append(user_resp)
        db.session.add(newp)
        db.session.commit()
        db.session.flush()
        iconproj = Icons.query.filter(Icons.id==newp.icon_id).first()
        iconproj.icon_name = "projeto-" + str(proj_id)
        db.session.add(iconproj)
        db.session.commit()
        flash('Congratulations, you have a new project!')
        return redirect(url_for('.projeto', proj_id=str(proj_id)))
    
    
    print("d:"+str(form.responsavel.data))
    photoicon = 'https://www.vamostrabalharjuntos.com.br/projetos/static/images/unnamed.png'
    return render_template('newproj.html', title='Novo Projeto', icons=icons, msg=msg, form=form, responsavel=responsavel,\
                           icon=icon, photoicon=photoicon)

@app.route('/user/<string:username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = Users.query.filter(Users.username==username).first()
    return render_template('user.html', title="Perfil de "+username, user=user)

@app.route('/projeto/<string:proj_id>', methods=['GET', 'POST'])
@login_required
def projeto(proj_id):
    projeto = Projs.query.filter(Projs.id==proj_id).first()
    tasks = Tasks.query.filter(Tasks.proj_id==proj_id).all()
    etapas = Etapas.query.filter(Etapas.proj_id==proj_id).all()
    big = bigword(projeto.titulo)
    proj_user = ProjsUsers.query.filter(and_(ProjsUsers.proj == projeto,ProjsUsers.user == current_user)).first()
    if proj_user != None:
        user_status = proj_user.status
    else:
        user_status = 'visitante'
    print ('user_status:'+str(user_status))
    return render_template('projeto.html', title=projeto.titulo, big=big, projeto=projeto, tasks=tasks, etapas=etapas, user_status=user_status)

@app.route('/editproj/<string:proj_id>', methods=['GET', 'POST'])
@login_required
def editproj(proj_id):
    if not(permiteacesso(proj_id,'administrador')):
        return redirect(url_for('.index'))
    projeto = Projs.query.filter(Projs.id==proj_id).first()
    form = EditprojForm()
    oldreg = ProjsUsers.query.filter(and_(ProjsUsers.status == 'responsável', ProjsUsers.proj == projeto)).first()
    print('oldreg:'+str(oldreg))
    projresp = Users.query.filter(Users.id == projeto.responsavel_id).first()
    if oldreg == None:
        a = ProjsUsers(user = projresp, proj = projeto, status = 'responsável')
        db.session.add(a)
        db.session.commit()
        flash('responsável do projeto corrigido.')
    org_choices = get_organizacao(current_user)
    form.organizacao.choices = org_choices
    #print('++++++++++++++++++++++++')
    #print('choices: '+str(org_choices))
    #print('++++++++++++++++++++++++')
    #print('projeto.orgs.first():'+str(projeto.orgs.first()))
    if projeto.orgs.first() == None:
        form.organizacao.process_data(int(org_choices[0][0]))
        #print('int(org_choices[0][0]):'+str(int(org_choices[0][0])))
    else:
        form.organizacao.process_data(int(projeto.orgs.first().id))
        #print('int(projeto.orgs.first().id):'+str(int(projeto.orgs.first().id)))
    #form.organizacao.process_data(int(proj_id))
    msg="Escolha uma organização da qual você faz parte."
    
    opcoes_resp=[]
    projusers = ProjsUsers.query.filter(ProjsUsers.proj == projeto).all()
    for projuser in projusers:
        opcao =(projuser.user.id,projuser.user.nome+' '+projuser.user.sobrenome)
        if projuser.user != projeto.responsavel:
            opcoes_resp.append(opcao)
    opcoes_resp.sort(key=takeSecond)
    form.responsavel.choices = opcoes_resp
    form.responsavel.process_data(projeto.responsavel.id)

    #form.responsavel.process_data(1)
    #form.responsavel.default = 1
    #form.organizacao.default = int(proj_id)
    id_list=['1',current_user.id]
    icons = Icons.query.filter(and_( Icons.criador_id.in_(id_list,) ,  Icons.tipo == 'icon')).all()
    #icon = Icons.query.filter(Icons.id=='10').first()
    photoicon = Icons.query.filter( (Icons.icon_name=="projeto-"+proj_id) & (Icons.tipo=='projicon')).first()
    if projeto.orgs.first() != None:
        #print("projeto.orgs:"+str(projeto.orgs.first()))
        #print("projeto.orgs.id:"+str(projeto.orgs.first().id))
        pass
    if form.validate_on_submit():
        projeto.titulo=form.titulo.data
        projeto.descricao=form.descricao.data
        projeto.objetivo=form.objetivo.data
        projeto.status=form.status.data
        projeto.visibilidade=form.visibilidade.data
        projeto.icon_id=form.icon.data
        org = request.form.get('organizacao')
        #oldresp_id = projeto.responsavel_id
        oldreg = ProjsUsers.query.filter(and_(ProjsUsers.status == 'responsável', ProjsUsers.proj == projeto)).first()
        resp=request.form.get('responsavel')
        if resp != None:
          projeto.responsavel_id=resp
          newresp = Users.query.filter(Users.id == projeto.responsavel_id).first()
          newreg = ProjsUsers.query.filter(ProjsUsers.user == newresp).first()
          if newreg == None:
              newreg = ProjsUsers(user = newresp, proj = projeto)
          if oldreg == None:
            newreg.status = 'responsável'
            db.sesson.add(newreg)
            db.session.commit()
            flash('correção: '+newresp.nome + ' ' +  newresp.sobrenome + ' agora responsável do projeto')  
          else:
            if oldreg.user.id != newresp.id:
              oldreg.status = 'participante'
              newreg.status = 'responsável'
              db.session.add(oldreg)
              db.session.add(newreg)
              db.session.add(projeto)
              db.session.commit()
              flash(newresp.nome + ' ' +  newresp.sobrenome + ' agora responsável do projeto')
        #print('form.organizacao.data:'+str(form.organizacao.data))
        print('form.status.data: '+str(form.status.data))
        print('form.visibilidade.data: '+str(form.visibilidade.data))
        if org:
            #print('***************************')
            #print("org:"+str(org))
            for o in projeto.orgs.all():
                #print('***************************')
                #print ('o:'+str(o))
                projeto.orgs.remove(o)
            org_reg = Orgs.query.filter( Orgs.id==org ).first()
            projeto.orgs.append(org_reg)
        db.session.add(projeto)
        db.session.commit()
        db.session.flush()
        flash('Congratulations, you edited the project!')
        return redirect(url_for('.projeto', proj_id=str(proj_id)))
    form.status.default = projeto.status
    form.status.process_data(projeto.status)
    form.visibilidade.default = projeto.visibilidade
    form.visibilidade.process_data(projeto.visibilidade)
    form.descricao.process_data(projeto.descricao)
    return render_template('editproj.html', title='Editar Projeto', icons=icons, msg=msg, form=form, projeto=projeto)


@app.route('/lista_de_projetos', methods=['GET', 'POST'])
@login_required
def listproj():
    user = Users.query.filter(Users.username==current_user.username).first()
    projetos = ProjsUsers.query.filter(ProjsUsers.user==user).all()
    outros=[]
    for p in user.projs.all():
        for porg in p.orgs.all():
            if user in porg.users.all():
                pass
                #flash(user.nome+' '+user.sobrenome+'('+str(user.id)+') em '+porg.titulo)
            else:
                porg.users.append(user)
                db.session.commit()
                db.session.flush()
                #flash('Ops, '+user.nome+' '+user.sobrenome+'('+str(user.id)+') agora em '+porg.titulo)
    for p in Projs.query.all():
        outro = True
        for o in user.orgs:
            if o in p.orgs:
                outro = False
        if outro:
          outros.append(p)
    outrosprojs = outros
    return render_template('lista_de_projetos.html', user=user, outrosprojs=outrosprojs, projetos=projetos, title='Lista de Projetos')

@app.route('/lista_de_organizacoes', methods=['GET', 'POST'])
@login_required
def listorgs():
    user = current_user
    outras=[]
    public = "PÚBLICO"
    user_orgs = []
    for u in user.orgs:
        user_orgs.append(u.id)
    for org in Orgs.query.all():
        if not(org.id in user_orgs):
            if org.visibilidade == public:
                outras.append(org.id)
    outrasorgs = Orgs.query.filter( Orgs.id.in_(outras,)).all()
    return render_template('lista_de_organizacoes.html', user=user, outrasorgs=outrasorgs, title='Lista de Organizações')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.imagem.data)
        #print('filename: '+filename)
        file_url = photos.url(filename)
        #print('file_url: '+file_url)
        tempo = strftime("%Y%m%d-%H%M%S", gmtime())
        newicon = Icons(icon_url = file_url,
                        icon_name = current_user.username+'-'+tempo+'-'+filename,
                        criador_id = current_user.id,
                        tipo = 'avatar')
        db.session.add(newicon)
        db.session.commit()
        db.session.flush()
        icon_id=newicon.id
        url = file_url.split('http://')[-1]
        flash('Congratulations, you uploaded the image!')
        flash(url_for('.edit', url=url))
        return redirect(url_for('.edit', url=url))
    
    return render_template('upload.html', form=form)

@app.route('/edit/<path:url>', methods=['GET', 'POST'])
def edit(url):
    return render_template('edit.html', url=url)

@app.route('/edit2', methods=['GET', 'POST'])
def edit2():
    return render_template('edit2.html')

@app.route('/teste', methods=['GET', 'POST'])
def teste():
    return render_template('teste.html')

@app.route('/save', methods=['GET', 'POST'])
def save():
    
    url = "https://vamostrabalharjuntos.com.br/"
    path = "uploads/"
    subdir = ""
    filename = ""
    my_file = ""
    #print ("THIS_FOLDER:"+THIS_FOLDER)
    if request.method == "POST":
        data = {}    # empty dict to store data
        data['imageId'] = request.json['imageId']
        data['data'] = request.json['imageData']
        data['dataType'] = request.json['imageType']
        data['username'] = request.json['username']
        data['tipo'] = request.json['tipo']
        data['icon_name'] = request.json['icon_name']
        tempo = strftime("%Y%m%d-%H%M%S", gmtime())
        filename = data['username'] + '-' + tempo + '-image'+ data['dataType']
        if data['tipo'] == "avatar":
            subdir = "avatar/"
        elif data['tipo'] == "photo":
            inf = data['icon_name'].split('-')
            subdir = "projeto-"+inf[1]+"/"+data['icon_name']+"/"
        elif data['tipo'] == "projicon":
            subdir = data['icon_name']+"/"
        elif data['tipo'] == "logo":
            subdir = "logo/"
        fullpath = os.path.join(THIS_FOLDER, path+subdir)
        my_file = fullpath+filename
        print("path: "+path+"   subdir: "+subdir+"   path/subdir: "+path+subdir+"  OK1")
        print("fullpath: "+fullpath)
        print("my_file: "+my_file)
        base64_img_bytes = data['data'].encode('utf-8')
        if not os.path.exists(fullpath):
            os.makedirs(fullpath, mode=0o666)
        f = open(my_file, 'wb')
        decoded_image_data = base64.decodebytes(base64_img_bytes)
        f.write(decoded_image_data)
        f.close()
        url_my_file = url+path+subdir+filename
        print("data['username']:"+data['username'])
        user = Users.query.filter(Users.username == data['username']).first()
        print("-----------------------------------")
        print("data['icon_name'] "+str(data['icon_name']))
        print("data['tipo'] "+str(data['tipo']))
        print("-----------------------------------")
        if data['tipo'] != "avatar":
            iconuser = Icons.query.filter(Icons.icon_name==data['icon_name']).first()
        else:
            iconuser = Icons.query.filter(Icons.criador_id==user.id).first()
        print("iconuser:"+str(iconuser))
        print("url_my_file:"+url_my_file)
        if iconuser != None:
            iconuser.criador_id = user.id 
            iconuser.tipo = data['tipo']
            iconuser.icon_url = url_my_file
            iconuser.icon_name = data['icon_name']
            db.session.add(iconuser)
            db.session.commit()
            icon_id = iconuser.id
        else:
            newicon = Icons(icon_url = url_my_file,
                        icon_name = data['icon_name'],
                        criador_id = user.id,
                        tipo = data['tipo'])
            db.session.add(newicon)
            db.session.commit()
            db.session.flush()
            icon_id=newicon.id
        flash(url_my_file+ ' foi salvo!')
        print(url_my_file+ ' foi salvo!')
        resposta = jsonify ( url = url_my_file, id = icon_id )
        print(resposta)
        return (resposta)
    return render_template('save.html', arquivo = filename , url = my_file)

def sendmsg(dest,origin,tex,tip):
    newmsg = Msgs(body = tex,
                  tipo = tip,
                  origin_id = origin.id)
    db.session.add(newmsg)
    db.session.commit()
    db.session.flush()
    a = UsersMsgs(status = "new", autor=origin.username)
    a.msg = newmsg
    a.user = origin
    db.session.add(a) 
    db.session.commit()
    a = UsersMsgs(status = "new", autor=origin.username)
    a.msg = newmsg
    a.user = destination
    db.session.add(a) 
    db.session.commit()
    return

def create_users(count=40):
    fake = Faker('pt_BR')
    i = 20
    while (i < count):
        u = Users(email = fake.email(),
                username = fake.user_name(),
                password = "password",
                confirmed = "True",
                nome = first_name(),
                sobrenome = last_name())
        db.session.add(u)
        db.session.commit()
    return

def fake_msgs(count=100):
    fake = Faker('pt_BR')
    i = 20
    while (i < count):
        u = Users(email = fake.email(),
                username = fake.user_name(),
                password = "password",
                confirmed = "True",
                nome = first_name(),
                sobrenome = last_name())
        db.session.add(u)
        db.session.commit()
    return    
    
if __name__ == "__main__":
    #app.run(ssl_context=('/etc/letsencrypt/live/vamostrabalharjuntos.com.br/fullchain.pem', '/etc/letsencrypt/live/vamostrabalharjuntos.com.br//privkey.pem'))
    #app.run(ssl_context='adhoc',host= '0.0.0.0')
    app.run()
