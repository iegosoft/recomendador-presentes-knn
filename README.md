# Recomendador de Presentes

Aplicação web em Flask que recomenda presentes com base no perfil de quem
vai receber (idade, gênero, orçamento, ocasião e interesses), usando
similaridade de cosseno e KNN sobre um catálogo de produtos.

## Como instalar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Como rodar

```bash
python app.py
```

A aplicação fica disponível em `http://localhost:5000`.

## Como rodar os testes

```bash
pytest
```

## Estrutura de pastas

```
data/             dataset simulado de presentes (presentes.csv)
templates/        template HTML da interface (index.html)
static/css/       estilos da interface
static/js/        lógica de front-end (fetch para a API)
scripts/          scripts utilitários descartáveis
tests/            testes automatizados (pytest)
recommender.py    motor de recomendação (classe GiftRecommender)
app.py            aplicação Flask e rotas
```

## Como o algoritmo funciona

A recomendação acontece em duas fases bem separadas: primeiro **filtros
rígidos** eliminam itens incompatíveis, depois um **ranqueamento por
similaridade** ordena o que sobrou pelo quanto combina com o perfil
informado.

### 1. Filtros rígidos

Antes de qualquer cálculo de similaridade, o catálogo é reduzido aos itens
que:

- estão dentro da faixa de idade do destinatário;
- são compatíveis com o gênero informado (itens `Unissex` sempre passam);
- cabem no orçamento.

O filtro de orçamento usa uma tolerância progressiva: tenta primeiro sem
margem nenhuma, depois com 15% e por fim com 30% de margem. A tolerância
só avança se a faixa de preço atual não tiver **nenhum item com
compatibilidade aceitável** (ver seção 3) — não basta existir algum item
qualquer dentro do preço. Essa distinção importa: a versão antiga parava
de ampliar a busca assim que encontrava 3 itens baratos de qualquer tipo,
e podia acabar recomendando algo sem nenhuma relação com os interesses só
porque cabia no orçamento original.

### 2. Ranqueamento por cobertura do perfil (KNN + cosseno)

Cada presente do catálogo é representado por um vetor multi-hot: uma
posição para cada tag do vocabulário e uma posição para cada ocasião. O
perfil informado no formulário é convertido para o mesmo formato de vetor
a partir dos interesses e da ocasião escolhidos. Quando a ocasião
escolhida é "Sem ocasião específica", a parte do vetor referente a
ocasião fica zerada e só os interesses contam.

As duas partes do vetor têm pesos diferentes: a parte de interesses pesa
o dobro da parte de ocasião (`PESO_TAGS = 1.0` contra `PESO_OCASIAO =
0.5` em `recommender.py`), porque o interesse é o sinal mais forte de que
*tipo* de presente combina com a pessoa — a ocasião é só contexto
adicional.

O `NearestNeighbors` do scikit-learn (`metric="cosine"`) busca, entre os
itens já filtrados, um pool de candidatos bem maior do que o número de
resultados exibidos (6x). Esse pool é só a busca inicial — a porcentagem
de compatibilidade exibida **não** é a similaridade de cosseno simétrica.
Cosseno padrão penaliza um item por ter características extras que o
usuário nem pediu (um item com 10 tags compartilhando 2 com o perfil
pontua pior do que um item com só essas 2 tags), o que deixava presentes
genuinamente bons com porcentagens baixas e arbitrárias. Em vez disso, a
compatibilidade exibida é a **cobertura do perfil**: que fração
(ponderada pelos mesmos pesos de tags/ocasião) do que o usuário pediu
aquele item realmente tem —
`dot(perfil, item) / dot(perfil, perfil)`. Um item que tem todas as tags e
a ocasião escolhidas marca 100%, independente de quantas outras
características ele também tenha.

### 3. Piso mínimo de confiança

Nenhuma recomendação é exibida com menos de 70% de cobertura do perfil
(`MIN_COMPATIBILIDADE` em `recommender.py`). Itens abaixo disso são
descartados antes mesmo de chegar à etapa de diversidade — o sistema
prefere devolver uma lista menor (ou vazia, com o estado correspondente
no front-end) a preencher os resultados com presentes de baixa relação
com o que foi pedido só para completar a grade.

### 5. Diversidade e desempate

Pegar só os itens mais parecidos do pool, sem mais nada, tende a devolver
uma lista dominada por uma única categoria, porque itens da mesma
categoria tendem a compartilhar tags — e o catálogo tem várias variantes
de preço do mesmo produto-base com tags idênticas, que empatam
perfeitamente em compatibilidade entre si. Por isso, antes da seleção
final: variantes do mesmo produto-base (mesma categoria e mesmas tags) são
reduzidas a uma só, mantendo a mais próxima do orçamento; depois, a
seleção limita em 2 o número de itens por categoria
(`MAX_ITENS_POR_CATEGORIA`), relaxando esse limite progressivamente só se
não houver itens suficientes de outras categorias para preencher a lista
(em vez de descartar o limite por completo). Quando duas opções têm
exatamente a mesma compatibilidade, o desempate é pela proximidade do
preço ao orçamento informado. O resultado final é sempre reordenado por
compatibilidade antes de ser devolvido.

### 6. Fallback para perfil sem correspondência

Se o vetor de perfil resultar todo zerado (nenhum interesse ou ocasião
reconhecida no vocabulário), o sistema não tenta calcular cosseno — cai
num fallback que ordena os itens filtrados pela proximidade ao orçamento
informado, sem gerar erro.
