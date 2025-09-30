from flask import Flask, render_template, request, redirect
import sqlite3
import base64

app = Flask(__name__)

def conectar():
    return sqlite3.connect('banco.db')

# Tabela de usuários
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

#guarda as infos do cadastro
@app.route('/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        senha = request.form['senha']
        confirmar = request.form['confirmar']
        area = request.form['area']

        if senha != confirmar:
            return "Erro: As senhas não coincidem."

        senha_criptografada = base64.b64encode(senha.encode()).decode()

        conn = conectar()
        cursor = conn.cursor()


        cursor.execute("SELECT * FROM usuarios WHERE email=?", (email,))
        if cursor.fetchone():
            conn.close()
            return "Erro: Este email já está cadastrado."
        

        cursor.execute(
            "INSERT INTO usuarios (email, nome, sobrenome, senha, area) VALUES (?, ?, ?, ?, ?)",
            (email, nome, sobrenome, senha_criptografada, area)
        )
        conn.commit()
        conn.close()
        return redirect('/index')

    return render_template('cadastro.html')

#direciona para a pagina inicial
@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
