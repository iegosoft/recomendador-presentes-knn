import logging
import os

from flask import Flask, jsonify, render_template, request

from recommender import OCASIAO_SEM_PREFERENCIA, OCASIOES_VOCABULARIO, TAGS_VOCABULARIO, GiftRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
recomendador = GiftRecommender()

GENEROS_VALIDOS = {"Masculino", "Feminino", "Unissex"}
OCASIOES_VALIDAS = set(OCASIOES_VOCABULARIO) | {OCASIAO_SEM_PREFERENCIA}


@app.route("/")
def index():
    return render_template(
        "index.html",
        tags=TAGS_VOCABULARIO,
        ocasioes=OCASIOES_VOCABULARIO,
        ocasiao_sem_preferencia=OCASIAO_SEM_PREFERENCIA,
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/recomendar", methods=["POST"])
def recomendar():
    dados = request.get_json(silent=True) or {}

    erro = _validar_dados(dados)
    if erro:
        logger.info("requisicao invalida em /api/recomendar: %s", erro)
        return jsonify({"erro": erro}), 400

    resultados, orcamento_ampliado = recomendador.recomendar(
        idade=dados["idade"],
        genero=dados["genero"],
        orcamento=dados["orcamento"],
        ocasiao=dados["ocasiao"],
        interesses=dados["interesses"],
    )

    resposta = {"resultados": resultados}
    if resultados and orcamento_ampliado:
        resposta["aviso"] = "Ampliamos a busca para encontrar presentes dentro do seu orçamento."

    return jsonify(resposta)


def _validar_dados(dados):
    idade = dados.get("idade")
    orcamento = dados.get("orcamento")
    genero = dados.get("genero")
    ocasiao = dados.get("ocasiao")
    interesses = dados.get("interesses")

    if not isinstance(idade, (int, float)) or isinstance(idade, bool) or not (0 < idade <= 120):
        return "idade deve ser um número entre 1 e 120"
    if not isinstance(orcamento, (int, float)) or isinstance(orcamento, bool) or orcamento <= 0:
        return "orçamento deve ser um número maior que zero"
    if genero not in GENEROS_VALIDOS:
        return "gênero inválido"
    if ocasiao not in OCASIOES_VALIDAS:
        return "ocasião inválida"
    if not isinstance(interesses, list) or len(interesses) == 0:
        return "selecione ao menos um interesse"
    if not all(isinstance(tag, str) and tag in TAGS_VOCABULARIO for tag in interesses):
        return "um ou mais interesses são inválidos"
    return None


@app.errorhandler(404)
def nao_encontrado(_erro):
    if request.path.startswith("/api/"):
        return jsonify({"erro": "rota não encontrada"}), 404
    return "Página não encontrada.", 404


@app.errorhandler(500)
def erro_interno(erro):
    logger.exception("erro interno nao tratado", exc_info=erro)
    if request.path.startswith("/api/"):
        return jsonify({"erro": "erro interno no servidor"}), 500
    return "Erro interno no servidor.", 500


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug, host=host, port=port)
