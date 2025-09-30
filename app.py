from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import base64
import re

app = Flask(__name__)
app.secret_key = "chave_super_secreta"  # troque por algo seguro!

def conectar():
    return sqlite3.connect('banco.db')

# Criação da tabela de usuários
conn = conectar()
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        nome TEXT NOT NULL,
        sobrenome TEXT NOT NULL,
        senha TEXT NOT NULL,
        area TEXT NOT NULL
    )
''')
conn.commit()
conn.close()

# Função para validar senha
def validar_senha(senha):
    if len(senha) < 8:
        return False
    if not re.search(r"[A-Z]", senha):
        return False
    if not re.search(r"[@$!%*?&]", senha):
        return False
    return True

# Função para validar email
def validar_email(email):
    return re.match(r".+@.+\.(com|com\.br)$", email) is not None

# Cadastro
@app.route('/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        area = request.form['area']
        senha = request.form['senha']
        confirmar = request.form['confirmar']

        if senha != confirmar:
            flash("Erro: As senhas não coincidem.", "erro")
            return redirect('/')

        if not validar_email(email):
            flash("Erro: O email deve terminar com .com ou .com.br", "erro")
            return redirect('/')

        if not validar_senha(senha):
            flash("Erro: A senha deve ter no mínimo 8 caracteres, incluir uma letra maiúscula e um caractere especial (@$!%*?&).", "erro")
            return redirect('/')

        senha_criptografada = base64.b64encode(senha.encode()).decode()

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email=?", (email,))
        if cursor.fetchone():
            conn.close()
            flash("Erro: O email utilizado já possui cadastro.", "erro")
            return redirect('/')

        cursor.execute(
            "INSERT INTO usuarios (email, nome, sobrenome, area, senha) VALUES (?, ?, ?, ?, ?)",
            (email, nome, sobrenome, area, senha_criptografada)
        )
        conn.commit()
        conn.close()

        session['usuario'] = email
        flash("Cadastro realizado com sucesso!", "sucesso")
        return redirect('/index')

    return render_template('cadastro.html')

# Página inicial (protegida)
@app.route('/index')
def index():
    if 'usuario' not in session:
        return redirect('/login')

    # Pegar o nome do usuário logado
    email = session['usuario']
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE email=?", (email,))
    resultado = cursor.fetchone()
    conn.close()
    nome_usuario = resultado[0] if resultado else "Usuário"

    return render_template('index.html', usuario=session['usuario'], nome_usuario=nome_usuario)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            senha_armazenada = base64.b64decode(user[0]).decode()
            if senha == senha_armazenada:
                session['usuario'] = email
                return redirect('/index')
            else:
                flash("Senha incorreta!", "erro")
                return redirect('/login')
        else:
            flash("Usuário não encontrado!", "erro")
            return redirect('/login')

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
