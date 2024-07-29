from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import os
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", 'localhost'),
        dbname=os.getenv("DB_NAME", 'cadastro'),
        user=os.getenv("DB_USER", 'postgres'),
        password=os.getenv("DB_PASSWORD", 'reboot3')
    )
    return conn

def fetch_user_data(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,))
    user_data = cur.fetchone()
    cur.execute('''
        SELECT entrada, intervalo_inicio, intervalo_fim, saida
        FROM registro_ponto
        WHERE user_id = %s
        ORDER BY entrada DESC
    ''', (user_id,))
    registros_ponto = cur.fetchall()
    cur.close()
    conn.close()
    return user_data, registros_ponto

def generate_pdf(user_id):
    user_data, registros_ponto = fetch_user_data(user_id)
    file_path = f"pdf/registro_ponto_{user_id}.pdf"
    
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Adicionar os dados do funcionário
    user_info = [
        ['ID', user_data[0]],
        ['Nome', user_data[4]],
        ['Sobrenome', user_data[5]],
        ['Email', user_data[2]],
        ['CPF', user_data[1]],
        ['RG', user_data[7]],
        ['Telefone', user_data[16]],
        ['Celular', user_data[17]],
        ['Endereço', f"{user_data[10]}, {user_data[11]}, {user_data[12]}, {user_data[13]}"],
        ['Cidade/Estado', f"{user_data[14]}/{user_data[15]}"]
    ]
    table = Table(user_info)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Paragraph(" ", styles['Normal']))

    # Adicionar os registros de ponto
    registros_data = [['Entrada', 'Início do Intervalo', 'Fim do Intervalo', 'Saída']]
    for registro in registros_ponto:
        registros_data.append([
            registro[0].strftime('%Y-%m-%d %H:%M:%S') if registro[0] else '',
            registro[1].strftime('%Y-%m-%d %H:%M:%S') if registro[1] else '',
            registro[2].strftime('%Y-%m-%d %H:%M:%S') if registro[2] else '',
            registro[3].strftime('%Y-%m-%d %H:%M:%S') if registro[3] else '',
        ])
    
    table = Table(registros_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    return file_path
