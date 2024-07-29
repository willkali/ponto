from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, send_file
from pdf.gerar_pdf import generate_pdf
from data_base import create_table
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import psycopg2
import os
import io

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", 'localhost'),
        dbname=os.getenv("DB_NAME", 'cadastro'),
        user=os.getenv("DB_USER", 'postgres'),
        password=os.getenv("DB_PASSWORD", 'reboot3')
    )
    return conn

@app.before_request
def initialize():
    if not hasattr(app, 'initialized'):
        create_table()
        app.initialized = True

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/scripts/<path:filename>')
def scripts(filename):
    return send_from_directory('scripts', filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()

        # Manipulação dos dados do formulário para inserção no banco de dados
        nascimento_str = request.form.get('nascimento')
        nascimento = None
        if nascimento_str:
            try:
                nascimento = datetime.strptime(nascimento_str, '%d/%m/%Y').date()
            except ValueError:
                try:
                    nascimento = datetime.strptime(nascimento_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Formato de data inválido. Use DD/MM/AAAA ou AAAA-MM-DD.', 'danger')
                    return redirect(url_for('register'))

        cur.execute('''
            INSERT INTO usuarios (cpf, email, senha, nome, sobrenome, nascimento, rg, sexo, cep, endereco, numero, bairro, complemento, cidade, estado, telefone, celular)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            request.form['cpf'],
            request.form['email'],
            request.form['senha'],
            request.form.get('nome'),
            request.form.get('sobrenome'),
            nascimento,
            request.form.get('rg'),
            request.form.get('sexo'),
            request.form.get('cep'),
            request.form.get('endereco'),
            request.form.get('numero'),
            request.form.get('bairro'),
            request.form.get('complemento'),
            request.form.get('cidade'),
            request.form.get('estado'),
            request.form.get('telefone'),
            request.form.get('celular')
        ))

        # Obtenha o ID do usuário recém-criado
        cur.execute('SELECT id FROM usuarios WHERE email = %s', (request.form['email'],))
        user_id = cur.fetchone()[0]

        # Inserir horários de trabalho
        dias = ["domingo", "segunda", "terca", "quarta", "quinta", "sexta", "sabado"]
        total_horas = 0
        for dia in dias:
            if request.form.get(f'{dia}_trabalhado'):
                entrada_str = request.form.get(f'entrada_{dia}')
                saida_str = request.form.get(f'saida_{dia}')
                intervalo_str = request.form.get(f'intervalo_{dia}')

                if entrada_str and saida_str:
                    try:
                        entrada = datetime.strptime(entrada_str, '%H:%M').time()
                        saida = datetime.strptime(saida_str, '%H:%M').time()
                        intervalo = int(intervalo_str) if intervalo_str else 0

                        entrada_dt = datetime.combine(datetime.today(), entrada)
                        saida_dt = datetime.combine(datetime.today(), saida)
                        carga_horaria = (saida_dt - entrada_dt).seconds / 3600 - intervalo / 60
                        total_horas += carga_horaria

                        cur.execute('''
                            INSERT INTO horarios_trabalho (user_id, dia_semana, entrada, saida, intervalo, carga_horaria)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (user_id, dia, entrada, saida, intervalo, carga_horaria))
                    except ValueError:
                        flash('Formato de horário inválido. Use HH:MM.', 'danger')
                        return redirect(url_for('register'))
                else:
                    flash('Entrada e saída são obrigatórias para cada dia de trabalho.', 'danger')
                    return redirect(url_for('register'))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('admin_dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuarios WHERE email = %s AND senha = %s', (email, senha))
        user = cur.fetchone()
        cur.execute('SELECT * FROM admin WHERE email = %s AND senha = %s', (email, senha))
        admin = cur.fetchone()
        cur.close()
        conn.close()

        if admin:
            session['usuario'] = admin[1]  # Supondo que o e-mail esteja na segunda coluna
            session['user_id'] = admin[0]  # Supondo que o ID esteja na primeira coluna
            print("Admin logado com sucesso")
            return redirect(url_for('admin_dashboard'))
        elif user:
            session['nome'] = user[4]  # Supondo que o nome esteja na quinta coluna
            session['sobrenome'] = user[5]  # Supondo que o sobrenome esteja na sexta coluna
            session['user_id'] = user[0]  # Supondo que o ID esteja na primeira coluna
            session['usuario'] = user[1]  # Supondo que o email esteja na segunda coluna (ou ajuste conforme sua tabela)
            print("Usuário logado com sucesso")
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('login'))

    return render_template('dashboard.html', user=user)

@app.route('/admin_dashboard')
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM usuarios')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'usuario' not in session or session['usuario'] != 'admin@ff.com':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')

        if action == 'delete' and user_id:
            try:
                cur.execute('DELETE FROM usuarios WHERE id = %s', (user_id,))
                conn.commit()
            except psycopg2.errors.ForeignKeyViolation:
                flash('Não é possível deletar o usuário porque ele tem registros de ponto associados.', 'danger')
            finally:
                cur.close()
                conn.close()
        elif action == 'edit' and user_id:
            return redirect(url_for('edit_register', user_id=user_id))

    cur.execute('SELECT id, nome, sobrenome, email FROM usuarios')
    users = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin.html', users=users)

