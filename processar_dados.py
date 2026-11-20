import json 
import csv
import os
import sqlite3
from datetime import datetime

PASTA = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(PASTA, "config.json"), encoding="utf-8") as arquivo:
    CONFIG = json.load(arquivo)
    

CAMPOS_NUMERICOS = ("fluxo_agua_l_min", "temperatura_agua_c")

def converter_int_para_float (registro):
    novo = dict(registro)
    for campo in CAMPOS_NUMERICOS:
        valor = novo.get(campo)
        if isinstance(valor, int) and not isinstance(valor, bool):
            novo[campo] = float(valor)
    return novo

def validar_molde_id(valor):
    if not isinstance(valor, str):
        return "Chegou um valor com tipo inválido no lugar de string."
    if valor.strip() == "":
        return "Chegou uma string vazia ou só com espaços."
    return None

def validar_numero(valor, minimo, maximo):
    if not isinstance(valor, float):
        return "O valor não é do tipo float."
    if not (minimo <= valor <= maximo):
        return "O valor não está entre o mínimo e o máximo."
    return None

def validar_vazamento(valor):
    if not isinstance(valor, bool):
        return "O valor não é booleano (True/False)."
    return None

def validar_data_hora(valor):
    if not isinstance(valor, str):
        return "O valor não é do tipo string."
    try:
        data = datetime.strptime(valor, CONFIG["formato_data_hora"])
    except ValueError:
        return "O texto não corresponde ao formato de data e hora esperado."
    if data.strftime(CONFIG["formato_data_hora"]) != valor:
        return "Formato quase correto, mas não exatamente igual ao esperado."
    return None

def identificar_erros(registro):
    erros = []

    if "molde_id" not in registro:
        erros.append({
            "campo": "molde_id",
            "valor_recebido": None,
            "tipo_esperado": "string",
            "motivo": "Campo ausente."
        })
    else: 
        motivo = validar_molde_id(registro["molde_id"])
        if motivo is not None:
            erros.append({
                "campo": "molde_id",
                "valor_recebido": registro["molde_id"],
                "tipo_esperado": "string",
                "motivo": motivo
            })
            

    if "data_hora" not in registro:
        erros.append({
            "campo": "data_hora",
            "valor_recebido": None,
            "tipo_esperado": "string",
            "motivo": "Campo ausente."
        })
    else: 
        motivo = validar_data_hora(registro["data_hora"])
        if motivo is not None:
            erros.append({
                "campo": "data_hora",
                "valor_recebido": registro["data_hora"],
                "tipo_esperado": "string",
                "motivo": motivo
            })

    

    if "fluxo_agua_l_min" not in registro:
        erros.append({
            "campo": "fluxo_agua_l_min",
            "valor_recebido": None,
            "tipo_esperado": "float",
            "motivo": "Campo ausente."
        })

    else: 
        motivo = validar_numero(registro["fluxo_agua_l_min"], CONFIG["faixas_validas"]["fluxo_minimo_agua"], CONFIG["faixas_validas"]["fluxo_maximo_agua"])
        if motivo is not None:
            erros.append({
                "campo": "fluxo_agua_l_min",
                "valor_recebido": registro["fluxo_agua_l_min"],
                "tipo_esperado": "float",
                "motivo": motivo
            })

    

    if "temperatura_agua_c" not in registro:
        erros.append({
            "campo": "temperatura_agua_c",
            "valor_recebido": None,
            "tipo_esperado": "float",
            "motivo": "Campo ausente."
        })

    else: 
        motivo = validar_numero(registro["temperatura_agua_c"], CONFIG["faixas_validas"]["temperatura_minima"], CONFIG["faixas_validas"]["temperatura_maxima"])
        if motivo is not None:
            erros.append({
                "campo": "temperatura_agua_c",
                "valor_recebido": registro["temperatura_agua_c"],
                "tipo_esperado": "float",
                "motivo": motivo
            })

    

    if "vazamento_oleo" not in registro:
        erros.append({
            "campo": "vazamento_oleo",
            "valor_recebido": None,
            "tipo_esperado": "booleano",
            "motivo": "Campo ausente."
        })
    else:
        motivo = validar_vazamento(registro["vazamento_oleo"])
        if motivo is not None:
            erros.append({
                "campo": "vazamento_oleo",
                "valor_recebido": registro["vazamento_oleo"],
                "tipo_esperado": "booleano",
                "motivo": motivo
            })

    return erros

