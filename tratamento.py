import pandas as pd 
from importacao import obitos, populacao, homem, raca, dtb, vab, ifdm


print(homem["cod_mun"].dtype)
#Separando codigo e nome do municipio/microrregiao
def separar_nome(tabela, coluna):
    """Recebe uma tabela e o nome da coluna com 'CODIGO NOME' e devolve a tabela com duas colunas novas."""
    tabela[["cod", "nome"]] = tabela[coluna].str.split(" ", n=1, expand=True)
    return tabela
obitos = separar_nome(obitos,"microrregiao")
populacao = separar_nome(populacao,"municipio")
print(obitos.head())
print(obitos.tail(10))
print(populacao.head())
print(populacao.tail(10))

#Associando municipios e microrregioes 
def padronizar_codigo (tabela,coluna):
    """Recebe uma tabela e o nome da coluna com codigo de municipio com 7 digitos e devolve a tabela com uma coluna a mais com 6 """
    tabela["cod_mun_6"] = tabela[coluna].str[:6]
    return tabela 
homem=padronizar_codigo(homem,"cod_mun")
raca=padronizar_codigo(raca,"cod_mun")
dtb=padronizar_codigo(dtb,"Código Município Completo")
for nome,tabela in {"homem":homem,"raca":raca,"dtb":dtb}.items():
    print(nome,tabela.head())
    print(nome,tabela.tail(10))
