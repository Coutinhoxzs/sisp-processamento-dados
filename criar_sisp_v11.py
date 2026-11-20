import os
import sqlite3

PASTA = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(PASTA, "sisp.db")

if os.path.exists(caminho):
    raise SystemExit("Já existe um sisp.db nesta pasta. Renomeie o antigo (por exemplo sisp_antigo_integer.db) e rode de novo.")

DDL_V11 = """
CREATE TABLE tb_medicoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    molde_id TEXT NOT NULL,
    data_hora TEXT NOT NULL,
    fluxo_agua_l_min REAL NOT NULL,
    temperatura_agua_c REAL NOT NULL,
    vazamento_oleo INTEGER NOT NULL CHECK (vazamento_oleo IN (0, 1)),
    status TEXT NOT NULL CHECK (status IN ('NORMAL', 'ATENÇÃO', 'CRÍTICO')),
    evento TEXT CHECK (evento IS NULL OR evento IN ('BAIXA_VAZAO', 'ALTA_TEMPERATURA', 'VAZAMENTO_OLEO', 'CONDICAO_MISTA')),
    severidade INTEGER NOT NULL CHECK (severidade BETWEEN 1 AND 3),
    mensagem TEXT NOT NULL
);
"""

conexao = sqlite3.connect(caminho)
conexao.executescript(DDL_V11)
conexao.close()
print("sisp.db criado (vazio) com a tb_medicoes v1.1.")