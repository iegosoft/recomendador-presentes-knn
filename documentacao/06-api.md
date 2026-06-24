# Referência da API REST

## Endpoints

### `GET /`

Retorna a interface HTML do sistema.

**Resposta:** `200 OK` — página HTML

---

### `GET /health`

Endpoint de verificação de saúde do servidor. Útil para monitoramento e orquestradores.

**Resposta:**
```json
{"status": "ok"}
```

---

### `POST /api/recomendar`

Endpoint principal. Recebe o perfil do destinatário e retorna uma lista de presentes recomendados.

**Content-Type:** `application/json`

#### Corpo da requisição

```json
{
  "idade": 28,
  "genero": "Feminino",
  "orcamento": 200,
  "ocasiao": "Aniversário",
  "interesses": ["leitura", "cafe", "decoracao"]
}
```

| Campo | Tipo | Validação |
|---|---|---|
| `idade` | número | Entre 1 e 120 |
| `genero` | string | `"Masculino"`, `"Feminino"` ou `"Unissex"` |
| `orcamento` | número | Maior que zero |
| `ocasiao` | string | Uma das 9 ocasiões ou `"Sem ocasião específica"` |
| `interesses` | array de strings | Ao menos 1 item; cada tag deve estar no vocabulário de 19 tags |

#### Resposta de sucesso — `200 OK`

```json
{
  "resultados": [
    {
      "id": 421,
      "nome": "Romance best-seller Vintage – Edição Padrão",
      "categoria": "Livros",
      "preco": 55.0,
      "tags": ["leitura", "arte"],
      "compatibilidade": 100.0
    },
    {
      "id": 190,
      "nome": "Difusor de aromaterapia Minimalista – Versão Compacta",
      "categoria": "Beleza & Bem-estar",
      "preco": 97.5,
      "tags": ["bem-estar", "decoracao", "beleza"],
      "compatibilidade": 66.7
    }
  ]
}
```

Quando o orçamento precisou ser ampliado para encontrar resultados, um aviso é incluído:

```json
{
  "resultados": [...],
  "aviso": "Ampliamos a busca para encontrar presentes dentro do seu orçamento."
}
```

#### Resposta de erro de validação — `400 Bad Request`

```json
{"erro": "selecione ao menos um interesse"}
```

#### Resposta de rota não encontrada — `404 Not Found`

Para rotas iniciadas com `/api/`:
```json
{"erro": "rota não encontrada"}
```

## Tags disponíveis para o campo `interesses`

```
tecnologia, fitness, viagem, musica, fotografia, arte,
jogos, leitura, culinaria, moda, beleza, bem-estar,
esportes, cafe, vinho, artesanato, decoracao, jardinagem, pets
```

## Ocasiões disponíveis para o campo `ocasiao`

```
Aniversário, Amigo Secreto, Natal, Formatura, Dia das Mães,
Dia dos Pais, Casamento, Dia dos Namorados, Chá de Bebê,
Sem ocasião específica
```
