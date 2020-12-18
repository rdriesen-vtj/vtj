#!/bin/python
# -*- coding: utf-8 -*-
import os
import base64
import json
import string
import logging
from time import gmtime, strftime
from datetime import datetime
from flask import Flask, render_template, flash, redirect, request, url_for, jsonify, logging as flog
from config import Config
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from threading import Thread
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.urls import url_parse
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from random import randint
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from faker import Faker
from flask_mail import Mail, Message

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
DEBUG = True


def create_app(config_name):
    login_manager.init_app(app)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads') # you'll need to create a folder named uploads
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'contato.vtj@gmail.com'
app.config['MAIL_PASSWORD'] = 'Rtdqxj00'
#app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
#app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Vamos Trabalhar Juntos]'
app.config['FLASKY_MAIL_SENDER'] = 'contato.vtj@gmail.com'
app.config['FLASKY_ADMIN'] = 'contato.vtj@gmail.com'   
#app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')          
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
moment = Moment(app)

from forms import LoginForm, RegistrationForm, Registration2Form, NewprojForm, EditprojForm, OrgusersForm, ProjusersForm,\
                  NewtaskForm, EdittaskForm, ProfileForm, OrgcreateForm, EditorgForm, UploadForm, MsgForm,\
                  PasswordResetRequestForm, PasswordResetForm, ChangePasswordForm, EnderecoForm

from models import Posts, Users, Orgs, Tasks, Projs, Icons, Msgs, UsersMsgs, Etapas

from forms import  TestForm, NewstageForm

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

def bigword(frase):
    big = False
    palavras = frase.split(" ")
    for palavra in palavras:
        if len(palavra) > 10:
            big = True
    return (big)

def get_responsavel(user,org=0):
    if org!=0:
        q = org.users.all()
        opcoes=[]
        opcao =(user.id,user.nome+' '+user.sobrenome)
        opcoes.append(opcao)
        #print("---get_responsavel---------------------------------------")
        #print (q)
        for user in q:
          if user.id != user.id:
            opcao =(int(user.id),user.nome+' '+user.sobrenome)  
            opcoes.append(opcao)  
            #print (str(opcoes))
            #print("---------------------------------------------------------")
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
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
   
@app.route('/logout')
def logout():
    logout_user()
    print (url_for('index'))
    return redirect(url_for('index'))
   
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data,
                     nome=form.nome.data,
                     sobrenome=form.sobrenome.data,
                     telefone=form.telefone.data,
                     email=form.email.data,
                     avatar_id = "12")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'Confirme sua conta',
                   'email/confirm', user=user, token=token)
        flash('Um email de confirmação foi enviado para seu email.')
        return redirect(url_for('index'))        
        #return redirect(url_for('register2', username=user.username))
    icons = Icons.query.filter_by(tipo='avatar').all()
    avatar = Icons.query.filter_by(id='12').first()
    return render_template('register.html', title='Register', form=form)
    #return render_template('register.html', title='Register', form=form)

@app.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('Sua conta foi confirmada.')
    else:
        flash('O link de confirmação é inválido ou expirou.')
    return redirect(url_for('index'))

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
        return redirect(url_for('login'))
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
            return redirect(url_for('index'))
        else:
            flash('Senha inválida.')
    return render_template("change_password.html", form=form)

