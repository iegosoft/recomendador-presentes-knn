# Recomendador de Presentes

Aplicacao web em Flask que recomenda presentes com base no perfil de quem
vai receber (idade, genero, orcamento, ocasiao e interesses), usando
similaridade de cosseno e KNN sobre um catalogo de produtos.

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

A aplicacao fica disponivel em `http://localhost:5000`.
