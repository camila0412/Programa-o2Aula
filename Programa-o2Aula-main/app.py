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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        senha = request.form['senha'].strip()

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE username_usuario = %s", (username,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario and check_password_hash(usuario['password_usuario'], senha):
            if not usuario['conta_ativa']:
                flash("Esta conta está desativada.", "erro")
                return redirect(url_for('login'))
            
            session['usuario_id'] = usuario['cod_usuario']
            session['usuario_nome'] = usuario['nome_usuario']
            return redirect(url_for('dashboard'))
        else:
            flash("Usuário ou senha inválidos.", "erro")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # 1. Verifica se a chave 'usuario_id' existe na sessão.
    #    Esta é a forma mais segura de saber se o login foi feito com sucesso.
    if 'usuario_id' not in session:
        # Se não estiver logado, envia uma mensagem e redireciona para a tela de login.
        flash("Você precisa fazer login para acessar esta página.", "erro")
        return redirect(url_for('login'))
    
    # 2. Se o usuário estiver logado, simplesmente renderize o template do dashboard.
    #    O template 'dashboard.html' (que estende o 'base.html') vai acessar
    #    automaticamente a variável {{ session['usuario_nome'] }} e exibi-la.
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('usuario_nome', None)
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for('login'))

# Rota Principal (Raiz do site)
@app.route('/')
def index():
    return redirect(url_for('login'))

# Rota para verificar se usuário ou email já existem
@app.route('/verificar_usuario_email', methods=['POST'])
def verificar_usuario_email():
    username = request.form['username']
    email = request.form['email']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuario WHERE username_usuario = %s OR email_usuario = %s", (username, email))
    existe = cursor.fetchone()
    cursor.close()
    conn.close()

    return 'existe' if existe else 'disponivel'

if __name__ == '__main__':
    app.run(debug=True)

# Rota para Listar e Pesquisar Publicadoras
@app.route('/publicadoras')
def publicadoras():
    # Proteção de rota
    if 'usuario_id' not in session:
        flash("Você precisa fazer login para acessar esta página.", "erro")
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Lógica de pesquisa
    query = request.args.get('q')
    if query:
        search_query = "%" + query + "%"
        cursor.execute("SELECT * FROM Publicadora WHERE nome_Publicadora LIKE %s ORDER BY nome_Publicadora ASC", (search_query,))
    else:
        cursor.execute("SELECT * FROM Publicadora ORDER BY nome_Publicadora ASC")
    
    lista_publicadoras = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('publicadoras.html', publicadoras=lista_publicadoras, query=query)

# Rota para Cadastrar uma Nova Publicadora
@app.route('/publicadoras/cadastrar', methods=['GET', 'POST'])
def cadastrar_publicadora():
    if 'usuario_id' not in session:
        flash("Você precisa fazer login para acessar esta página.", "erro")
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome_publicadora'].strip()
        pais = request.form['pais_publicadora'].strip()

        if not nome:
            flash("O nome da publicadora é obrigatório.", "erro")
            return redirect(url_for('cadastrar_publicadora'))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verifica se a publicadora já existe
        cursor.execute("SELECT cod_Publicadora FROM Publicadora WHERE nome_Publicadora = %s", (nome,))
        if cursor.fetchone():
            flash("Já existe uma publicadora com este nome.", "erro")
            cursor.close()
            conn.close()
            return redirect(url_for('cadastrar_publicadora'))

        # Insere a nova publicadora
        cursor.execute("INSERT INTO Publicadora (nome_Publicadora, pais_Publicadora) VALUES (%s, %s)", (nome, pais))
        conn.commit()
        
        cursor.close()
        conn.close()

        flash("Publicadora cadastrada com sucesso!", "sucesso")
        return redirect(url_for('publicadoras'))

    return render_template('cadastrar_publicadora.html')