@app.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset de sua senha',
                       'email/reset_password',
                       user=user, token=token)
        flash('Enviamos um email com instruções para o reset de sua senha.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form)

@app.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        #user = Users.query.filter_by(email=form.email.data.lower()).first()
        #user = Users.query.filter_by(Users.username==current_user.username).first()
        if Users.reset_password(token, form.password.data):
            db.session.commit()
            flash('Sua senha foi alterada.')
            return redirect(url_for('login'))
        else:
            return redirect(url_for('index'))
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
        return redirect(url_for('profile'))
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
        return redirect(url_for('profile'))
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
    icon = Icons.query.filter(Icons.id=='10').first()
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
        return redirect(url_for('organizacao', orgname=str(neworg.titulo)))
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
        return redirect(url_for('organizacao', orgname=str(org.titulo)))
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

@app.route('/projusers/<string:projtit>', methods=['GET', 'POST'])
@login_required
def projusers(projtit):
    proj = Projs.query.filter(Projs.titulo==projtit).first()
    form = ProjusersForm()
    if proj.responsavel.id == current_user.id:
        proj.users.append(current_user)
        db.session.commit()
        db.session.flush()
        flash(current_user.nome + ' ' + current_user.sobrenome + ' agora no projeto.')
    opcoes=[]
    for org in proj.orgs:
        membros = org.users
        for membro in membros:
            opcao = (membro.id,org.titulo+': '+membro.nome+' '+membro.sobrenome)  
            if membro != proj.responsavel:
                if not(membro in proj.users):
                    opcoes.append(opcao)
        #if len(opcoes)==0:
        #   opcao =('0','Sem membros cadastrados')
        #   opcoes.append(opcao)
    form.incluidos.choices = opcoes
    
    opcoes=[]
    for user in proj.users:
        opcao =(user.id,user.nome+' '+user.sobrenome)  
        if user != proj.responsavel:
            opcoes.append(opcao)
    #print(str(opcoes)+' com '+str(len(opcoes))+' itens')
    #if len(opcoes)==0:
    #    opcao =('0','Sem membros cadastrados')
    #    opcoes.append(opcao)
    form.excluidos.choices = opcoes
    big = bigword(proj.titulo)
    if form.validate_on_submit():
        print ('valid')
        incluir_ids = request.form.getlist('incluidos')
        #print('excluir_ids:'+ str(excluir_ids))
        if incluir_ids != []:
            for newmember_id in incluir_ids:
                newmember = Users.query.filter(Users.id == newmember_id).first()
                if newmember in proj.users:
                  flash('Usuario ja participa do projeto')
                else:
                  proj.users.append(newmember)
                  db.session.commit()
                  db.session.flush()
                  flash( newmember.nome + ' ' +  newmember.sobrenome + ' incluido!')
            db.session.commit()
                  
        excluir_ids = request.form.getlist('excluidos')
        #print('excluir_ids:'+ str(excluir_ids))
        if excluir_ids != []:
            for member_id in excluir_ids:
                member = Users.query.filter(Users.id == member_id).first()
                proj.users.remove(member)
                flash(member.nome + ' ' + member.sobrenome + ' excluido!')
            db.session.commit()
            
        opcoes=[]
        for org in proj.orgs:
            membros = org.users
            for membro in membros:
                opcao = (membro.id,org.titulo+': '+membro.nome+' '+membro.sobrenome)  
                if membro != proj.responsavel:
                    if not(membro in proj.users):
                        opcoes.append(opcao)
        form.incluidos.choices = opcoes
        
        opcoes=[]
        for user in proj.users:
           opcao = (user.id,user.nome+' '+user.sobrenome)  
           if user != proj.responsavel:
               opcoes.append(opcao)
        #if len(opcoes)==0:
        #   opcao =('0','Sem membros cadastrados')
        #   opcoes.append(opcao)
        form.excluidos.choices = opcoes
        
    return render_template('projusers.html', title='Membros da Organização', form=form, big=big, projeto=proj)
    
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
        return redirect(url_for('index'))
    return render_template('organizacao.html', title='Organização '+ org.titulo , org=org, \
                           descricao=descricao, icon_url=org.logo.icon_url, icon_name=org.logo.icon_name)

@app.route('/newtask/<string:proj>', methods=['GET', 'POST'])
@login_required
def newtask(proj):
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
        #return redirect(url_for('projeto/'+str(proj_id)))
        return redirect(url_for('projeto', proj_id=str(proj_id)))
    
    return render_template('newtask.html', title='Nova Tarefa', projeto = projeto, form=form)


@app.route('/newstage/<string:proj>', methods=['GET', 'POST'])
@login_required
def newstage(proj):
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
        #return redirect(url_for('projeto/'+str(proj_id)))
        return redirect(url_for('projeto', proj_id=str(proj_id)))
    form.visibilidade.default = 'RASCUNHO'
    form.visibilidade.process_data('RASCUNHO')
    
    return render_template('newstage.html', title='Nova Etapa', projeto = projeto, form=form)

@app.route('/editstage/<string:stage_id>', methods=['GET', 'POST'])
@login_required
def editstage(stage_id):
    form = NewstageForm()
    etapa = Etapas.query.filter(Etapas.id==stage_id).first()
    projeto = Projs.query.filter(Projs.id==etapa.proj_id).first()
    if form.validate_on_submit():
        etapa.titulo=form.titulo.data
        etapa.body=form.body.data
        etapa.visibilidade=form.visibilidade.data
        photo_ids = form.imagens.data.strip().split(' ')
        for photo_id in photo_ids:
            photo = Icons.query.filter(Icons.id == photo_id).first()
            etapa.photos.append(photo)
        db.session.add(etapa)
        db.session.commit()
        db.session.flush()
        flash('Etapa editada.')
        #return redirect(url_for('projeto/'+str(proj_id)))
        return redirect(url_for('projeto', proj_id=str(projeto.id)))
        form.responsavel.process_data(org.responsavel.id)
    form.visibilidade.process_data(etapa.visibilidade)
    form.body.process_data(etapa.body)
    form.titulo.process_data(etapa.titulo)
    photos=etapa.photos
    contador = 0
    for p in photos:
        contador = contador + 1
    
    return render_template('editstage.html', title='Editar Etapa', projeto = projeto, form=form, etapa=etapa, photos=photos, contador=contador)

@app.route('/newmsg', methods=['GET', 'POST'])
@login_required
def newmsg():
    form = MsgForm()
    destinos = Users.query.all()
    user = Users.query.filter(Users.id == current_user.id).first()
    opcoes=[]
    for destino in destinos:
      if (destino.id != user.id):  
        opcao =(destino.id,destino.nome+' '+destino.sobrenome)  
        if not(opcao in opcoes):
          opcoes.append(opcao)
    form.destination.choices = opcoes
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
        a = UsersMsgs(status = "new", autor=user.username)
        a.msg = newmsg
        a.user = user
        db.session.add(a) 
        db.session.commit()
        db.session.flush()
        msg_id=newmsg.id
        for dst_id in destination_ids:
            destination = Users.query.filter(Users.id == dst_id).first()
            a = UsersMsgs(status = "new", autor=user.username)
            a.msg = newmsg
            a.user = destination
            db.session.add(a) 
            db.session.commit()
            db.session.flush()
        print('Mensagem nova')
        print(str(newmsg.users))
        print(str(user.msgs))
        flash('Mensagem enviada.')
        #return redirect(url_for('projeto/'+str(proj_id)))
        return redirect(url_for('index'))
    
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
        #return redirect(url_for('projeto/'+str(proj_id)))
        return redirect(url_for('index'))
    
    return render_template('replymsg.html', title='Enviar Mensagem', old_msg=old_msg, destination=destination, form=form)



@app.route('/edittask/<string:proj>/<string:task>', methods=['GET', 'POST'])
@login_required
def edittask(proj,task):
    form = EdittaskForm()
    projeto = Projs.query.filter(Projs.id==proj).first()
    tarefa = Tasks.query.filter(Tasks.id==task).first()
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
        #return redirect(url_for('projeto/'+str(proj_id)))
        return redirect(url_for('task', proj=str(proj), task=str(task)))
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
    return render_template('delstage.html', title='Apagar Etapa', projeto = projeto, etapa = etapa)


@app.route('/delorg/<string:org_id>', methods=['GET', 'POST'])
@login_required
def delorg(org_id):
    org = Orgs.query.filter(Orgs.id==org_id).first()
    if org.responsavel.username != current_user.username:
        flash('Ação não autorizada.')
        return redirect(url_for('index'))
    return render_template('delorg.html', title='Deletar Organização?', org = org)

@app.route('/deltaskconfirmed/<string:proj>/<string:task>', methods=['GET', 'POST'])
@login_required
def deltaskconfirmed(proj,task):
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
    return redirect(url_for('projeto', proj_id=str(projeto.id)))

@app.route('/delstageconfirmed/<string:stage_id>', methods=['GET', 'POST'])
@login_required
def delstageconfirmed(stage_id):
    etapa = Etapas.query.filter(Etapas.id==stage_id).first()
    projeto = Projs.query.filter(Projs.id==etapa.proj_id).first()
    db.session.delete(etapa)
    db.session.commit() 
    flash('Etapa apagada.')
    tasks = Tasks.query.filter(Tasks.proj_id==projeto.id).all()
    descricao = projeto.descricao
    if projeto.descricao:
        descricao = projeto.descricao.split('\n')
    else:
        descricao = " "        
    return redirect(url_for('projeto', proj_id=str(projeto.id)))

@app.route('/delorgconfirmed/<string:org_id>', methods=['GET', 'POST'])
@login_required
def delorgconfirmed(org_id):
    org = Orgs.query.filter(Orgs.id==org_id).first()
    if org.responsavel.username != current_user.username:
        flash('Somente o responsável pela organização pode executar essa ação.')
        return redirect(url_for('organizacao', orgname=str(org.titulo)))
    db.session.delete(org)
    db.session.commit() 
    flash('Organização apagada.')
    return redirect(url_for('listorgs', orgname=str(org.titulo)))

   
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
    form.responsavel.choices = get_responsavel(user)
    form.responsavel.default = 1
    id_list=['1']
    icons = Icons.query.filter(and_( Icons.criador_id.in_(id_list,) ,  Icons.tipo == 'icon')).all()
    icon = Icons.query.filter(Icons.id=='10').first()
    if form.validate_on_submit():
        newp = Projs(status="ATIVO",
                     titulo=form.titulo.data,
                     descricao=form.descricao.data,
                     objetivo=form.objetivo.data,
                     visibilidade=form.visibilidade.data,
                     responsavel_id=form.responsavel.data,
                     icon_id=form.icon.data
                     )
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
        return redirect(url_for('projeto', proj_id=str(proj_id)))
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
    return render_template('projeto.html', title=projeto.titulo, big=big, projeto=projeto, tasks=tasks, etapas=etapas)

@app.route('/editproj/<string:proj_id>', methods=['GET', 'POST'])
@login_required
def editproj(proj_id):
    projeto = Projs.query.filter(Projs.id==proj_id).first()
    form = EditprojForm()
    org_choices = get_organizacao(current_user)
    form.organizacao.choices = org_choices
    print('++++++++++++++++++++++++')
    print('choices: '+str(org_choices))
    print('++++++++++++++++++++++++')
    print('projeto.orgs.first():'+str(projeto.orgs.first()))
    if projeto.orgs.first() == None:
        form.organizacao.process_data(int(org_choices[0][0]))
        print('int(org_choices[0][0]):'+str(int(org_choices[0][0])))
    else:
        form.organizacao.process_data(int(projeto.orgs.first().id))
        print('int(projeto.orgs.first().id):'+str(int(projeto.orgs.first().id)))
    #form.organizacao.process_data(int(proj_id))
    msg="Escolha uma organização da qual você faz parte."
    resp_choices = get_responsavel(current_user,projeto.orgs.first())
    print('++++++++++++++++++++++++')
    print('resp choices: '+str(resp_choices))
    print('++++++++++++++++++++++++')
    form.responsavel.choices = resp_choices
    form.responsavel.process_data(projeto.responsavel.id)
    form.visibilidade.default = projeto.visibilidade
    form.visibilidade.process_data(projeto.visibilidade)
    
    #form.responsavel.process_data(1)
    #form.responsavel.default = 1
    #form.organizacao.default = int(proj_id)
    id_list=['1',current_user.id]
    icons = Icons.query.filter(and_( Icons.criador_id.in_(id_list,) ,  Icons.tipo == 'icon')).all()
    #icon = Icons.query.filter(Icons.id=='10').first()
    photoicon = Icons.query.filter( (Icons.icon_name=="projeto-"+proj_id) & (Icons.tipo=='projicon')).first()
    if projeto.orgs.first() != None:
        print("projeto.orgs:"+str(projeto.orgs.first()))
        print("projeto.orgs.id:"+str(projeto.orgs.first().id))
    if form.validate_on_submit():
        projeto.titulo=form.titulo.data
        projeto.descricao=form.descricao.data
        projeto.objetivo=form.objetivo.data
        projeto.status="ATIVO"
        projeto.visibilidade=form.visibilidade.data
        projeto.icon_id=form.icon.data
        oldresp_id = projeto.responsavel_id
        projeto.responsavel_id=request.form.get('responsavel')
        org = request.form.get('organizacao')
        newmember = Users.query.filter(Users.id == projeto.responsavel_id).first()
        if oldresp_id != newmember.id:
          if newmember in projeto.users:
            flash(newmember.nome + ' ' +  newmember.sobrenome + ' agora responsável do projeto')
          else:
            projeto.users.append(newmember)
            flash( newmember.nome + ' ' +  newmember.sobrenome + ' agora participante e responsável do projeto!')
            db.session.commit()
        print('form.organizacao.data:'+str(form.organizacao.data))
        if org:
            print('***************************')
            print("org:"+str(org))
            for o in projeto.orgs.all():
                print('***************************')
                print ('o:'+str(o))
                projeto.orgs.remove(o)
            org_reg = Orgs.query.filter( Orgs.id==org ).first()
            projeto.orgs.append(org_reg)
        db.session.add(projeto)
        db.session.commit()
        db.session.flush()
        flash('Congratulations, you edited the project!')
        return redirect(url_for('projeto', proj_id=str(proj_id)))
    form.descricao.process_data(projeto.descricao)
    return render_template('editproj.html', title='Editar Projeto', icons=icons, msg=msg, form=form, projeto=projeto)


@app.route('/lista_de_projetos', methods=['GET', 'POST'])
@login_required
def listproj():
    user = Users.query.filter(Users.username==current_user.username).first()
    outros=[]
    for p in user.projs.all():
        for porg in p.orgs.all():
            if user in porg.users.all():
                flash(user.nome+' '+user.sobrenome+'('+str(user.id)+') em '+porg.titulo)
            else:
                porg.users.append(user)
                db.session.commit()
                db.session.flush()
                flash('Ops, '+user.nome+' '+user.sobrenome+'('+str(user.id)+') agora em '+porg.titulo)
    for p in Projs.query.all():
        outro = True
        for o in user.orgs:
            if o in p.orgs:
                outro = False
        if outro:
          outros.append(p)
    outrosprojs = outros
    return render_template('lista_de_projetos.html', user=user, outrosprojs=outrosprojs, title='Lista de Projetos')

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
        flash(url_for('edit', url=url))
        return redirect(url_for('edit', url=url))
    
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
    
    url = "https://vamostrabalharjuntos.com.br/projetos/"
    path = "static/"
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
        my_file = os.path.join(THIS_FOLDER, path+filename)
        print("my_file:"+my_file)
        base64_img_bytes = data['data'].encode('utf-8')
        f = open(my_file, 'wb')
        decoded_image_data = base64.decodebytes(base64_img_bytes)
        f.write(decoded_image_data)
        f.close()
        url_my_file = url+path+filename
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
    app.run(ssl_context=('/etc/letsencrypt/live/vamostrabalharjuntos.com.br/fullchain.pem', '/etc/letsencrypt/live/vamostrabalharjuntos.com.br//privkey.pem'))
