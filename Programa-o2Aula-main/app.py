from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector


app = Flask(__name__)

app.secret_key = 'baincaCaimla0412'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'login'
}


@app.route('/cadastro', methods = [ 'GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        username = request.form['username']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuario WHERE username_name =" "%s OR email_usuario = %s", (username, email))
        if cursor.fetchone():
            flash ("Nome de usuário ou email já cadastrado." , "erro")
            return redirect(url_for('cadastro'))
        
        cursor.execute("""INSERT INTO usuario (nome_usuario, username_usuario, password_usuario, email_usuario, conta_ativa) VALUES (%s, %s, %s, %s, %s)""", (nome, username, senha, email, True))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Cadastro realizado com sucesso! Você já pode fazer login.", "sucesso")
        return redirect(url_for('login'))
    
    return render_template('cadastro.html')