@app.route('/controle_registros', methods=['GET'])
def controle_registros():
    if 'usuario' not in session or session['usuario'] != 'admin@ff.com':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch the users from the database
    cur.execute('SELECT id, nome, sobrenome, email FROM usuarios')
    users = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('controle_registros.html', users=users)

@app.route('/edit_register/<int:user_id>', methods=['GET', 'POST'])
def edit_register(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        cpf = request.form.get('cpf')
        email = request.form.get('email')
        senha = request.form.get('senha')
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')

        if not cpf or not email or not senha or not nome or not sobrenome:
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('edit_register', user_id=user_id))

        nascimento_str = request.form.get('nascimento')
        nascimento = None
        if nascimento_str:
            try:
                nascimento = datetime.strptime(nascimento_str, '%d/%m/%Y')
            except ValueError:
                try:
                    nascimento = datetime.strptime(nascimento_str, '%Y-%m-%d')
                except ValueError:
                    flash('Formato de data inválido. Use DD/MM/AAAA ou AAAA-MM-DD.', 'danger')
                    return redirect(url_for('edit_register', user_id=user_id))

        cur.execute('''
            UPDATE usuarios SET
            cpf = %s, email = %s, senha = %s, nome = %s, sobrenome = %s, nascimento = %s, rg = %s, sexo = %s, cep = %s,
            endereco = %s, numero = %s, bairro = %s, complemento = %s, cidade = %s, estado = %s, telefone = %s, celular = %s
            WHERE id = %s
        ''', (
            cpf,
            email,
            senha,
            nome,
            sobrenome,
            nascimento,
            request.form.get('rg'),
            request.form.get('sexo'),
            request.form.get('cep'),
            request.form.get('endereco'),
            request.form.get('numero'),
            request.form.get('bairro'),
            request.form.get('complemento'),
            request.form.get('cidade'),
            request.form.get('estado'),
            request.form.get('telefone'),
            request.form.get('celular'),
            user_id
        ))

        conn.commit()
        cur.close()
        conn.close()

        flash('Registro atualizado com sucesso.', 'success')
        return redirect(url_for('admin'))

    cur.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin'))

    return render_template('edit_register.html', user=user)

