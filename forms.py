#!/bin/python
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField, TextAreaField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from models import Users, Orgs, Posts, Projs, Tasks, Etapas
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from flask_wtf.file import FileField, FileRequired, FileAllowed

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
