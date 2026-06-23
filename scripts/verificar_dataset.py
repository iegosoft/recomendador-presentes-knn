import pandas as pd

COLUNAS_ESPERADAS = [
    "id",
    "nome",
    "categoria",
    "preco",
    "idade_min",
    "idade_max",
    "genero",
    "ocasiao",
    "tags",
]

df = pd.read_csv("data/presentes.csv")

assert list(df.columns) == COLUNAS_ESPERADAS, "colunas inesperadas no CSV"
assert len(df) >= 1500, "menos de 1500 itens no catalogo"

print(f"OK: {len(df)} itens carregados, {len(df.columns)} colunas.")
print(f"Categorias: {df['categoria'].nunique()}")
