from flask import Flask, jsonify, render_template, request

from recommender import OCASIAO_SEM_PREFERENCIA, OCASIOES_VOCABULARIO, TAGS_VOCABULARIO, GiftRecommender

app = Flask(__name__)
recomendador = GiftRecommender()


@app.route("/")
def index():
    return render_template(
        "index.html",
        tags=TAGS_VOCABULARIO,
        ocasioes=OCASIOES_VOCABULARIO,
        ocasiao_sem_preferencia=OCASIAO_SEM_PREFERENCIA,
    )


@app.route("/api/recomendar", methods=["POST"])
def recomendar():
    dados = request.get_json(silent=True) or {}

    erro = _validar_dados(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    resultados, orcamento_ampliado = recomendador.recomendar(
        idade=dados["idade"],
        genero=dados.get("genero", ""),
        orcamento=dados["orcamento"],
        ocasiao=dados.get("ocasiao", ""),
        interesses=dados["interesses"],
    )

    resposta = {"resultados": resultados}
    if resultados and orcamento_ampliado:
        resposta["aviso"] = "Ampliamos a busca para encontrar presentes dentro do seu orcamento."

    return jsonify(resposta)


def _validar_dados(dados):
    idade = dados.get("idade")
    orcamento = dados.get("orcamento")
    interesses = dados.get("interesses")

    if not isinstance(idade, (int, float)) or isinstance(idade, bool) or idade <= 0:
        return "idade deve ser um numero maior que zero"
    if not isinstance(orcamento, (int, float)) or isinstance(orcamento, bool) or orcamento <= 0:
        return "orcamento deve ser um numero maior que zero"
    if not isinstance(interesses, list) or len(interesses) == 0:
        return "selecione ao menos um interesse"
    return None


if __name__ == "__main__":
    app.run(debug=True)
