from processar_dados import classificar, validar_data_hora, identificar_erros, converter_int_para_float

total = 0
falhas = 0


def conferir(nome, obtido, esperado):
    global total, falhas
    total += 1
    if obtido == esperado:
        print("OK:     " + nome)
    else:
        falhas += 1
        print("FALHOU: " + nome + " | esperado = " + str(esperado) + " | obtido = " + str(obtido))


def testar_classificacao(nome, fluxo, temperatura, vazamento, evento_esperado, severidade_esperada):
    registro = {
        "molde_id": "M001",
        "data_hora": "2026-10-15T08:00:00",
        "fluxo_agua_l_min": fluxo,
        "temperatura_agua_c": temperatura,
        "vazamento_oleo": vazamento,
    }
    resultado = classificar(registro)
    conferir(nome, (resultado["evento"], resultado["severidade"]), (evento_esperado, severidade_esperada))


print("--- Classificação ---")
testar_classificacao("tudo normal", 18.0, 30.0, False, None, 1)
testar_classificacao("só fluxo baixo (atenção)", 12.0, 30.0, False, "BAIXA_VAZAO", 2)
testar_classificacao("só fluxo muito baixo (crítico)", 5.0, 30.0, False, "BAIXA_VAZAO", 3)
testar_classificacao("só temperatura alta (atenção)", 18.0, 42.0, False, "ALTA_TEMPERATURA", 2)
testar_classificacao("só temperatura muito alta (crítico)", 18.0, 50.0, False, "ALTA_TEMPERATURA", 3)
testar_classificacao("fluxo e temperatura em atenção", 12.0, 42.0, False, "CONDICAO_MISTA", 2)
testar_classificacao("fluxo crítico e temperatura em atenção (maior vence)", 5.0, 42.0, False, "CONDICAO_MISTA", 3)
testar_classificacao("só vazamento", 18.0, 30.0, True, "VAZAMENTO_OLEO", 3)
testar_classificacao("vazamento + fluxo crítico + temperatura crítica", 5.0, 50.0, True, "VAZAMENTO_OLEO", 3)

print("--- Limites exatos (regra estrita) ---")
testar_classificacao("fluxo = 15.0 é normal", 15.0, 30.0, False, None, 1)
testar_classificacao("fluxo = 10.0 é atenção, não crítico", 10.0, 30.0, False, "BAIXA_VAZAO", 2)
testar_classificacao("temperatura = 40.0 é normal", 18.0, 40.0, False, None, 1)
testar_classificacao("temperatura = 45.0 é atenção, não crítico", 18.0, 45.0, False, "ALTA_TEMPERATURA", 2)

print("--- Data e hora (formato com segundos) ---")
conferir("data com segundos é válida", validar_data_hora("2026-10-15T08:00:00"), None)
conferir("data sem segundos é inválida", validar_data_hora("2026-10-15T08:00") is None, False)
conferir("data com barras é inválida", validar_data_hora("15/10/2026 08:00:00") is None, False)
conferir("data com espaço no lugar do T é inválida", validar_data_hora("2026-10-15 08:00:00") is None, False)
conferir("data que não existe (31/11) é inválida", validar_data_hora("2026-11-31T08:00:00") is None, False)
conferir("data que não é texto é inválida", validar_data_hora(20261015) is None, False)

print("--- Validação do registro ---")
ok = {"molde_id": "M001", "data_hora": "2026-10-15T08:00:00",
      "fluxo_agua_l_min": 18.0, "temperatura_agua_c": 30.0, "vazamento_oleo": False}
conferir("registro correto não gera erros", identificar_erros(ok), [])

com_int = dict(ok)
com_int["fluxo_agua_l_min"] = 12
conferir("int 12 vira float 12.0 e passa", identificar_erros(converter_int_para_float(com_int)), [])

como_texto = dict(ok)
como_texto["fluxo_agua_l_min"] = "18.5"
conferir("fluxo como texto é rejeitado", len(identificar_erros(como_texto)), 1)

vazamento_texto = dict(ok)
vazamento_texto["vazamento_oleo"] = "true"
conferir("vazamento como texto é rejeitado", len(identificar_erros(vazamento_texto)), 1)

sem_campo = dict(ok)
del sem_campo["vazamento_oleo"]
conferir("campo ausente é rejeitado", len(identificar_erros(sem_campo)), 1)

fluxo_fora = dict(ok)
fluxo_fora["fluxo_agua_l_min"] = 100.1
conferir("fluxo acima de 100.0 é rejeitado", len(identificar_erros(fluxo_fora)), 1)

fluxo_limite = dict(ok)
fluxo_limite["fluxo_agua_l_min"] = 100.0
conferir("fluxo = 100.0 (limite da faixa) é aceito", identificar_erros(fluxo_limite), [])

print()
print("Total:", total, "| Passaram:", total - falhas, "| Falharam:", falhas)
    
