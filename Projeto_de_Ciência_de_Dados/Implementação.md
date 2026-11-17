# Fase 6 — Implementação (CRISP-DM)

O guia CRISP-DM pede quatro entregáveis nesta fase: plano de implementação, plano de monitoramento, relatório final e revisão do projeto.

## 6.1 Plano de implementação (arquitetura)

O projeto vira um **pipeline reprodutível**. Para atualizar a análise, basta adicionar o novo relatório da SSP e rodar os notebooks:

```
 SSP-DF publica relatório (PDF)
            │
            ▼
 dados/brutos/*.pdf ──► src/extracao.py ──► dados/processados/violencia_domestica_ra.xlsx / .csv
                        (texto ou OCR,          │
                         validação de totais)   ▼
                                    notebooks/02_modelagem.ipynb ──► figuras/*.png
                                                │                    resultado_modelagem_*.csv
                                                ▼
                                    notebooks/03_avaliacao.ipynb ──► avaliacao_verificacoes.csv
```

**Como executar:**

```bash
pip install -r requirements.txt          # e instalar o Tesseract OCR com o idioma português
cd notebooks
jupyter nbconvert --to notebook --execute --inplace 01_extracao_preparacao.ipynb 02_modelagem.ipynb 03_avaliacao.ipynb
```

Para analisar outro par de anos, altere `ANO_BASE` e `ANO_ALVO` na primeira célula dos notebooks 02 e 03.

**Quem usa os resultados:** gestores de segurança pública e da rede de proteção à mulher (Secretaria da Mulher, Casa da Mulher Brasileira, DEAMs) podem usar o ranking e os grupos para priorizar onde reforçar atendimento e prevenção:
- **grupo de alto volume** (Ceilândia, Planaltina, Samambaia e outras 6 RAs): concentra a demanda e é prioritário para capacidade de atendimento;
- **grupo de crescimento acelerado** (Estrutural, Fercal, Candangolândia, SIA, Jardim Botânico, Núcleo Bandeirante): volume pequeno, mas merece acompanhamento para que a alta não se consolide.

## 6.2 Plano de monitoramento

| O que monitorar | Quando | Como |
|---|---|---|
| Novo relatório semestral ou anual da SSP | Janeiro e julho | Salvar o PDF em `dados/brutos/` e rodar o pipeline |
| Falha na extração (layout do PDF mudou) | A cada execução | O notebook 01 para com erro se alguma soma não bater com o TOTAL |
| Revisões dos números anteriores | A cada novo relatório | Aba `totais_por_relatorio` e tabela de revisões no notebook 01 |
| Mudança no ranking | A cada novo relatório | Spearman entre o período novo e o anterior; queda abaixo de 0,9 indica mudança relevante |
| Novas RAs (ex.: Arapoanga, Água Quente) | Quando a SSP passar a separá-las | Incluir os nomes em `RAS_CANONICAS` (`src/extracao.py`) |

**Primeiro sinal do monitoramento:** o 1º semestre de 2026 (RAC-020/2026) registrou 11.206 casos, contra 11.709 no 1º semestre de 2025 (−4,3%). Ceilândia, Planaltina e Samambaia continuam nas três primeiras posições.

## 6.3 Relatório final (resumo)

> Em 2024 e 2025, os registros de violência doméstica ou familiar no Distrito Federal se concentraram em **Ceilândia, Planaltina e Samambaia**, que lideram o ranking em todos os anos analisados desde 2018. Em 2025, as 10 RAs com mais registros (Ceilândia, Planaltina, Samambaia, Taguatinga, Recanto das Emas, Gama, Sol Nascente/Pôr do Sol, Santa Maria, São Sebastião e Brasília) responderam por 66% dos 23.066 casos registrados no DF. O total cresceu 6,2% em relação a 2024, puxado principalmente por Planaltina (+249), Ceilândia (+213), Recanto das Emas (+147) e Sol Nascente/Pôr do Sol (+140). Brasília teve a maior queda (−125). Os números são absolutos, ou seja, refletem também o tamanho da população de cada RA, e representam casos registrados, não o total de episódios de violência.

Material de apoio: figuras 1 a 5 em `figuras/`, planilha `dados/processados/violencia_domestica_ra.xlsx` e notebooks executados com saídas.

## 6.4 Revisão do projeto (lições aprendidas)

- **Dados públicos nem sempre são dados abertos.** A informação existia, mas só em PDF, em parte como imagem. Extrair por código com validação garantiu uma base confiável e reprodutível, sem digitação manual.
- **Validar contra a própria fonte** (somas × TOTAL, Quantit. × diferença) foi o que deu segurança para usar OCR.
- **A comparação justa é a do mesmo relatório.** Comparar relatórios de anos diferentes expôs revisões, mudanças na divisão territorial e uma possível mudança de critério entre 2022 e 2024.
- **Próximos passos:** taxas por 100 mil habitantes (PDAD-A 2024), relatório de 2023 para completar a série e, se a SSP fornecer via Lei de Acesso à Informação, microdados mensais por RA.