# Rota para Editar uma Publicadora
@app.route('/publicadoras/editar/<int:cod>', methods=['GET', 'POST'])
def editar_publicadora(cod):
    if 'usuario_id' not in session:
        flash("Você precisa fazer login para acessar esta página.", "erro")
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome_publicadora'].strip()
        pais = request.form['pais_publicadora'].strip()

        if not nome:
            flash("O nome da publicadora é obrigatório.", "erro")
            return redirect(url_for('editar_publicadora', cod=cod))

        # Verifica se o novo nome já existe em outro registro
        cursor.execute("SELECT cod_Publicadora FROM Publicadora WHERE nome_Publicadora = %s AND cod_Publicadora != %s", (nome, cod))
        if cursor.fetchone():
            flash("Já existe outra publicadora com este nome.", "erro")
            cursor.close()
            conn.close()
            return redirect(url_for('editar_publicadora', cod=cod))
        
        # Atualiza o registro
        cursor.execute("UPDATE Publicadora SET nome_Publicadora = %s, pais_Publicadora = %s WHERE cod_Publicadora = %s", (nome, pais, cod))
        conn.commit()
        
        cursor.close()
        conn.close()

        flash("Publicadora atualizada com sucesso!", "sucesso")
        return redirect(url_for('publicadoras'))

    # GET: Busca a publicadora atual para preencher o formulário
    cursor.execute("SELECT * FROM Publicadora WHERE cod_Publicadora = %s", (cod,))
    pub = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if not pub:
        flash("Publicadora não encontrada.", "erro")
        return redirect(url_for('publicadoras'))

    return render_template('editar_publicadora.html', pub=pub)

# Rota para Excluir uma Publicadora
@app.route('/publicadoras/excluir/<int:cod>', methods=['POST'])
def excluir_publicadora(cod):
    if 'usuario_id' not in session:
        flash("Você precisa fazer login para acessar esta página.", "erro")
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Exclui a publicadora
    # Nota: A regra ON DELETE SET NULL na tabela Jogo fará com que os jogos
    # desta publicadora tenham seu `cod_publicadora_fk` definido como NULL.
    cursor.execute("DELETE FROM Publicadora WHERE cod_Publicadora = %s", (cod,))
    conn.commit()
    
    cursor.close()
    conn.close()

    flash("Publicadora excluída com sucesso!", "sucesso")
    return redirect(url_for('publicadoras'))






# Rotas de Gerenciamento de Jogos
# -------------------------------------------

# Rota para Listar Jogos em formato de Card
@app.route('/jogos')
def jogos():
    if 'usuario_id' not in session:
        flash("Você precisa fazer login para acessar esta página.", "erro")
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Query complexa para buscar jogos e agrupar plataformas e gêneros
    # Usamos LEFT JOIN para garantir que jogos sem dev/pub ainda apareçam
    # Usamos GROUP_CONCAT para juntar múltiplos gêneros/plataformas em uma única string
    base_query = """
        SELECT 
            j.cod_Jogo,
            j.titulo_Jogo,
            j.url_imagem_capa_Jogo,
            YEAR(j.data_lancamento_Jogo) AS ano_lancamento,
            d.nome_Desenvolvedor,
            GROUP_CONCAT(DISTINCT p.nome_Plataforma ORDER BY p.nome_Plataforma SEPARATOR ', ') AS plataformas,
            GROUP_CONCAT(DISTINCT g.nome_Genero ORDER BY g.nome_Genero SEPARATOR ', ') AS generos
        FROM 
            Jogo j
        LEFT JOIN 
            Desenvolvedor d ON j.cod_desenvolvedor_fk = d.cod_Desenvolvedor
        LEFT JOIN 
            Jogo_Plataforma jp ON j.cod_Jogo = jp.cod_jogo_fk
        LEFT JOIN 
            Plataforma p ON jp.cod_plataforma_fk = p.cod_Plataforma
        LEFT JOIN 
            Jogo_Genero jg ON j.cod_Jogo = jg.cod_jogo_fk
        LEFT JOIN 
            Genero g ON jg.cod_genero_fk = g.cod_Genero
    """

    # Lógica de pesquisa
    query = request.args.get('q')
    if query:
        search_query = "%" + query + "%"
        # Adiciona a cláusula WHERE e GROUP BY para a pesquisa
        cursor.execute(base_query + " WHERE j.titulo_Jogo LIKE %s GROUP BY j.cod_Jogo ORDER BY j.titulo_Jogo ASC", (search_query,))
    else:
        # Adiciona apenas o GROUP BY para a listagem completa
        cursor.execute(base_query + " GROUP BY j.cod_Jogo ORDER BY j.titulo_Jogo ASC")

    lista_jogos = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('jogos.html', jogos=lista_jogos, query=query)


# Executa o app
if __name__ == '__main__':
    app.run(debug=True)
