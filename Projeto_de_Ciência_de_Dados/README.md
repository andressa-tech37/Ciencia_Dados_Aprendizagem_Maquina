# Projeto de Ciência de Dados — Violência Doméstica no Distrito Federal

**Disciplina:** Ciência de Dados e Aprendizagem de Máquina · UDF · 2026.2  
**Docente:** Profa. Kadidja Valéria  
**Início:** 28/10/2026  
**Metodologia:** CRISP-DM — [guia IBM](https://www.ibm.com/docs/pt-br/SS3RA7_18.5.0/nl/pt/BR/pdf/ModelerCRISPDM.pdf)

**Pergunta:** Quais regiões administrativas do Distrito Federal apresentam os maiores registros de violência doméstica de 2024 a 2025?

**Resposta curta:** Ceilândia (3.135 registros em 2025), Planaltina (1.951) e Samambaia (1.809) lideram em 2024 e em 2025. As 10 maiores RAs concentram 66% dos 23.066 registros de 2025, e o total do DF cresceu 6,2% em relação a 2024.

## Fases do CRISP-DM

| Fase | Documento | Notebook |
|---|---|---|
| 1. Entendimento do Negócio | [Entendimento_do_Negócio.md](Entendimento_do_Negócio.md) | — |
| 2. Entendimento dos Dados | [Entendimento_dos_Dados.md](Entendimento_dos_Dados.md) | — |
| 3. Preparação dos Dados | [Preparação_de_Dados.md](Preparação_de_Dados.md) | [01_extracao_preparacao.ipynb](notebooks/01_extracao_preparacao.ipynb) |
| 4. Modelagem | [Modelagem.md](Modelagem.md) | [02_modelagem.ipynb](notebooks/02_modelagem.ipynb) |
| 5. Avaliação | [Avaliação.md](Avaliação.md) | [03_avaliacao.ipynb](notebooks/03_avaliacao.ipynb) |
| 6. Implementação | [Implementação.md](Implementação.md) | — |

## Estrutura

```
Projeto_de_Ciência_de_Dados/
├── dados/
│   ├── brutos/          relatórios em PDF da SSP-DF (fonte original)
│   └── processados/     planilha extraída (.xlsx/.csv), logs e resultados
├── src/extracao.py      extração das tabelas (pdfplumber + OCR Tesseract)
├── notebooks/           01 preparação · 02 modelagem · 03 avaliação (executados)
├── figuras/             gráficos gerados pela modelagem
└── *.md                 documentação de cada fase
```

## Reprodução

```bash
pip install -r requirements.txt
# OCR: instalar o Tesseract com o pacote de idioma português (tesseract-ocr-por)
cd notebooks
jupyter nbconvert --to notebook --execute --inplace 01_extracao_preparacao.ipynb 02_modelagem.ipynb 03_avaliacao.ipynb
```

Ambiente usado: Python 3.13, pandas 3.0, pdfplumber 0.11, Tesseract 5, scikit-learn 1.9, matplotlib 3.11. Semente aleatória: 42.

## Fontes

- SSP-DF, Relatório de Análise Criminal nº 001/2026 — Violência Doméstica ou Familiar no DF, 2024 e 2025 (fonte principal).
- SSP-DF, Relatório de Análise Criminal nº 020/2026 — 1º semestre de 2025 e 2026.
- SSP-DF, Análises de Fenômenos de Segurança Pública nº 005/2020, 002/2021 e 003/2023 (2018 a 2022).
- Referência complementar: [IPEDF — Panorama da violência contra a mulher no DF](https://ipe.df.gov.br/panorama-da-violencia-contra-a-mulher-no-distrito-federal).
