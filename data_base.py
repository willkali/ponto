# data_base.py

import psycopg2
import os

def create_database():
    try:
        # Conectar ao banco de dados padrão 'postgres'
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", 'localhost'),
            dbname='postgres',
            user=os.getenv("DB_USER", 'postgres'),
            password=os.getenv("DB_PASSWORD", 'reboot3')
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Verificar se o banco de dados 'cadastro' existe
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ('cadastro',))
        exists = cur.fetchone()

        if not exists:
            cur.execute('CREATE DATABASE cadastro')
            print("Banco de dados 'cadastro' criado com sucesso.")
        else:
            print("Banco de dados 'cadastro' já existe.")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")

def create_table():
    try:
        # Chamar a função create_database para garantir que o banco de dados exista
        create_database()

        # Pegando variáveis de ambiente
        host = os.getenv("DB_HOST", 'localhost')
        dbname = os.getenv("DB_NAME", 'cadastro')
        user = os.getenv("DB_USER", 'postgres')
        password = os.getenv("DB_PASSWORD", 'reboot3')

        # Mensagem de depuração
        print(f"Conectando ao banco de dados em {host} com usuário {user} no banco {dbname}")

        # Conectando ao banco de dados 'cadastro'
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password
        )
        cur = conn.cursor()

        # Criar a tabela de usuários
        cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            cpf VARCHAR(14) NOT NULL,
            email VARCHAR(255) NOT NULL,
            senha VARCHAR(255) NOT NULL,
            nome VARCHAR(255) NOT NULL,
            sobrenome VARCHAR(255) NOT NULL,
            nascimento DATE NOT NULL,
            rg VARCHAR(20) NOT NULL,
            sexo VARCHAR(10),
            cep VARCHAR(10),
            endereco VARCHAR(255),
            numero VARCHAR(10),
            bairro VARCHAR(255),
            complemento VARCHAR(255),
            cidade VARCHAR(255),
            estado VARCHAR(2),
            telefone VARCHAR(15),
            celular VARCHAR(15),
            status VARCHAR(50),
            obs TEXT
        )
        ''')
        
        # Criação da tabela registro_ponto, se não existir
        cur.execute('''
        CREATE TABLE IF NOT EXISTS registro_ponto (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            entrada TIMESTAMP,
            intervalo_inicio TIMESTAMP,
            intervalo_fim TIMESTAMP,
            saida TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
        );
    ''')
        
        # Criação da tabela horarios_trabalho, se não existir
        cur.execute('''
        CREATE TABLE IF NOT EXISTS horarios_trabalho (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            dia_semana VARCHAR(10),
            entrada TIME,
            saida TIME,
            intervalo INTEGER,
            carga_horaria INTERVAL,
            FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
        );
    ''')
        # Criando a tabela de admin
        cur.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                senha VARCHAR(255) NOT NULL
            )
        ''')
        print("Tabela 'admin' criada com sucesso ou já existe.")

        # Adicionando um usuário admin padrão
        cur.execute('''
            INSERT INTO admin (email, senha) VALUES (%s, %s)
            ON CONFLICT (email) DO NOTHING
        ''', ('admin@ff.com', '1234'))  # Você deve hash essa senha em um aplicativo real

        conn.commit()
        cur.close()
        conn.close()
        print("Tabelas e usuário admin configurados com sucesso.")

    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

# Chame a função create_table para verificar se está funcionando
create_table()
