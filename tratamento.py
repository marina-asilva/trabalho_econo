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
    #fora = ~tabela["cod_mun_6"].isin(ref["cod_mun_6"])    # essa linha foi usada para conferir quais linhas nao estavam no merge -> com ela descobrimos que a primeira linha da raca sao informacoes do brasil, por isso tratamos raca no bloco de cima
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
#   print(nome,tabela.head())
#   print(nome,tabela.tail(10))
#print(raca.columns)
#print(homem.columns)
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
divisor2019 = populacao.groupby("chave")["pop_2019"].sum() # soma a populacao do municipio (que esta em pop_2019) para cada uma das microregioes
#print(populacao.groupby("chave")["pop_2019"].sum()) 
mortes = obitos.set_index("cod")["obitos"]          # série indexada por cod
#print(mortes/ divisor2019 * 100_000)  
taxa_obito = mortes/ divisor2019 * 100_000
#CHECANDO SE A TABELA DE RACA E GENERO TEM A MESMA POPULACAO TOTAL

#print(raca["cod_mun_6"].dtypes)
#print(raca["total"].dtypes)
#print(homem["cod_mun_6"].dtypes)
#print(homem["pop_total"].dtypes)
#s1 = homem.set_index("cod_mun_6")["pop_total"].sort_index()     # chave vira índice, depois ordena
#s2 = raca.set_index("cod_mun_6")["total"].sort_index()
#print(s1.equals(s2))       
#dif = s1 != s2         máscara: True onde os valores diferem 
#print(dif.sum())  
#print(pd.concat([s1, s2], axis=1)[dif])   #mostra só as linhas que diferem, lado a lado
divisor2022 = raca.groupby("chave")["total"].sum()
#TRATAMENTO HOMEM 
n_homem =  homem.groupby("chave")["homens"].sum()
taxa_homem = n_homem / divisor2022 
#print(taxa_homem)
#TRATAMENTO RACA2
#Procurando o erro de objct para não rodar os dicionarios e definicao de variaveis
#print(raca.dtypes)
#conv = pd.to_numeric(raca["indigena"], errors="coerce")
#print(raca.loc[conv.isna(),["indigena"]])
#conv = pd.to_numeric(raca["amarela"], errors="coerce")
#print(raca.loc[conv.isna(),["amarela"]])
#Rodando isso descobrimos que era os tracos, que vamos trocar por 0

raca[["indigena","amarela"]] = raca[["indigena","amarela"]].replace("-", 0)
raca[["indigena","amarela"]] = raca[["indigena","amarela"]].astype(int)
cor = {}
for nome in ["branca", "preta", "amarela", "parda", "indigena"]:
  cor[nome] = raca.groupby("chave")[nome].sum()

resultado = {}
for nome, cores in cor.items():
  resultado[nome] = cores / divisor2022
#print(resultado)

#TRATAMENTO VAB 
#peguei codigo do importacao para entender como ele importava a tabela vab
#vab = pd.read_excel(
    #PASTA / "VAB.xlsx",
   # sheet_name=["AGRO", "IND", "SERV", "ADM"],
   # header=None,
    #skiprows=4,
   # skipfooter=1,
   # names=["cod_micro", "nome", "valor_2019", "unidade", "valor_2023"],
   # dtype={"cod_micro": str},
#A ideia foi primeiro testar o codigo sozinho e depois colocar no looping
#copia_vab = vab["AGRO"].copy()
#print(copia_vab.head())
#print(copia_vab.shape, copia_vab.dtypes)
#copia_vab = copia_vab.drop(index = [0])
#copia_vab["valor_2019"] = copia_vab["valor_2019"].astype(float)
#agro = copia_vab.set_index("cod_micro")["valor_2019"]
copia_vab = {}
for setor in ["AGRO", "IND", "SERV", "ADM"]:
   temp =vab[setor].copy()
   temp = temp.drop(index = [0])
   temp["valor_2019"] = temp["valor_2019"].astype(float)
   temp["valor_2019"] = temp["valor_2019"]/100
   copia_vab[setor] = temp.set_index("cod_micro")["valor_2019"]
#print(copia_vab.items())
