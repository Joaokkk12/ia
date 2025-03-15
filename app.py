import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
from fuzzywuzzy import fuzz  # Usando fuzzywuzzy para comparação de similaridade

app = Flask(__name__)
CORS(app)

# Padrão de regex para identificar o formato de "quando eu falar"
PADRAO_PERGUNTA = r"quando eu falar (.*?), tu fala (.*)"

# Dicionário de perguntas predefinidas com suas respectivas respostas
perguntas_predefinidas = {
    "ok":"...",
    "oi": "ola! como posso ajudar hoje?",
    "como vai": "estou otimo, posso ajudar em algo?",
    "tudo bem?": "tudo, e com voce?",
    "bem": "que bom, posso ajudar em algo?",
    "olá": "ola, como posso te ajudar hoje?",
    "qual seu nome?": "reRex, e o seu?",
    "prazer em conhece-lo": "prazer, como posso te ajudar?",
    "voce um robo": "sou uma ia criada com python com respostas pre-definidas, porém posso aprender com você!",
    "obrigad": "de nada!",
    "kakaka":"kkk",
    "kkk":"kkk",
    "KAKAKA":"kkk",
    "jajajajaja":"kkk",
    
    "chatGPT":"um amigo",
    "quem te fez?":"tambem penso nisso",
    "rapunzel":"jogue seus cabelos!",
    "rapunzel o filme":"é um longa metragem de animação produzido pela Walt Disney Animation Studios. ...pode ver mais em <br><a href='https://pt.wikipedia.org/wiki/Tangled'>Wikipedia</a>"
}

# Função para carregar as respostas do JSON
def carregar_respostas():
    try:
        with open("respostas.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Função para salvar as respostas no JSON
def salvar_respostas(respostas):
    with open("respostas.json", "w") as file:
        json.dump(respostas, file, indent=4)

# Carregar as respostas personalizadas na inicialização
respostas_personalizadas = carregar_respostas()

# Função para encontrar a pergunta mais similar
def encontrar_pergunta_similar(pergunta_usuario):
    # Compara a pergunta do usuário com as perguntas predefinidas
    for pergunta, resposta in perguntas_predefinidas.items():
        similaridade = fuzz.ratio(pergunta_usuario.lower(), pergunta.lower())  # Comparação de similaridade
        if similaridade >= 80:  # Define que 80% de similaridade é suficiente
            return resposta
    
    # Verifica as perguntas salvas no JSON
    for pergunta_salva, resposta_salva in respostas_personalizadas.items():
        similaridade = fuzz.ratio(pergunta_usuario.lower(), pergunta_salva.lower())  # Comparação de similaridade
        if similaridade >= 80:
            return resposta_salva
    
    return None  # Se não encontrar nenhuma similaridade

@app.route("/salvar_resposta", methods=["POST"])
def salvar_resposta():
    data = request.get_json()
    texto = data.get("pergunta", "").strip().lower()

    print(f"Texto recebido: {texto}")  # Adicionando um print para verificar o que o servidor está recebendo

    match = re.match(PADRAO_PERGUNTA, texto)
    
    if match:
        pergunta, resposta = match.groups()
        pergunta, resposta = pergunta.strip(), resposta.strip()

        respostas_personalizadas[pergunta] = resposta
        salvar_respostas(respostas_personalizadas)  # Agora salva sempre que aprende algo novo
        
        return jsonify({"status": "sucesso", "mensagem": f"Agora, quando você disser '{pergunta}', eu responderei '{resposta}'!"})
    else:
        print("Formato inválido!")  # Verificando se o formato não está batendo com a regex
        return jsonify({"status": "erro", "mensagem": "Formato inválido! Use: 'quando eu falar [pergunta], tu fala [resposta]'."})

@app.route("/perguntar", methods=["POST"])
def perguntar():
    data = request.get_json()
    pergunta_usuario = data.get("pergunta", "").lower().strip()

    # Tenta encontrar uma pergunta similar
    resposta = encontrar_pergunta_similar(pergunta_usuario)

    if resposta:
        return jsonify({"resposta": resposta})
    else:
        return jsonify({"resposta": "Não sei o que é isso, mas posso aprender com você!"})

if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))
