from controllers.sql import Banco
from flask import session
from datetime import datetime

class Chat:
    def __init__(self, mensagem=None):
        self.mensagem = mensagem
        self.banco = Banco()

    def enviar_mensagem(self):
        usuario = session.get("usuario_logado")
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formato de data e hora

        try:
            dados = {
                'mensagem': f"{usuario}: {self.mensagem}",
                'data_hora': data_hora  # Adiciona a data e hora ao banco
            }
            self.banco.inserir('tb_chat', dados)
            print(f"Chat.py | Enviar Mensagem | Mensagem enviada com sucesso às {data_hora}")
        except Exception as e:
            print(f"Chat.py | Enviar Mensagem | Erro ao enviar: {e}")

    def consultar_mensagem(self):
        try:
            dados = self.banco.consultar('tb_chat')
            print("Chat.py | Consultar Mensagem | Consultado com sucesso")
            return dados
        except Exception as e:
            print(f"Chat.py | Consultar Mensagem | Erro ao consultar: {e}")
            return []
