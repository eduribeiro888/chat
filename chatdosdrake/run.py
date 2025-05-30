from flask import Flask, render_template, redirect, request, session, jsonify
from controllers.sql import Banco
from controllers.chat import Chat
from flask_socketio import SocketIO
import sqlite3
from datetime import datetime  # Importando datetime para timestamp

app = Flask(__name__)
socketio = SocketIO(app)
app.config['SECRET_KEY'] = '1234'

# -----------------------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

# -----------------------------------------------------------------------------------------------------------------

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# -----------------------------------------------------------------------------------------------------------------

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')

    if not usuario or not senha:
        return "Erro: Usuário e senha são obrigatórios!", 400

    try:
        with sqlite3.connect('models/banco.db', check_same_thread=False) as conexao:
            cursor = conexao.cursor()
            sql = "SELECT * FROM tb_login WHERE usuario = ? AND senha = ?"
            cursor.execute(sql, (usuario, senha))
            user = cursor.fetchone()
            if user:
                session['usuario_logado'] = usuario
                print(session['usuario_logado'])
                return redirect('/chat')
            else:
                return "Erro: Usuário ou senha inválidos!", 401
    except sqlite3.Error as e:
        return f"Erro ao acessar o banco de dados: {e}", 500

# -----------------------------------------------------------------------------------------------------------------

@app.route('/cadastrousuario', methods=['POST'])
def cadastrousuario():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')

    if not usuario or not senha:
        return "Erro: Usuário e senha são obrigatórios!", 400

    try:
        with sqlite3.connect('models/banco.db', check_same_thread=False) as conexao:
            cursor = conexao.cursor()
            sql = '''INSERT INTO tb_login (usuario, senha) VALUES (?, ?)'''
            cursor.execute(sql, (usuario, senha))
            conexao.commit()
    except sqlite3.Error as e:
        return f"Erro ao inserir no banco de dados: {e}", 500

    return redirect('/')

# -----------------------------------------------------------------------------------------------------------------

@app.route('/chat', methods=['GET'])
def chat():
    usuario_logado = session.get('usuario_logado')

    if not usuario_logado:
        return redirect('/')  # Redireciona caso não esteja logado

    chat_obj = Chat()
    mensagens = chat_obj.consultar_mensagem()

    # Buscar os dados do usuário logado no banco
    with sqlite3.connect('models/banco.db', check_same_thread=False) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM tb_login WHERE usuario = ?", (usuario_logado,))
        usuario = cursor.fetchone()  # Retorna algo como (id, usuario, nome)

    return render_template('chat.html', mensagens=mensagens, usuario=usuario, usuario_logado=usuario_logado)

# -----------------------------------------------------------------------------------------------------------------

@socketio.on('enviar_mensagem')
def handle_message(data):
    mensagem = data['mensagem']
    chat_obj = Chat(mensagem)
    chat_obj.enviar_mensagem()

    # Emitindo evento para todos os clientes conectados
    socketio.emit('nova_mensagem', {
        'mensagem': f"{session.get('usuario_logado')}: {mensagem}",
        'data_hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# -----------------------------------------------------------------------------------------------------------------

 

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=80, debug=True)
