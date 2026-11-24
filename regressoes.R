#Marina Andrade e Silva ; Fernanda Feliciano de Oliveira 
#Econometria I: taxa de suicídio (2019) e composição setorial do VAB, por microrregião
#Base: base_final.xlsx 

library(AER)  
library(readxl)

# Leitura e preparo 
dados <- as.data.frame(read_excel("~/Downloads/base_final.xlsx", sheet = "base"))

dados$suic<-dados$taxa_obito
dados$agro<-dados$vab_agro
dados$ind<-dados$vab_ind
dados$serv<-dados$vab_serv
dados$adm<-dados$vab_adm
dados$er<-dados$emprego_renda
dados$edu<-dados$educacao
dados$branca<-dados$prop_branca
dados$homens<-dados$prop_homem
dados$preta<-dados$prop_preta
dados$parda<-dados$prop_parda
dados$amarela<-dados$prop_amarela
dados$indigena<-dados$prop_indigena

ufs <- sort(unique(as.character(dados$uf))) #Transforma os dados de uf em dummy
dados$uf <- factor(as.character(dados$uf), levels = c("31", ufs[ufs != "31"])) #Minas Gerais fica de fora 

# Conferência da base 
nrow(dados)
colSums(is.na(dados))
summary(dados[, c("suic", "agro", "ind", "serv", "adm", "er", "edu", "saude",
                  "branca", "homens")])
table(dados$uf)

# Modelos 
# M1: só o VAB 
m1 <- lm(suic ~ agro + ind + adm, data = dados)
summary(m1)
coeftest(m1, vcov. = vcovHC, type = "HC1")

# M2: M1 + controles 
m2 <- lm(suic ~ agro + ind + adm + er + edu + saude + branca + homens, data = dados)
summary(m2)
coeftest(m2, vcov. = vcovHC, type = "HC1")

# M3: M2 + dummies de UF
m3 <- lm(suic ~ agro + ind + adm + er + edu + saude + branca + homens + uf, data = dados)
summary(m3)
coeftest(m3, vcov. = vcovHC, type = "HC1")[1:9, ]

# Intervalo de confiança-M3 com erros robustos 
rob3 <- coeftest(m3, vcov. = vcovHC, type = "HC1")
cbind(inferior = rob3[2:4, 1] - 1.96 * rob3[2:4, 2],
      superior = rob3[2:4, 1] + 1.96 * rob3[2:4, 2])

# Heterocedasticidade 
bptest(m1)
bptest(m2)
bptest(m3)

# White simplificado- M3
resid2 <- resid(m3)^2
yhat   <- predict(m3)
yhat2  <- yhat^2
summary(lm(resid2 ~ yhat + yhat2))

#Erro-padrão comum contra robusto 
cbind(comum   = summary(m3)$coefficients[1:9, 2],
      robusto = rob3[1:9, 2])

# Testes F robustos
#Setores 
linearHypothesis(m1, c("agro", "ind", "adm"), vcov. = vcovHC(m1, type = "HC1"))
linearHypothesis(m2, c("agro", "ind", "adm"), vcov. = vcovHC(m2, type = "HC1"))
linearHypothesis(m3, c("agro", "ind", "adm"), vcov. = vcovHC(m3, type = "HC1"))

#IFDM
linearHypothesis(m3, c("er", "edu", "saude"), vcov. = vcovHC(m3, type = "HC1"))

# Dummies de UF
linearHypothesis(m3, grep("^uf", names(coef(m3)), value = TRUE),
                 vcov. = vcovHC(m3, type = "HC1"))

# Robustez
#quatro cores no lugar de apenas % branca
r1 <- lm(suic ~ agro + ind + adm + er + edu + saude + homens +
           preta + parda + amarela + indigena + uf, data = dados)

# sem os 5% de microrregiões menos populosas
corte <- quantile(dados$pop_2019, 0.05)
grandes <- droplevels(subset(dados, pop_2019 > corte))
r2 <- lm(suic ~ agro + ind + adm + er + edu + saude + branca + homens + uf,
         data = grandes)

#sem as microrregiões com taxa zero
sem_zero <- droplevels(subset(dados, suic > 0))
r3 <- lm(suic ~ agro + ind + adm + er + edu + saude + branca + homens + uf,
         data = sem_zero)

#Gráficos

library(ggplot2)   

#Distribuição 
png("fig1a_hist_taxa.png", width = 6, height = 4, units = "in", res = 300)
hist(dados$suic, breaks = 40, main = "Taxa de suicídio por microrregião, 2019",
     xlab = "Suicídios por 100 mil habitantes")
dev.off()

png("fig1b_boxplot_uf.png", width = 8, height = 4, units = "in", res = 300)
boxplot(suic ~ factor(uf, levels = sort(levels(uf))), data = dados, las = 2,
        main = "Taxa de suicídio por UF", xlab = "Código da UF",
        ylab = "Suicídios por 100 mil habitantes")
dev.off()

png("fig1c_boxplot_setores.png", width = 6, height = 4, units = "in", res = 300)
boxplot(dados[, c("agro", "ind", "serv", "adm")],
        main = "Participação de cada setor no VAB", ylab = "Fração do VAB")
dev.off()

# Coeficientes do M3 com intervalo de 95%
rob3 <- coeftest(m3, vcov. = vcovHC, type = "HC1")
vars <- c("agro", "ind", "adm", "er", "edu", "saude", "branca", "homens")
g3 <- data.frame(var = factor(vars, levels = rev(vars)),
                 est = rob3[vars, 1] * 0.1,
                 ep  = rob3[vars, 2] * 0.1,
                 row.names = NULL)
g3$lo <- g3$est - 1.96 * g3$ep
g3$hi <- g3$est + 1.96 * g3$ep
p <- ggplot(g3, aes(x = est, y = var)) +
  geom_pointrange(aes(xmin = lo, xmax = hi)) +
  geom_vline(xintercept = 0, linetype = "dashed") +
  labs(x = "Variação na taxa por 100 mil para +0,10 na variável",
       y = "", title = "M3: coeficientes e intervalos de 95%")

png("fig3_coeficientes_m3.png", width = 7, height = 4, units = "in", res = 300)
print(p)
dev.off()
