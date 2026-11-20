# SISP – Processamento e qualidade de dados de moldes

Script em Python que lê medições de moldes em formato JSONL, **valida a qualidade de cada registro**, classifica a situação de cada medição (normal, atenção ou crítico) e grava o resultado num banco **SQLite**. Registros com problema não entram no banco: vão para um **log de erros em CSV**, com o motivo da rejeição.

Esta é a minha parte do **SISP (Sistema Inteligente de Sensores Preditivos)**, um protótipo acadêmico de monitoramento preditivo desenvolvido em equipe de 6 pessoas no curso de Análise e Desenvolvimento de Sistemas da ETEP (São José dos Campos – SP), a ser apresentado na EXPOETEP em novembro de 2026.

> Os dados e os limites usados aqui são **simulados**. Não são dados reais de nenhuma empresa.

## O que o código faz

```
entrada.jsonl ──► leitura linha a linha ──► validação ──┬──► classificação ──► sisp.db (tb_medicoes)
                                                        └──► log_erros.csv (registros rejeitados)
```

1. **Lê** o arquivo `entrada.jsonl`, uma medição por linha.
2. **Trata linhas quebradas:** se a linha não é um JSON válido, ou não é um objeto com campos, ela vai para o log e o processamento continua.
3. **Valida cada campo** do registro:

   | Campo | Regra |
   |---|---|
   | `molde_id` | texto, não pode ser vazio |
   | `data_hora` | texto no formato exato `AAAA-MM-DDTHH:MM:SS` |
   | `fluxo_agua_l_min` | número entre 0 e 100 (inteiros são convertidos para decimal) |
   | `temperatura_agua_c` | número entre 0 e 100 |
   | `vazamento_oleo` | `true` ou `false` |

   Campos ausentes também são registrados como erro.
4. **Classifica** os registros válidos:

   | Evento | Atenção | Crítico |
   |---|---|---|
   | `BAIXA_VAZAO` | fluxo abaixo de 15 L/min | fluxo abaixo de 10 L/min |
   | `ALTA_TEMPERATURA` | temperatura acima de 40 °C | temperatura acima de 45 °C |
   | `VAZAMENTO_OLEO` | – | sempre crítico |
   | `CONDICAO_MISTA` | vazão e temperatura fora ao mesmo tempo | pega a maior severidade |

   Cada registro recebe `status`, `evento`, `severidade` (1 a 3) e uma mensagem de recomendação.
5. **Grava** o resultado na tabela `tb_medicoes` e mostra um resumo no final.

Os limites ficam no `config.json`, separados do código: para mudar uma faixa, não é preciso mexer no programa.

## Como rodar

Precisa só do **Python 3**. Não usa nenhuma biblioteca externa (apenas `json`, `csv`, `sqlite3`, `datetime` e `os`).

```bash
python criar_sisp_v11.py     # cria o banco sisp.db vazio, com a tabela tb_medicoes
python processar_dados.py    # processa o entrada.jsonl
```

Saída com os dados de exemplo:

```
Resumo: lidos = 36 | aceitos = 36 | rejeitados = 0
```

Resultado no banco: 17 medições **NORMAL**, 9 em **ATENÇÃO** e 10 **CRÍTICAS**. Por exemplo, o molde M001 perde vazão aos poucos até ficar crítico, o M002 aquece até passar de 45 °C e o M003 passa a acusar vazamento de óleo a partir das 08:30.

## Estrutura

```
├── processar_dados.py   # leitura, validação, classificação e gravação (minha parte)
├── criar_sisp_v11.py    # cria o banco e a tabela tb_medicoes (feito por um colega da equipe)
├── config.json          # formato de data, faixas válidas, limites e nomes de arquivos
└── entrada.jsonl        # medições simuladas de 3 moldes
```

## Minha parte no projeto

Fui responsável pelo processamento de dados em Python: leitura do JSONL, regras de qualidade, log de erros, classificação e carga no SQLite. A estrutura da tabela (`criar_sisp_v11.py`) foi feita por outro integrante da equipe e está aqui para o script poder rodar.

## Próximos passos

- Evitar duplicação: hoje, rodar o script duas vezes grava as mesmas medições de novo.
- Fazer um único commit no banco no final do arquivo, em vez de um por linha.
- Reduzir a repetição na função `identificar_erros` usando uma lista de regras.
- Separar os testes do código principal.
