# =============================================================================
# PASSO 1 — IMPORTAÇÃO DAS BASES BRUTAS
# -----------------------------------------------------------------------------
# Este bloco só LÊ os arquivos como foram baixados. Nenhuma limpeza é feita
# aqui: linhas "Brasil", "Ignorado", "Total", o "-" do Tabnet e a separação
# código/nome ficam para os passos seguintes.
#
# Código escrito com auxílio de IA (Claude), dentro da exceção prevista nas
# orientações da disciplina (etapa 3.2: código de importação).
# =============================================================================

from pathlib import Path

import pandas as pd

# Pasta das bases, montada a partir do local DESTE arquivo (__file__).
# Assim o script encontra os dados de qualquer pasta de onde for rodado
# (terminal, VS Code, Code Runner...), desde que a estrutura seja:
#   trabalho_econo/importacao.py
#   trabalho_econo/dados/brutos/<arquivos>
PASTA = Path(__file__).parent / "dados" / "brutos"


# --- 1. Óbitos por lesões autoprovocadas, por microrregião (DATASUS/Tabnet, 2019)
# Arquivo de texto com colunas separadas por ";" e codificação Latin-1
# (por isso os acentos quebram se lido como UTF-8).
# skiprows=4   -> pula as 4 linhas de título; a 5ª linha vira o nome das colunas
# skipfooter=7 -> pula as 7 linhas de fonte/notas depois da linha "Total"
# engine="python" -> o skipfooter só funciona com esse leitor
# dtype=str    -> lê tudo como texto (o "-" e os códigos ficam intactos)
obitos = pd.read_csv(
    PASTA / "suicidio.csv",
    sep=";",
    encoding="latin-1",
    skiprows=4,
    skipfooter=7,
    engine="python",
    dtype=str,
)
obitos.columns = ["microrregiao", "obitos"]


# --- 2. Participação de cada setor no VAB, por microrregião (IBGE/SIDRA, tab. 5938, 2019)
# Cada setor está numa aba diferente. Passar uma lista em sheet_name devolve
# um dicionário {nome_da_aba: tabela}.
# header=None  -> não usa nenhuma linha como nome de coluna (o cabeçalho do
#                 SIDRA ocupa várias linhas e confunde o pandas)
# skiprows=4   -> pula as 4 linhas de título; a primeira linha lida é "Brasil"
# skipfooter=1 -> pula a linha "Fonte: IBGE..."
# As colunas do arquivo são: código, nome, valor 2019, unidade (%), valor 2023
# (2023 vem como "..." porque o IBGE não divulgou VAB setorial para esse ano).
vab = pd.read_excel(
    PASTA / "VAB.xlsx",
    sheet_name=["AGRO", "IND", "SERV", "ADM"],
    header=None,
    skiprows=4,
    skipfooter=1,
    names=["cod_micro", "nome", "valor_2019", "unidade", "valor_2023"],
    dtype={"cod_micro": str},
)
# Ex.: vab["AGRO"] é a tabela da agropecuária


# --- 3. População residente e homens, por município (IBGE/SIDRA, tab. 9514, Censo 2022)
# skiprows=6   -> pula as 6 linhas de título; a primeira linha lida já é um município
# skipfooter=1 -> pula a linha "Fonte"
# Colunas: código (7 dígitos), nome (UF), forma de declaração da idade, total, homens
homem = pd.read_excel(
    PASTA / "Homem.xlsx",
    sheet_name="Tabela",
    header=None,
    skiprows=6,
    skipfooter=1,
    names=["cod_mun", "nome", "forma_declaracao", "pop_total", "homens"],
    dtype={"cod_mun": str},
)


# --- 4. População por cor ou raça, por município (IBGE/SIDRA, tab. 9605, Censo 2022)
# skiprows=5   -> pula as 5 linhas de título; a primeira linha lida é "Brasil"
# skipfooter=1 -> pula a linha "Fonte"
raca = pd.read_excel(
    PASTA / "Raca.xlsx",
    sheet_name="Tabela",
    header=None,
    skiprows=5,
    skipfooter=1,
    names=["cod_mun", "nome", "total", "branca", "preta", "amarela", "parda", "indigena"],
    dtype={"cod_mun": str},
)


# --- 5. IFDM Emprego & Renda, por município (FIRJAN, série histórica 2013–2023)
# Aqui a primeira linha já é o cabeçalho, então não precisa pular nada.
# A planilha tem uma aba por dimensão do índice; usamos só Emprego & Renda.
ifdm = pd.read_excel(
    PASTA / "IFDM.xlsx",
    sheet_name="IFDM Emprego&Renda",
    dtype={"COD_MUNIC": str},
)


# --- 6. DTB 2019 — correspondência município -> microrregião (IBGE)
# Arquivo .xls (formato antigo do Excel): o pandas precisa do pacote xlrd
# para ler. Se der erro pedindo xlrd, rode no terminal:  pip install xlrd
# dtype=str em todas as colunas preserva os zeros à esquerda (ex.: "011").
dtb = pd.read_excel(
    PASTA / "dtb.xls",
    dtype=str,
)


# --- 7. População residente estimada, por município (DATASUS/Tabnet, RIPSA, 2019)
# Mesmo formato do arquivo de óbitos: texto, ";" e Latin-1.
# skiprows=3   -> pula as 3 linhas de título; a 4ª vira o nome das colunas
# skipfooter=8 -> pula as 8 linhas de fonte/notas depois da linha "Total"
populacao = pd.read_csv(
    PASTA / "populacao.csv",
    sep=";",
    encoding="latin-1",
    skiprows=3,
    skipfooter=8,
    engine="python",
    dtype=str,
)
populacao.columns = ["municipio", "pop_2019"]


# --- Conferência rápida: dimensões e primeiras/últimas linhas de cada base
bases = {"obitos": obitos, "populacao": populacao, "homem": homem, "raca": raca, "ifdm": ifdm, "dtb": dtb}
bases.update({f"vab_{k}": v for k, v in vab.items()})

for nome, df in bases.items():
    print(f"\n===== {nome}: {df.shape[0]} linhas x {df.shape[1]} colunas")
    print(df.head(3))
    print(df.tail(2))
