import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

TAGS_VOCABULARIO = [
    "tecnologia", "fitness", "viagem", "musica", "fotografia", "arte",
    "jogos", "leitura", "culinaria", "moda", "beleza", "bem-estar",
    "esportes", "cafe", "vinho", "artesanato", "decoracao", "jardinagem",
    "pets",
]

OCASIOES_VOCABULARIO = [
    "Aniversário", "Amigo Secreto", "Natal", "Formatura", "Dia das Mães",
    "Dia dos Pais", "Casamento", "Dia dos Namorados", "Chá de Bebê",
]

OCASIAO_SEM_PREFERENCIA = "Sem ocasião específica"

TOLERANCIAS_ORCAMENTO = [0.0, 0.15, 0.30]

# abaixo desse numero de itens, tenta a proxima tolerancia de orcamento
MIN_ITENS_PARA_PARAR = 3

# interesses pesam mais que a ocasiao: e o sinal mais forte de que tipo de presente combina
PESO_TAGS = 1.0
PESO_OCASIAO = 0.5

# tamanho do pool avaliado pelo KNN antes do corte por diversidade, em multiplos de top_n
MULTIPLICADOR_POOL = 4

# limite de itens da mesma categoria entre os resultados finais
MAX_ITENS_POR_CATEGORIA = 2


class GiftRecommender:
    def __init__(self, caminho_csv="data/presentes.csv"):
        self.df = pd.read_csv(caminho_csv)
        self.df["tags_lista"] = self.df["tags"].apply(self._dividir_multivalorado)
        self.df["ocasioes_lista"] = self.df["ocasiao"].apply(self._dividir_multivalorado)
        self._matriz_itens = np.array(
            [
                self._vetorizar(tags, ocasioes)
                for tags, ocasioes in zip(self.df["tags_lista"], self.df["ocasioes_lista"])
            ],
            dtype=float,
        )

    @staticmethod
    def _dividir_multivalorado(valor):
        if pd.isna(valor):
            return []
        return [parte.strip() for parte in str(valor).split(";") if parte.strip()]

    def _vetorizar(self, tags, ocasioes):
        vetor_tags = [PESO_TAGS if tag in tags else 0.0 for tag in TAGS_VOCABULARIO]
        if OCASIAO_SEM_PREFERENCIA in ocasioes:
            vetor_ocasioes = [0.0] * len(OCASIOES_VOCABULARIO)
        else:
            vetor_ocasioes = [PESO_OCASIAO if oc in ocasioes else 0.0 for oc in OCASIOES_VOCABULARIO]
        return vetor_tags + vetor_ocasioes

    def _filtrar_por_idade_e_genero(self, idade, genero):
        mascara_idade = (self.df["idade_min"] <= idade) & (self.df["idade_max"] >= idade)
        mascara_genero = (self.df["genero"] == "Unissex") | (self.df["genero"] == genero)
        return self.df[mascara_idade & mascara_genero]

    def _filtrar_por_orcamento(self, candidatos, orcamento):
        filtrado = candidatos
        tolerancia_usada = 0.0
        for tolerancia in TOLERANCIAS_ORCAMENTO:
            limite = orcamento * (1 + tolerancia)
            filtrado = candidatos[candidatos["preco"] <= limite]
            tolerancia_usada = tolerancia
            if len(filtrado) >= MIN_ITENS_PARA_PARAR:
                break
        return filtrado, tolerancia_usada

    def recomendar(self, idade, genero, orcamento, ocasiao, interesses, top_n=6):
        candidatos = self._filtrar_por_idade_e_genero(idade, genero)
        candidatos, tolerancia_usada = self._filtrar_por_orcamento(candidatos, orcamento)

        if candidatos.empty:
            return [], False

        ocasioes_perfil = [ocasiao] if ocasiao else []
        perfil = np.array(self._vetorizar(interesses, ocasioes_perfil), dtype=float)

        if not perfil.any():
            resultados = self._recomendar_por_orcamento(candidatos, orcamento, top_n)
            return resultados, tolerancia_usada > 0

        indices = candidatos.index.to_numpy()
        matriz_candidatos = self._matriz_itens[indices]

        tamanho_pool = min(len(candidatos), top_n * MULTIPLICADOR_POOL)
        modelo = NearestNeighbors(metric="cosine", n_neighbors=tamanho_pool)
        modelo.fit(matriz_candidatos)
        distancias, posicoes = modelo.kneighbors([perfil])

        pool = [
            self._formatar_item(
                candidatos.iloc[posicao], round((1 - float(distancia)) * 100, 1)
            )
            for distancia, posicao in zip(distancias[0], posicoes[0])
        ]
        pool.sort(key=lambda item: (-item["compatibilidade"], abs(item["preco"] - orcamento)))

        resultados = self._selecionar_com_diversidade(pool, top_n)
        return resultados, tolerancia_usada > 0

    @staticmethod
    def _selecionar_com_diversidade(pool_ordenado, top_n):
        selecionados = []
        contagem_por_categoria = {}

        for item in pool_ordenado:
            if len(selecionados) >= top_n:
                break
            usados = contagem_por_categoria.get(item["categoria"], 0)
            if usados < MAX_ITENS_POR_CATEGORIA:
                selecionados.append(item)
                contagem_por_categoria[item["categoria"]] = usados + 1

        if len(selecionados) < top_n:
            ids_selecionados = {item["id"] for item in selecionados}
            for item in pool_ordenado:
                if len(selecionados) >= top_n:
                    break
                if item["id"] not in ids_selecionados:
                    selecionados.append(item)

        selecionados.sort(key=lambda item: -item["compatibilidade"])
        return selecionados

    def _recomendar_por_orcamento(self, candidatos, orcamento, top_n):
        candidatos = candidatos.copy()
        candidatos["distancia_orcamento"] = (candidatos["preco"] - orcamento).abs()
        candidatos = candidatos.sort_values("distancia_orcamento").head(top_n)
        return [self._formatar_item(item, None) for _, item in candidatos.iterrows()]

    @staticmethod
    def _formatar_item(item, compatibilidade):
        return {
            "id": int(item["id"]),
            "nome": str(item["nome"]),
            "categoria": str(item["categoria"]),
            "preco": float(item["preco"]),
            "tags": list(item["tags_lista"]),
            "compatibilidade": compatibilidade,
        }


if __name__ == "__main__":
    recomendador = GiftRecommender()

    resultados, orcamento_ampliado = recomendador.recomendar(
        idade=28,
        genero="Feminino",
        orcamento=200,
        ocasiao="Aniversário",
        interesses=["leitura", "cafe", "decoracao"],
    )
    print(f"Orcamento ampliado: {orcamento_ampliado}")
    for item in resultados:
        print(f"{item['compatibilidade']}% - {item['nome']} ({item['categoria']}) - R$ {item['preco']}")

    print()

    resultados_fallback, _ = recomendador.recomendar(
        idade=35,
        genero="Masculino",
        orcamento=150,
        ocasiao=OCASIAO_SEM_PREFERENCIA,
        interesses=["tag-inexistente"],
    )
    print("Fallback por orcamento (perfil sem correspondencia nos vetores):")
    for item in resultados_fallback:
        print(f"{item['nome']} ({item['categoria']}) - R$ {item['preco']}")
