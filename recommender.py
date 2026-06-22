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

# tamanho do pool avaliado pelo KNN antes do corte por diversidade, em multiplos de top_n
MULTIPLICADOR_POOL = 6

# limite de itens da mesma categoria entre os resultados finais
MAX_ITENS_POR_CATEGORIA = 2

# nenhuma recomendacao e exibida com menos do que isso de compatibilidade
MIN_COMPATIBILIDADE = 70.0

# bonus de compatibilidade quando o item tambem serve pra ocasiao escolhida -
# a ocasiao e so contexto adicional, por isso conta como bonus e nao como
# parte do calculo principal (que e sobre os interesses)
BONUS_OCASIAO = 5.0


class GiftRecommender:
    def __init__(self, caminho_csv="data/presentes.csv"):
        self.df = pd.read_csv(caminho_csv)
        self.df["tags_lista"] = self.df["tags"].apply(self._dividir_multivalorado)
        self.df["ocasioes_lista"] = self.df["ocasiao"].apply(self._dividir_multivalorado)
        self._matriz_tags = np.array(
            [self._vetorizar_tags(tags) for tags in self.df["tags_lista"]],
            dtype=float,
        )

    @staticmethod
    def _dividir_multivalorado(valor):
        if pd.isna(valor):
            return []
        return [parte.strip() for parte in str(valor).split(";") if parte.strip()]

    @staticmethod
    def _vetorizar_tags(tags):
        return [1.0 if tag in tags else 0.0 for tag in TAGS_VOCABULARIO]

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
        elegiveis = self._filtrar_por_idade_e_genero(idade, genero)
        if elegiveis.empty:
            return [], False

        perfil_tags = np.array(self._vetorizar_tags(interesses), dtype=float)

        if not perfil_tags.any():
            candidatos, tolerancia_usada = self._filtrar_por_orcamento(elegiveis, orcamento)
            if candidatos.empty:
                return [], False
            resultados = self._recomendar_por_orcamento(candidatos, orcamento, top_n)
            return resultados, tolerancia_usada > 0

        # a tolerancia de orcamento so avanca se a faixa de preco atual nao
        # tiver nenhum item com compatibilidade aceitavel - e nao apenas "algum
        # item qualquer dentro do preco", que e o que fazia o sistema parar de
        # ampliar a busca cedo demais e devolver presentes sem relacao com os
        # interesses so porque cabiam no orcamento original.
        norma_perfil_ao_quadrado = float(np.dot(perfil_tags, perfil_tags))
        pool = []
        tolerancia_usada = 0.0
        for tolerancia in TOLERANCIAS_ORCAMENTO:
            tolerancia_usada = tolerancia
            limite = orcamento * (1 + tolerancia)
            candidatos = elegiveis[elegiveis["preco"] <= limite]
            if candidatos.empty:
                continue
            pool = self._pool_compativel(candidatos, perfil_tags, norma_perfil_ao_quadrado, ocasiao, orcamento, top_n)
            if pool:
                break

        if not pool:
            return [], False

        pool = self._remover_variantes_duplicadas(pool)
        resultados = self._selecionar_com_diversidade(pool, top_n)
        return resultados, tolerancia_usada > 0

    def _pool_compativel(self, candidatos, perfil_tags, norma_perfil_ao_quadrado, ocasiao, orcamento, top_n):
        indices = candidatos.index.to_numpy()
        matriz_candidatos = self._matriz_tags[indices]

        # NearestNeighbors com cosseno faz a busca inicial dos mais parecidos.
        # A compatibilidade exibida, porem, e a cobertura do perfil: que
        # fracao das tags escolhidas pelo usuario esse item realmente tem
        # (overlap / norma_perfil). Isso responde a pergunta que importa pro
        # usuario - "o presente tem o que eu pedi?" - sem penalizar um item
        # por ter caracteristicas extras que ele nem pediu. Um item que cobre
        # todas as tags escolhidas marca 100%, mesmo que tambem sirva pra
        # outras coisas.
        #
        # A ocasiao fica de fora desse calculo principal (que e so sobre
        # interesses) e entra como um bonus simples: a maioria dos itens do
        # catalogo serve para varias ocasioes ao mesmo tempo, e isso nao deve
        # ser tratado como "tag extra irrelevante" que penaliza o item.
        tamanho_pool = min(len(candidatos), top_n * MULTIPLICADOR_POOL)
        modelo = NearestNeighbors(metric="cosine", n_neighbors=tamanho_pool)
        modelo.fit(matriz_candidatos)
        _, posicoes = modelo.kneighbors([perfil_tags])

        ocasioes_lista = candidatos["ocasioes_lista"].to_numpy()
        usa_ocasiao = bool(ocasiao) and ocasiao != OCASIAO_SEM_PREFERENCIA

        pool = []
        for posicao in posicoes[0]:
            vetor_item = matriz_candidatos[posicao]
            sobreposicao = float(np.dot(vetor_item, perfil_tags))
            cobertura = sobreposicao / norma_perfil_ao_quadrado

            bonus = BONUS_OCASIAO if usa_ocasiao and ocasiao in ocasioes_lista[posicao] else 0.0
            compatibilidade = round(min(cobertura * 100 + bonus, 100.0), 1)

            if compatibilidade >= MIN_COMPATIBILIDADE:
                pool.append(self._formatar_item(candidatos.iloc[posicao], compatibilidade))

        pool.sort(key=lambda item: (-item["compatibilidade"], abs(item["preco"] - orcamento)))
        return pool

    @staticmethod
    def _remover_variantes_duplicadas(pool_ordenado):
        # itens com a mesma categoria e exatamente as mesmas tags sao a mesma
        # ideia de presente (ex: variantes de preco do mesmo produto) e empatam
        # em compatibilidade; manter so o mais proximo do orcamento entre eles
        # evita que eles sozinhos tomem todas as vagas do pool de diversidade.
        vistos = set()
        unicos = []
        for item in pool_ordenado:
            chave = (item["categoria"], tuple(sorted(item["tags"])))
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(item)
        return unicos

    @staticmethod
    def _selecionar_com_diversidade(pool_ordenado, top_n):
        limite = MAX_ITENS_POR_CATEGORIA

        while True:
            selecionados = []
            contagem_por_categoria = {}
            for item in pool_ordenado:
                if len(selecionados) >= top_n:
                    break
                usados = contagem_por_categoria.get(item["categoria"], 0)
                if usados < limite:
                    selecionados.append(item)
                    contagem_por_categoria[item["categoria"]] = usados + 1

            if len(selecionados) >= top_n or limite >= len(pool_ordenado):
                break
            limite += 1

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
