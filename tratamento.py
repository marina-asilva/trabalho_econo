import pandas as pd 
from importacao import obitos, populacao, homem, raca, dtb, vab, ifdm

# Conferências (comentadas para não poluir a saída; descomentar para rodar)


def separar_nome(tabela, coluna):
    """Recebe uma tabela e o nome da coluna com 'CODIGO NOME' e devolve a tabela com duas colunas novas."""
    tabela[["cod", "nome"]] = tabela[coluna].str.split(" ", n=1, expand=True)
    return tabela
obitos = separar_nome(obitos,"microrregiao")
populacao = separar_nome(populacao,"municipio")
#print(obitos.head())
#print(obitos.tail(10))
#print(populacao.head())
#print(populacao.tail(10))

#PADRONIZANDO CODIGOS DE MUNICIPIO E MICROREGIAO
def padronizar_codigo (tabela,coluna):
    """Recebe uma tabela e o nome da coluna com codigo de municipio com 7 digitos e devolve a tabela com uma coluna a mais com 6 """
    tabela["cod_mun_6"] = tabela[coluna].str[:6]
    return tabela 
homem=padronizar_codigo(homem,"cod_mun")
raca=padronizar_codigo(raca,"cod_mun")
dtb=padronizar_codigo(dtb,"Código Município Completo")
#for nome,tabela in {"homem":homem,"raca":raca,"dtb":dtb}.items():
   #print(nome,tabela.head())
   #print(nome,tabela.tail(10))
#print(dtb.dtypes)
#print(dtb["Microrregião Geográfica"].str.len().value_counts())
dtb["chave"] = dtb["UF"] + dtb["Microrregião Geográfica"] # Cria código completo de microrregiao no dtb(com 5 digitos), porque essa tabela separava uf e 3 codigos de microrregiao
#print(dtb)

#TRATANDO POPULACAO

#print(populacao)
#print((populacao["pop_2019"] == "-").sum())

#filtrada = populacao[populacao["nome"].str.contains("IGNORADO", na=False)]
#print(len(filtrada))  

#print(populacao.columns)
#print(populacao["cod"])
#print(populacao["pop_2019"])
total1 = populacao["cod"] == "Total"
traco = populacao["pop_2019"] == "-"
populacao = populacao[~(total1|traco)].copy()
populacao["pop_2019"] = populacao["pop_2019"].astype(int)
#print(populacao)
populacao = populacao.rename(columns={"cod": "cod_mun_6"})

#TRATANDO RACA
raca = raca.drop(index = [0])

#ASSOCIANDO MUNICIPIOS E MICRORREGIOES
def merge_municipio (tabela):
    ref = dtb[["cod_mun_6", "chave"]].drop_duplicates() #apenas retirando duplicatas, normal
    res = tabela.merge(ref, on = "cod_mun_6", how = "left", validate = "m:1", indicator = True) #funcao de merge -> funciona como procv
    fora = ~tabela["cod_mun_6"].isin(ref["cod_mun_6"])    # essa linha foi usada para conferir quais linhas nao estavam no merge -> com ela descobrimos que a primeira linha da raca sao informacoes do brasil, por isso tratamos raca no bloco de cima
    #print(res["_merge"].value_counts()) # isso eh continuacao da conferencia que esta no def 
    #print(tabela[fora]) # isso eh continuacao da conferencia que esta no def 
    return res 

#for nome,tabela in {"homem":homem,"raca":raca,"populacao":populacao}.items(): # isso eh continuacao da conferencia que esta no def 
    #print(nome)
    #merge_municipio(tabela)
raca=merge_municipio(raca)
homem=merge_municipio(homem)
populacao=merge_municipio(populacao)
#for nome,tabela in {"homem":homem,"raca":raca,"populacao":populacao}.items(): # confere se deu certo as mudancas de variavel depois do merge
   #print(nome,tabela.head())
   #print(nome,tabela.tail(10))

#TRATANDO OBITOS
obitos["obitos"] = obitos["obitos"].replace("-", "0") 
obitos["obitos"] = obitos["obitos"].astype(int)
ignorado = obitos["cod"] == "Ignorado"
obitos_ignorado = obitos[ignorado].copy()
obitos_ignorado = obitos_ignorado.drop(columns=["microrregiao"])
obitos_ignorado["nome"] = obitos_ignorado["nome"].str[-2:]
#print(obitos_ignorado)
total = obitos["cod"] == "Total"
obitos = obitos[~(total|ignorado)].copy()
#print(obitos)

#soma_a = obitos["obitos"].sum()    
#soma_b = obitos_ignorado["obitos"].sum()      
#print(soma_a + soma_b)   
divisor2019 = populacao.groupby("chave")["pop_2019"].sum()
#print(populacao.groupby("chave")["pop_2019"].sum()) 
mortes = obitos.set_index("cod")["obitos"]          # série indexada por cod
#print(mortes/ divisor2019 * 100_000)  
taxa_obito = mortes/ divisor2019 * 100_000
