# Dataset — Catálogo de Presentes

## Arquivo

`data/presentes.csv`

## Volume e estrutura

O catálogo contém **1.512 itens**, gerados a partir de 72 produtos-base por meio de variações sistemáticas de estilo e faixa de preço.

### Colunas do CSV

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | inteiro | Identificador único do item |
| `nome` | texto | Nome do produto (inclui estilo e linha de preço) |
| `categoria` | texto | Categoria principal do produto |
| `preco` | número | Preço em reais (R$) |
| `idade_min` | inteiro | Idade mínima recomendada do destinatário |
| `idade_max` | inteiro | Idade máxima recomendada do destinatário |
| `genero` | texto | `Masculino`, `Feminino` ou `Unissex` |
| `ocasiao` | texto | Ocasiões separadas por `;` (ex: `Aniversário;Natal`) |
| `tags` | texto | Tags de interesse separadas por `;` (ex: `fitness;bem-estar`) |

### Faixa de preços

| Indicador | Valor |
|---|---|
| Mínimo | R$ 15 |
| Mediana | aproximadamente R$ 154 |
| Máximo | aproximadamente R$ 2.970 |

## Categorias disponíveis (12)

- Tecnologia
- Livros
- Moda
- Beleza & Bem-estar
- Esportes & Fitness
- Jogos
- Culinária
- Música
- Arte & Artesanato
- Viagem
- Pets
- Casa & Decoração

## Ocasiões disponíveis (9 + sem preferência)

- Aniversário, Amigo Secreto, Natal, Formatura
- Dia das Mães, Dia dos Pais, Casamento
- Dia dos Namorados, Chá de Bebê
- Sem ocasião específica

## Como o catálogo foi gerado

O script `scripts/gerar_dataset.py` parte de **72 produtos-base** cuidadosamente escolhidos para representar bem todas as categorias e combinações de tags. Cada produto-base é então expandido em **21 variantes** pela combinação de:

- **3 estilos**: Vintage, Industrial, Minimalista
- **7 faixas de preço**:

| Linha | Multiplicador | Descrição |
|---|---|---|
| Linha Popular | 0,27 | Preço mínimo acessível (a partir de R$ 15) |
| Linha Econômica | 0,40 | Opção de entrada |
| Linha Essencial | 0,55 | Preço intermediário baixo |
| Versão Compacta | 0,75 | Abaixo do preço-base |
| Edição Padrão | 1,00 | Preço-base original |
| Linha Premium | 1,30 | Versão superior |
| Edição Limitada | 1,65 | Versão top de linha |

O preço de cada variante é calculado como `round(preco_base × multiplicador)`.

**Total de itens:** 72 produtos-base × 3 estilos × 7 faixas = **1.512 itens**

Todas as variantes de um mesmo produto-base compartilham as mesmas tags e ocasiões. Por isso, o algoritmo inclui uma etapa de **deduplicação** que mantém apenas um representante por combinação de (categoria, conjunto de tags) antes de aplicar a seleção por diversidade.