@app.route('/registro_ponto', methods=['GET', 'POST'])
def registro_ponto():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    user_id = session.get('user_id')
    timestamp = datetime.now()

    estado = 'entrada'

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'entrada':
            cur.execute('INSERT INTO registro_ponto (user_id, entrada) VALUES (%s, %s)', (user_id, timestamp))
            conn.commit()
            flash('Registro de entrada salvo com sucesso.', 'success')
        elif action == 'intervalo_inicio':
            cur.execute('UPDATE registro_ponto SET intervalo_inicio = %s WHERE user_id = %s AND saida IS NULL', (timestamp, user_id))
            conn.commit()
            flash('Início de intervalo registrado com sucesso.', 'success')
        elif action == 'intervalo_fim':
            cur.execute('UPDATE registro_ponto SET intervalo_fim = %s WHERE user_id = %s AND saida IS NULL', (timestamp, user_id))
            conn.commit()
            flash('Fim de intervalo registrado com sucesso.', 'success')
        elif action == 'saida':
            cur.execute('UPDATE registro_ponto SET saida = %s WHERE user_id = %s AND saida IS NULL', (timestamp, user_id))
            conn.commit()
            flash('Registro de saída salvo com sucesso.', 'success')

    cur.execute('''
        SELECT entrada, intervalo_inicio, intervalo_fim, saida
        FROM registro_ponto
        WHERE user_id = %s AND DATE(entrada) = %s
    ''', (user_id, datetime.today().date()))
    result = cur.fetchone()

    if result:
        entrada, intervalo_inicio, intervalo_fim, saida = result
        
        if not entrada:
            estado = 'entrada'
        elif not intervalo_inicio:
            estado = 'intervalo_inicio'
        elif not intervalo_fim:
            estado = 'intervalo_fim'
        elif not saida:
            estado = 'saida'
        else:
            estado = 'completo'

    cur.close()
    conn.close()

    return render_template('registro_ponto.html', estado=estado, nome=session.get('nome'))

@app.route('/controle_registro_usuario')
def controle_registro_usuario():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Recuperar registros de ponto
    cur.execute('''
        SELECT 
            entrada, 
            intervalo_inicio, 
            intervalo_fim, 
            saida
        FROM registro_ponto
        WHERE user_id = %s
        ORDER BY entrada DESC
    ''', (user_id,))

    registros = cur.fetchall()

    # Recuperar carga horária cadastrada
    cur.execute('''
        SELECT carga_horaria
        FROM horarios_trabalho
        WHERE user_id = %s
        LIMIT 1
    ''', (user_id,))

    carga_horaria_result = cur.fetchone()
    carga_horaria = carga_horaria_result['carga_horaria'] if carga_horaria_result else timedelta(hours=8)  # Valor padrão se não encontrado

    for registro in registros:
        entrada = registro['entrada']
        intervalo_inicio = registro['intervalo_inicio']
        intervalo_fim = registro['intervalo_fim']
        saida = registro['saida']

        if entrada and intervalo_inicio and intervalo_fim and saida:
            total_horas_trabalhadas = (intervalo_inicio - entrada) + (saida - intervalo_fim)
            total_horas_trabalhadas_seconds = int(total_horas_trabalhadas.total_seconds())
            
            # Convertendo o total de segundos para HH:mm:ss
            total_horas_trabalhadas_str = str(timedelta(seconds=total_horas_trabalhadas_seconds))
            registro['total_horas_trabalhadas'] = total_horas_trabalhadas_str

            # Calculando o saldo
            carga_horaria_seconds = int(carga_horaria.total_seconds())
            saldo_seconds = total_horas_trabalhadas_seconds - carga_horaria_seconds
            saldo_str = str(timedelta(seconds=abs(saldo_seconds)))
            
            # Formatação do saldo
            if saldo_seconds >= 0:
                registro['saldo'] = f"+{saldo_str}"
                registro['saldo_class'] = "positive"
            else:
                registro['saldo'] = f"-{saldo_str}"
                registro['saldo_class'] = "negative"
        else:
            registro['total_horas_trabalhadas'] = '00:00:00'
            registro['saldo'] = f"+{str(carga_horaria)}"
            registro['saldo_class'] = "positive"

    cur.close()
    conn.close()

    return render_template('controle_registro_usuario.html', registros=registros)

@app.route('/gerar_pdf/<int:user_id>', methods=['GET'])
def gerar_pdf(user_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    pdf_path = generate_pdf(user_id)
    return send_file(pdf_path, as_attachment=True)

@app.route('/fonts/<path:filename>')
def fonts(filename):
    return send_from_directory('fonts', filename)

@app.route('/img/<path:filename>')
def img(filename):
    return send_from_directory('img', filename)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
