# Fase 3 — Preparação dos Dados (CRISP-DM)

**Projeto:** Análise dos casos de violência doméstica no Distrito Federal  
**Pergunta de negócio:** Quais regiões administrativas do Distrito Federal apresentam os maiores registros de violência doméstica de 2024 a 2025?  
**Notebook:** [`notebooks/01_extracao_preparacao.ipynb`](notebooks/01_extracao_preparacao.ipynb) · **Código:** [`src/extracao.py`](src/extracao.py)

## Objetivo

A SSP-DF não publica planilhas de violência doméstica por Região Administrativa (RA): os números saem apenas como **tabelas dentro de relatórios em PDF**. Nesta fase, essas tabelas foram **extraídas por código** e convertidas em uma planilha estruturada, validada contra os totais oficiais.

## 3.1 Selecionar (filtrar)

Foram selecionados cinco relatórios da SSP-DF com a mesma *Tabela 1 — Crimes de Violência Doméstica por Região Administrativa*:

| Arquivo (`dados/brutos/`) | Relatório | Períodos | Formato da tabela |
|---|---|---|---|
| `SSPDF_RAC-001-2026_VD_2024-2025.pdf` | RAC nº 001/2026 (16/01/2026) — **fonte principal** | 2024 e 2025 | imagem |
| `SSPDF_RAC-020-2026_VD_1sem2025-2026.pdf` | RAC nº 020/2026 (13/07/2026) | 1º sem. 2025 e 2026 | imagem |
| `SSPDF_FSP-003-2023_VD_2021-2022.pdf` | Análise FSP nº 003/2023 | 2021 e 2022 | texto |
| `SSPDF_FSP-002-2021_VD_2019-2020.pdf` | Análise FSP nº 002/2021 | 2019 e 2020 | texto |
| `SSPDF_FSP-005-2020_VD_2018-2019.pdf` | Análise FSP nº 005/2020 | 2018 e 2019 | texto |

Somente a Tabela 1 (página 1) foi usada. Os relatórios anteriores a 2024 servem para dar contexto histórico e verificar a estabilidade do ranking, sem substituir a fonte principal. O informe de estupro e aborto legal da SES-DF não foi usado: os dados vêm do SINAN, são agrupados por regional de saúde e tratam de outro fenômeno.

## 3.2 Limpar (tratar)

| Problema | Tratamento |
|---|---|
| Tabela gravada como **imagem** nos relatórios RAC de 2026 | Página renderizada em 300 dpi e lida com **OCR** (Tesseract, idioma português) |
| Erros típicos de OCR em números (`$1` no lugar de `51`, `O` no lugar de `0`) | Tabela de substituição de caracteres antes da conversão para número |
| Nomes de RA escritos de formas diferentes (`SOBRADINHO 2`, `Sobradinho 2`, `Sol Nascente/Por Do Sol`, `VARJAO DO TORTO`) | Padronização para 33 nomes canônicos com acentuação correta |
| Colunas extras (participação %) no relatório de 2018/2019 | Ignoradas; mantidos apenas os dois valores anuais |
| Linhas decorativas ("68%", "Concentrados em 10 Regiões...") | Descartadas pelo padrão de linha da tabela |

**Validação automática (dupla):**
1. em cada linha, *ano 2 − ano 1* precisa ser igual à coluna *Quantit.* do próprio relatório;
2. em cada período, a soma das RAs precisa ser igual à linha *TOTAL*.

**Resultado:** os 10 totais conferidos bateram (0 divergências), inclusive nos PDFs lidos por OCR. Houve um único aviso: a coluna *Quantit.* de Park Way no RAC-001 saiu ilegível no OCR, mas o valor foi confirmado pela soma total e pelo gráfico de Pareto do próprio relatório (p. 2). O registro completo está em `dados/processados/log_validacao.csv`.

| Período | RAs | Total extraído = total oficial |
|---|---:|---:|
| 2024 | 33 | 21.721 |
| 2025 | 33 | 23.066 |
| 1º sem. 2025 | 33 | 11.709 |
| 1º sem. 2026 | 33 | 11.206 |
| 2018 / 2019 / 2020 / 2021 / 2022 | 31 / 33 / 33 / 33 / 33 | 15.368 / 16.861 / 15.995 / 16.791 / 16.949 |

## 3.3 Construir (derivar)

Variáveis criadas para cada RA e período: participação no total do DF (%), posição no ranking, variação absoluta e percentual entre 2024 e 2025 e o indicador `comparavel_33_RAs`.

## 3.4 Integrar (mesclar)

- Os relatórios foram unidos em uma **base longa** (uma linha por RA, período e ano) e em uma **visão larga** (uma linha por RA, uma coluna por ano).
- **Revisões:** cada ano aparece em dois relatórios, e a SSP revisa os números ("dados sujeitos a alterações"). Regra adotada: vale a **data de atualização mais recente**. Exemplo: 2019 tinha 16.549 registros no relatório de jan/2020 e passou a 16.861 no de jan/2021.
- **Mudança na divisão territorial:** em 2019 foram criadas as RAs Sol Nascente/Pôr do Sol (desmembrada de Ceilândia) e Arniqueira (desmembrada de Águas Claras). Por isso 2018 tem só 31 RAs e foi marcado como não comparável.

## Entregáveis da Fase 3

| Arquivo | Conteúdo |
|---|---|
| `dados/processados/violencia_domestica_ra.xlsx` | Planilha final: abas `por_RA_e_ano`, `base_longa`, `log_validacao`, `totais_por_relatorio`, `dicionario` |
| `dados/processados/violencia_domestica_ra.csv` | Base consolidada (formato longo) |
| `dados/processados/extracao_bruta.csv` | Tudo o que foi extraído, antes de resolver as revisões |
| `dados/processados/log_validacao.csv` | Resultado das validações |
| `src/extracao.py` | Código reutilizável de extração (texto + OCR) |

Para reproduzir: `python src/extracao.py dados/brutos dados/processados` ou execute o notebook 01.
