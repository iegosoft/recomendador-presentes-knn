# O Modelo de Recomendação

Esta é a parte central do projeto, onde álgebra linear, KNN e métricas de similaridade se juntam para produzir recomendações personalizadas.

---

## 1. Representação vetorial dos dados (Multi-hot Encoding)

O primeiro passo é transformar informações qualitativas — os interesses de quem vai receber o presente e as tags de cada item do catálogo — em números que possam ser comparados matematicamente.

O projeto define um vocabulário fixo de **19 tags** (interesses possíveis):

```
tecnologia, fitness, viagem, musica, fotografia, arte,
jogos, leitura, culinaria, moda, beleza, bem-estar,
esportes, cafe, vinho, artesanato, decoracao, jardinagem, pets
```

Cada tag ocupa uma posição fixa nesse vocabulário. Um item ou perfil é representado como um **vetor binário de 19 dimensões** — 1 se aquela tag está presente, 0 se não está. Esse tipo de codificação é chamado de **multi-hot encoding**.

**Exemplo — item "Tapete de yoga":**
```
tags: fitness, bem-estar, esportes
vetor: [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
         ^tecnologia  ^fitness              ^bem-estar ^esportes
```

**Exemplo — perfil do usuário com interesses em fitness e esportes:**
```
interesses: fitness, esportes
vetor: [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
```

Com isso, tanto o perfil quanto cada item do catálogo existem no **mesmo espaço vetorial de 19 dimensões**, o que permite calcular a similaridade entre eles.

---

## 2. K-Vizinhos Mais Próximos (KNN) — busca dos candidatos

Com os vetores definidos, o algoritmo usa **K-Nearest Neighbors (KNN)** para encontrar os itens do catálogo mais próximos do perfil do usuário.

O KNN é um algoritmo não-paramétrico de aprendizado de máquina: em vez de criar um modelo treinado com pesos, ele simplesmente procura no espaço vetorial quais pontos estão mais perto de um ponto de consulta. Neste projeto, o ponto de consulta é o vetor de interesses do usuário, e os pontos do catálogo são os vetores de tags de cada item.

**Implementação (em `recommender.py`):**
```python
from sklearn.neighbors import NearestNeighbors

tamanho_pool = min(len(candidatos), top_n * MULTIPLICADOR_POOL)
modelo = NearestNeighbors(metric="cosine", n_neighbors=tamanho_pool)
modelo.fit(matriz_candidatos)  # matriz_candidatos: shape (N_itens, 19)
_, posicoes = modelo.kneighbors([perfil_tags])  # perfil_tags: shape (19,)
```

O parâmetro `metric="cosine"` faz com que o KNN use a **distância cosseno** internamente para determinar quais itens são os mais próximos. O resultado são os índices dos `tamanho_pool` itens mais similares ao perfil, em ordem crescente de distância (ou seja, ordem decrescente de similaridade).

---

## 3. Similaridade de Cosseno — a métrica de distância

A **similaridade de cosseno** mede o ângulo entre dois vetores. Ela responde a pergunta: *esses dois vetores apontam na mesma direção?*

A fórmula é:

```
cos(θ) = (A · B) / (‖A‖ × ‖B‖)
```

Onde:
- `A · B` é o **produto interno** (dot product) entre os vetores
- `‖A‖` e `‖B‖` são as **normas** (comprimentos) de cada vetor
- O resultado varia de **0** (vetores perpendiculares — nenhuma similaridade) a **1** (vetores paralelos — similaridade total)

**Conexão com álgebra linear:** o produto interno `A · B` é exatamente o que você estudou em Álgebra Linear. Para vetores binários como os deste projeto, `A · B` conta quantas tags os dois têm em comum (sobreposição). As normas `‖A‖` e `‖B‖` são as raízes quadradas do número de tags de cada um. Dividir pelo produto das normas normaliza o resultado pelo tamanho dos vetores.

**Por que cosseno e não distância euclidiana?** Com vetores binários, dois itens com muitas tags em comum mas também muitas tags diferentes teriam distância euclidiana grande, mas similaridade cosseno alta — o cosseno captura a *direção* (interesses compartilhados) e ignora a *magnitude* (quantidade de tags).

O KNN com `metric="cosine"` usa `1 - cos(θ)` como distância (para que menor distância = maior similaridade), mas o conceito é o mesmo.

---

## 4. Coeficiente de Sobreposição — a métrica exibida ao usuário

Após o KNN identificar os candidatos mais próximos, o sistema calcula a **compatibilidade exibida ao usuário**. Aqui, não é usado o cosseno bruto, mas o **Coeficiente de Sobreposição** (também chamado de Szymkiewicz-Simpson):

