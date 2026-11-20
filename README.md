# Taxa de suicídio e composição setorial do VAB por microrregião (2019)

Trabalho empírico de **Econometria I** 

**Autoras:** Marina Andrade e Silva e Fernanda Feliciano de Oliveira.

## Pergunta e método

O trabalho estima, por MQO em cross-section, a relação entre a taxa de suicídio (por 100 mil habitantes, 2019) e a composição setorial do Valor Adicionado Bruto (VAB) das microrregiões brasileiras: agropecuária, indústria e administração pública (serviços é a categoria omitida). Os controles são os componentes do IFDM de 2019 (Emprego & Renda, Educação e Saúde), a proporção de brancos, a proporção de homens e dummies de UF.

O tratamento das bases é feito em Python (pandas). A estimação é feita em R.

## Estrutura do repositório

```
trabalho_econo/
├── importacao.py        # lê as bases brutas, sem limpeza
├── tratamento.py        # trata as bases e gera a base final
├── base_final.xlsx      # base final (abas: base, dic1, dic2)
├── requirements.txt     # pacotes de Python
└── dados/
    └── brutos/          # bases como foram baixadas
```

## Bases brutas (`dados/brutos/`)

| Arquivo | Fonte | Conteúdo | Ano |
|---|---|---|---|
| `suicidio.csv` | DATASUS/Tabnet | Óbitos por lesões autoprovocadas, por microrregião | 2019 |
| `populacao.csv` | DATASUS/Tabnet (RIPSA) | População residente estimada, por município | 2019 |
| `VAB.xlsx` | IBGE/SIDRA, tabela 5938 | Participação de cada setor no VAB, por microrregião | 2019 |
| `Homem.xlsx` | IBGE/SIDRA, tabela 9514 | População total e de homens, por município | Censo 2022 |
| `Raca.xlsx` | IBGE/SIDRA, tabela 9605 | População por cor ou raça, por município | Censo 2022 |
| `IFDM.xlsx` | FIRJAN | Índice FIRJAN de Desenvolvimento Municipal, série histórica 2013–2023 (usa-se 2019) | 2019 |
| `dtb.xls` | IBGE (DTB) | Correspondência município → microrregião | 2019 |

As bases foram baixadas manualmente dos sites das fontes.

## Base final (`base_final.xlsx`)

Uma linha por microrregião (557 microrregiões), com a chave de 5 dígitos (código da UF + 3 dígitos da microrregião) como identificador. 
*Foi esxluido DF que compõe uma microrregião, por isso há apenas 557 microrregiões. Para mais explicações conferir o relatório final

- **`base`:** as variáveis da análise e a coluna `uf`.
- **`dic1`:** o que cada coluna da aba `base` mede.
- **`dic2`:** códigos e nomes das UFs (primeiro bloco) e das microrregiões (segundo bloco).

## Como rodar

1. Instale os pacotes: `pip install -r requirements.txt`.
2. Mantenha as bases brutas em `dados/brutos/`, com os nomes da tabela acima.
3. Rode `python tratamento.py`. O script importa `importacao.py`, trata as bases e grava `base_final.xlsx`.

O `importacao.py` encontra a pasta de dados a partir do próprio local do arquivo, então pode ser rodado de qualquer diretório.

## Uso de IA

A IA (Claude, da Anthropic) foi usada nos papéis de tutora, mentora e ferramenta, conforme as orientações da disciplina. Os links públicos das conversas estão no apêndice do relatório.
