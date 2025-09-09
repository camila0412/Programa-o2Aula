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