```
sobreposição = A · B                      (tags em comum)
compatibilidade = sobreposição / min(‖A‖², ‖B‖²)
```

Onde A é o vetor do item e B é o vetor do perfil. Como os vetores são binários, `‖V‖²` é simplesmente o número de tags do vetor V.

**Por que não usar o cosseno diretamente como porcentagem exibida?**

O cosseno simétrico traz um problema prático: ele penaliza itens que têm *tags extras* que o usuário não pediu. Um item com 10 tags, compartilhando 2 com o perfil, pontua pior do que um item com apenas essas 2 tags — mesmo sendo uma excelente opção para quem tem esses 2 interesses.

**Por que não usar cobertura pura (sobreposição / |perfil|)?**

A cobertura pura resolve o problema acima, mas cria outro: quanto mais interesses o usuário selecionar, mais difícil fica qualquer item atingir uma boa pontuação, porque o denominador cresce com o número de interesses escolhidos. Se o usuário seleciona 5 interesses de categorias diferentes (ex: tecnologia, culinária, viagem, leitura, pets), nenhum produto do mundo cobre todos os 5 — o sistema devolveria lista vazia mesmo havendo ótimas opções para cada interesse individualmente.

**O Coeficiente de Sobreposição resolve os dois problemas:**

Ao dividir pelo *menor* dos dois conjuntos, um item focado que atende 100% do que ele se propõe a cobrir recebe 100% de compatibilidade — independente de quantos outros interesses o usuário também selecionou. E itens com tags irrelevantes extras não são penalizados, porque o denominador é limitado ao menor dos dois conjuntos.

**Implementação (em `recommender.py`):**
```python
sobreposicao = float(np.dot(vetor_item, perfil_tags))
norma_item_ao_quadrado = float(np.dot(vetor_item, vetor_item))
menor_conjunto = min(norma_perfil_ao_quadrado, norma_item_ao_quadrado)
indice_sobreposicao = sobreposicao / menor_conjunto if menor_conjunto > 0 else 0.0
compatibilidade = round(min(indice_sobreposicao * 100 + bonus, 100.0), 1)
```

---

## 5. Pipeline completo do algoritmo

```
Entrada: { idade, gênero, orçamento, ocasião, interesses[] }
         ↓
1. FILTROS RÍGIDOS
   - Filtra itens por faixa etária e gênero
   - Filtra itens pelo orçamento (com tolerância progressiva: 0%, 15%, 30%)
         ↓
2. VETORIZAÇÃO DO PERFIL
   - Converte interesses em vetor multi-hot de 19 dimensões
         ↓
3. KNN COM COSSENO (scikit-learn)
   - Monta a matriz de vetores dos candidatos (N x 19)
   - Treina NearestNeighbors(metric="cosine")
   - Recupera os top (top_n × 20) candidatos mais próximos
         ↓
4. CÁLCULO DE COMPATIBILIDADE (Coeficiente de Sobreposição)
   - Para cada candidato retornado pelo KNN:
     - Calcula sobreposição via dot product
     - Divide pelo menor dos dois conjuntos
     - Aplica bônus de ocasião (+5%) se aplicável
     - Descarta itens abaixo de 58% de compatibilidade
         ↓
5. DEDUPLICAÇÃO
   - Remove variantes duplicadas do mesmo produto
     (mesma categoria + mesmas tags → mantém apenas um)
         ↓
6. SELEÇÃO COM DIVERSIDADE
   - Aplica limite de 2 itens por categoria
   - Se necessário, relaxa o limite progressivamente
   - Ordena resultado final por compatibilidade decrescente
         ↓
Saída: lista de até 6 presentes com compatibilidade exibida
```

---

## 6. Parâmetros do modelo

| Parâmetro | Valor | Descrição |
|---|---|---|
| `TAGS_VOCABULARIO` | 19 tags | Dimensão do espaço vetorial |
| `MULTIPLICADOR_POOL` | 20 | KNN retorna `top_n × 20` candidatos antes do corte |
| `MIN_COMPATIBILIDADE` | 58.0% | Piso mínimo para aparecer nos resultados |
| `BONUS_OCASIAO` | 5.0% | Bônus quando o item serve para a ocasião escolhida |
| `TOLERANCIAS_ORCAMENTO` | [0%, 15%, 30%] | Tolerâncias progressivas de orçamento |
| `MAX_ITENS_POR_CATEGORIA` | 2 | Limite de itens da mesma categoria no resultado |
| `MIN_ITENS_PARA_PARAR` | 3 | Mínimo de itens para encerrar a busca progressiva |