registro_ok = {"molde_id": "M001", "data_hora": "2026-10-14T11:53:00",
               "fluxo_agua_l_min": 18.0, "temperatura_agua_c": 30.0,
               "vazamento_oleo": False}
registro_ruim = {"molde_id": "", "data_hora": "14/10/2026",
                 "fluxo_agua_l_min": "18.5", "temperatura_agua_c": 150.0,
                 "vazamento_oleo": "true"}


COLUNAS_LOG = ["molde_id", "data_hora_registro", "campo",
               "valor_recebido", "tipo_esperado", "motivo", "data_hora_erro"]

def registrar_log(registro, erros):
    caminho = os.path.join(PASTA, CONFIG["caminhos"]["nome_do_log"])
    arquivo_novo = not os.path.exists(caminho)

    # a data_hora do registro só vai para o log se ela mesma estiver correta
    data_hora_invalida = False
    for erro in erros:
        if erro["campo"] == "data_hora":
            data_hora_invalida = True

    with open(caminho, "a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        if arquivo_novo:
            escritor.writerow(COLUNAS_LOG)
        for erro in erros:
            escritor.writerow([
                registro.get("molde_id",""),
                "" if data_hora_invalida else registro.get("data_hora",""),
                erro["campo"],
                json.dumps(erro["valor_recebido"],ensure_ascii=False),
                erro["tipo_esperado"],
                erro["motivo"],
                datetime.now().strftime(CONFIG["formato_data_hora"]),
            ])

# registrar_log(registro_ruim, identificar_erros(registro_ruim))   # teste antigo, desligado

def nivel_fluxo(fluxo):
    if fluxo < CONFIG["limites"]["Crítico"]["fluxo_agua_abaixo_de"]:
        return 3
    if fluxo < CONFIG["limites"]["Atenção"]["fluxo_agua_abaixo_de"]:   # o mesmo, mas com o limite de "Atenção"
        return 2
    return 1

def nivel_temperatura(temperatura):
    if temperatura > CONFIG["limites"]["Crítico"]["temperatura_acima_de"]:
        return 3
    if temperatura > CONFIG["limites"]["Atenção"]["temperatura_acima_de"]:
        return 2
    return 1

def definir_evento_e_severidade(registro):
    n_fluxo = nivel_fluxo(registro["fluxo_agua_l_min"])
    n_temp = nivel_temperatura(registro["temperatura_agua_c"])

    if registro["vazamento_oleo"]:
        evento = "VAZAMENTO_OLEO"
        severidade = 3
    elif n_fluxo > 1 and n_temp > 1:
        evento = "CONDICAO_MISTA"
        severidade = max(n_fluxo, n_temp)
    elif n_fluxo > 1:
        evento = "BAIXA_VAZAO"
        severidade = n_fluxo
    elif n_temp > 1:
        evento = "ALTA_TEMPERATURA"
        severidade = n_temp
    else:
        evento = None          # dica: nada de anormal
        severidade = 1

    return {"evento": evento, "severidade": severidade}

STATUS_POR_SEVERIDADE = {1: "NORMAL", 2: "ATENÇÃO", 3: "CRÍTICO"}

MENSAGENS = {
    None: "Parâmetros dentro das faixas definidas para a simulação.",
    "BAIXA_VAZAO": "Possível condição anormal no circuito de refrigeração. Recomenda-se inspeção técnica do fluxo.",
    "ALTA_TEMPERATURA": "Temperatura da água acima do parâmetro da simulação. Pode indicar condição anormal. Recomenda-se verificar o circuito de água.",
    "VAZAMENTO_OLEO": "Vazamento de óleo detectado. Recomenda-se inspeção técnica de engates e mangueiras.",
    "CONDICAO_MISTA": "Mais de uma condição anormal detectada ao mesmo tempo. Recomenda-se inspeção técnica. Não substitui a avaliação técnica.",
}

def classificar(registro):
    resultado = definir_evento_e_severidade(registro)

    novo = dict(registro)
    novo["status"] = STATUS_POR_SEVERIDADE[resultado["severidade"]]
    novo["evento"] = resultado["evento"]
    novo["severidade"] = resultado["severidade"]
    novo["mensagem"] = MENSAGENS[resultado["evento"]]
    return novo


def abrir_conexao(caminho=None):
    if caminho is None:
        caminho = CONFIG["caminhos"]["nome_do_banco"]
    caminho = os.path.join(PASTA, caminho)
    conexao = sqlite3.connect(caminho)
    cursor = conexao.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tb_medicoes'")
    existe = cursor.fetchone()
    if not existe:
        conexao.close()
        raise RuntimeError("Tabela 'tb_medicoes' não encontrada no banco '" + caminho + "'. Crie a tabela com o DDL do Integrante 4 antes de rodar o processamento.")
    return conexao


def gravar_medicao(conexao, processado):
    sql = """
        INSERT INTO tb_medicoes (
            molde_id, data_hora, fluxo_agua_l_min, temperatura_agua_c,
            vazamento_oleo, status, evento, severidade, mensagem
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    valores = (
        processado["molde_id"],
        processado["data_hora"],
        processado["fluxo_agua_l_min"],
        processado["temperatura_agua_c"],
        int(processado["vazamento_oleo"]),
        processado["status"],
        processado["evento"],
        processado["severidade"],
        processado["mensagem"],
    )
    conexao.cursor().execute(sql, valores)
    conexao.commit()

def processar_registro(registro, conexao):
    registro = converter_int_para_float(registro)
    erros = identificar_erros(registro)
    if erros:
        registrar_log(registro, erros)
        return False
    processado = classificar(registro)
    gravar_medicao(conexao, processado)
    return True


def registrar_erro_de_linha(numero_linha, texto, motivo):
    erro = {
        "campo": "linha " + str(numero_linha),
        "valor_recebido": texto,
        "tipo_esperado": "objeto JSON válido",
        "motivo": motivo,
    }
    registrar_log({}, [erro])


def processar_arquivo(caminho="entrada.jsonl", caminho_banco=None):
    caminho = os.path.join(PASTA, caminho)
    if not os.path.exists(caminho):
        raise FileNotFoundError("Arquivo de entrada '" + caminho + "' não encontrado.")

    conexao = abrir_conexao(caminho_banco)
    lidos = 0
    aceitos = 0
    rejeitados = 0

    try:
        with open(caminho, encoding="utf-8") as arquivo:
            for numero, linha in enumerate(arquivo, start=1):
                texto = linha.strip()
                if texto == "":
                    continue
                lidos += 1

                try:
                    registro = json.loads(texto)
                except json.JSONDecodeError:
                    registrar_erro_de_linha(numero, texto, "A linha não é um JSON válido.")
                    rejeitados += 1
                    continue

                if not isinstance(registro, dict):
                    registrar_erro_de_linha(numero, texto, "A linha é um JSON válido, mas não é um objeto com campos.")
                    rejeitados += 1
                    continue

                if processar_registro(registro, conexao):
                    aceitos += 1
                else:
                    rejeitados += 1
    finally:
        conexao.close()

    print("Resumo: lidos =", lidos, "| aceitos =", aceitos, "| rejeitados =", rejeitados)
    return lidos, aceitos, rejeitados

if __name__ == "__main__":
    processar_arquivo("entrada.jsonl")