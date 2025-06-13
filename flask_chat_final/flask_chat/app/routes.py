from flask import Blueprint, render_template, request, session, jsonify
from datetime import datetime
from app import socketio
import os
from app.gemini.modelo import responder_pergunta, fn_rag, fn_juiz, piadas_ovo
import time

bp = Blueprint("chat", __name__)

def registrar_log(origem, mensagem, chat_id):
    os.makedirs("logs", exist_ok=True)
    caminho = f"logs/chat_{chat_id}.log"
    mensagem = mensagem.strip()
    if mensagem:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(caminho, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{origem}] {mensagem}\n")
        html = f"[{timestamp}] [{origem}] {mensagem}"
        socketio.emit("nova_mensagem", {"html": html})
    
def carregar_historico():
    chat_id = session.get("chat_id")
    caminho = f"logs/chat_{chat_id}.log"
    linhas_coloridas = []
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = list(f.readlines())
            for linha in linhas:
                if "[CLIENTE]" in linha:
                    cor = "red"
                elif "[ESPECIALISTA]" in linha:
                    cor = "blue"
                else:
                    cor = "black"
                linhas_coloridas.append(f'<font color="{cor}">{linha.strip()}</font>')
    return linhas_coloridas

# ROTA PRINCIPAL - Página com ovos flutuantes
@bp.route("/")
def home():
    return render_template("index.html", title="🥚 Central de Chat")

@bp.route("/cliente", methods=["GET", "POST"])
def usuario():
    if "chat_id" not in session:
        session["chat_id"] = datetime.now().strftime("%Y%m%d-%H%M%S")
        registrar_log("SISTEMA", f"=== Início da Sessão {session['chat_id']} ===", session["chat_id"])

    if request.method == "POST":
        if "enviar" in request.form:
            msg = request.form["mensagem"]
            registrar_log("CLIENTE", msg, session["chat_id"])

            # Se for uma pergunta, consulta o Gemini
            if msg.strip().endswith("?"):
                resposta = fn_rag(msg)
                time.sleep(30)
                resposta_juiz = fn_juiz(msg, resposta)

                # após verificar se ocorreu alucinação, gravar a resposta no log da sessão
                registrar_log("GEMINI", resposta, session["chat_id"])
                registrar_log("GEMINI", resposta_juiz, session["chat_id"])
        elif "encerrar" in request.form:
            registrar_log("SISTEMA", f"=== Fim da Sessão {session['chat_id']} ===", session["chat_id"])
            session.pop("chat_id", None)
    historico = carregar_historico()
    return render_template("cliente.html", historico=historico, title="Chat - Cliente")

@bp.route("/especialista", methods=["GET", "POST"])
def atendente():
    if "chat_id" not in session:
        session["chat_id"] = datetime.now().strftime("%Y%m%d-%H%M%S")
        registrar_log("SISTEMA", f"=== Início da Sessão {session['chat_id']} ===", session["chat_id"])

    if request.method == "POST":
        if "enviar" in request.form:
            msg = request.form["mensagem"]
            registrar_log("ESPECIALISTA", msg, session["chat_id"])
        elif "encerrar" in request.form:
            registrar_log("SISTEMA", f"=== Fim da Sessão {session['chat_id']} ===", session["chat_id"])
            session.pop("chat_id", None)
    historico = carregar_historico()
    return render_template("especialista.html", historico=historico, title="Chat - Especialista")

@bp.route("/piada")
def piada():
    texto = piadas_ovo()
    return jsonify({"piada": texto})
