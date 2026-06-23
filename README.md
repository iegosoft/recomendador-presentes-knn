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

Para desenvolver (com `pytest`), instale as dependências de desenvolvimento
em vez disso:

```bash
pip install -r requirements-dev.txt
```

## Como rodar

```bash
python app.py
```

A aplicação fica disponível em `http://localhost:5000`.

### Variáveis de ambiente

| Variável      | Padrão      | Descrição                                  |
|---------------|-------------|---------------------------------------------|
| `FLASK_DEBUG` | `false`     | `true` ativa o modo debug do Flask (recarga automática e depurador interativo — nunca use em produção) |
| `HOST`        | `127.0.0.1` | endereço em que o servidor escuta           |
| `PORT`        | `5000`      | porta em que o servidor escuta              |

### Rodando em produção

O servidor embutido do Flask (`python app.py`) é só para desenvolvimento.
Em produção, sirva a aplicação com um servidor WSGI como o
[Gunicorn](https://gunicorn.org/):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

O endpoint `GET /health` devolve `{"status": "ok"}` e pode ser usado como
healthcheck por um orquestrador (Docker, Kubernetes, etc.).

## Como rodar os testes

```bash
pytest
```

O workflow em `.github/workflows/testes.yml` roda essa mesma suíte
automaticamente em cada push e pull request para `main`.

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

### 2. Ranqueamento por coeficiente de sobreposição (KNN + cosseno)

Cada presente do catálogo é representado por um vetor multi-hot com uma
posição para cada tag do vocabulário (a ocasião **não** entra nesse
vetor — ver por quê mais abaixo). O perfil informado no formulário é
convertido para o mesmo formato a partir dos interesses escolhidos.

O `NearestNeighbors` do scikit-learn (`metric="cosine"`) busca, entre os
itens já filtrados, um pool de candidatos bem maior do que o número de
resultados exibidos (20x — precisa ser grande porque o catálogo tem
várias variantes de preço/estilo com tags idênticas). Esse pool é só a
busca inicial — a porcentagem de compatibilidade exibida **não** é a
similaridade de cosseno simétrica nem a cobertura simples do perfil. O
projeto passou por três formulações até chegar na atual, e vale registrar
o porquê de cada uma não ser suficiente:

1. **Cosseno simétrico** penaliza um item por ter características extras
   que o usuário nem pediu (um item com 10 tags compartilhando 2 com o
   perfil pontua pior que um item com só essas 2 tags) — presentes
   genuinamente bons saíam com porcentagens baixas e arbitrárias.
2. **Cobertura do perfil** (`overlap / |perfil|`) resolve o problema 1,
   mas cria outro: quanto mais interesses o usuário marca, maior fica o
   denominador, e mais difícil qualquer item pontuar bem. Cobrir 2 de 5
   interesses escolhidos virava só 40%, mesmo que o item fosse perfeito
   pra esses 2 especificamente — era esse o motivo de a busca devolver
   lista vazia quando os interesses marcados eram de categorias muito
   diferentes entre si (nenhum presente cobre 5 categorias ao mesmo
   tempo, e não deveria precisar cobrir).
3. **Coeficiente de sobreposição** (*overlap coefficient* / Szymkiewicz–
   Simpson), a versão atual: `overlap / min(|perfil|, |item|)`. Dividir
   pelo *menor* dos dois conjuntos resolve os dois problemas ao mesmo
   tempo — um item pequeno e focado que bate 100% com 2 dos interesses
   marca 100%, porque ele esgota a própria capacidade nesses 2,
   **independente de quantos outros interesses o usuário também tenha
   marcado**. E um item com tags extras irrelevantes ainda marca 100%
   quando cobre tudo que o perfil pede.

A ocasião conta como um **bônus** de 5 pontos (`BONUS_OCASIAO`) quando o
item também serve para a ocasião escolhida, em vez de entrar no mesmo
vetor dos interesses. Ela foi deliberadamente tirada do vetor principal:
a maioria dos itens do catálogo serve para várias ocasiões ao mesmo
tempo, e colocar isso no mesmo cálculo fazia esse "servir para várias
ocasiões" ser tratado como característica extra irrelevante, inflando a
base de comparação do item e empurrando a compatibilidade pra baixo de
forma artificial.

### 3. Piso mínimo de confiança

Nenhuma recomendação é exibida com menos de 58% de compatibilidade
(`MIN_COMPATIBILIDADE` em `recommender.py`). Itens abaixo disso são
descartados antes mesmo de chegar à etapa de diversidade — o sistema
prefere devolver uma lista menor (ou vazia, com o estado correspondente
no front-end) a preencher os resultados com presentes de baixa relação
com o que foi pedido só para completar a grade. Como a compatibilidade
agora é o coeficiente de sobreposição (e não mais a cobertura simples),
esse piso deixa de penalizar quem marca vários interesses de categorias
diferentes — basta que o item bata bem com *pelo menos um* deles. O que
ainda fica de fora são correspondências fracas mesmo dentro de um único
interesse (um item que só compartilha uma tag secundária, por exemplo) —
o sistema não finge uma confiança que não tem.

### 4. Diversidade e desempate

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

### 5. Fallback para perfil sem correspondência

Se o vetor de perfil (interesses) resultar todo zerado, o sistema não
tenta calcular cobertura — cai num fallback que ordena os itens filtrados
pela proximidade ao orçamento informado, sem gerar erro. Na prática isso
só acontece chamando `GiftRecommender.recomendar` diretamente com tags
fora do vocabulário, já que a API valida os interesses antes de chegar
aqui.
