# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(255))
    sobrenome = db.Column(db.String(255))
    nascimento = db.Column(db.Date)
    rg = db.Column(db.String(20))
    sexo = db.Column(db.String(1))
    cep = db.Column(db.String(10))
    endereco = db.Column(db.String(255))
    numero = db.Column(db.String(10))
    bairro = db.Column(db.String(100))
    complemento = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    telefone = db.Column(db.String(20))
    celular = db.Column(db.String(20))
