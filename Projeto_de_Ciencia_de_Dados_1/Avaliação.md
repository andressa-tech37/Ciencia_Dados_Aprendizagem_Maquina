# Fase 5 — Avaliação (CRISP-DM)

**Notebook:** [`notebooks/03_avaliacao.ipynb`](notebooks/03_avaliacao.ipynb) · **Resultado das verificações:** `dados/processados/avaliacao_verificacoes.csv`

O guia CRISP-DM define o objetivo desta fase: avaliar os resultados **pelos critérios de sucesso da Fase 1** (impacto real > precisão técnica) e decidir entre **implementar ou iterar**.

## 5.1 Os resultados respondem à pergunta?

**Sim.** Em 2024 e 2025, as regiões administrativas com mais registros de violência doméstica ou familiar no DF foram, nesta ordem em 2025: **Ceilândia (3.135), Planaltina (1.951) e Samambaia (1.809)**, seguidas por Taguatinga, Recanto das Emas, Gama, Sol Nascente/Pôr do Sol, Santa Maria, São Sebastião e Brasília. Essas 10 RAs concentram **66%** dos registros. Os registros no DF subiram **6,2%** (de 21.721 para 23.066), e o maior aumento absoluto foi em **Planaltina (+249)**.

A resposta é **robusta**: as mesmas 10 RAs lideram em 2024, em 2025 e na soma dos dois anos; o ranking dos dois anos tem correlação de Spearman de 0,992; e as três primeiras posições se repetem em todos os anos desde 2018.

## 5.2 Fidelidade dos dados (verificações automáticas)

| Verificação | Resultado |
|---|---|
| Soma das RAs = TOTAL oficial, nos 10 períodos extraídos | ✔ 0 divergências |
| Totais 2024 (21.721) e 2025 (23.066) iguais aos da Fase 2 | ✔ |
| Top 10 de 2025 igual ao registrado na Fase 2 | ✔ sem diferenças |
| Concentração das 10 maiores ≈ 66%, como afirma o relatório | ✔ 66,1% |
| 1º semestre de 2025 (outro relatório, RAC-020) ≈ metade do ano | ✔ 50,8% no DF; só Sudoeste ficou fora da faixa de 40–60% (39%) |
| Mesmas 10 RAs em 2024 e 2025 | ✔ |
| Top 10 de 2025 = top 10 da soma 2024+2025 | ✔ |
| Ranking 2024 × 2025 estável (Spearman ≥ 0,9) | ✔ ρ = 0,992 |
| Ceilândia lidera em todos os anos | ✔ 2018–2025 |

## 5.3 Critérios de sucesso da Fase 1

| Critério | Situação | Evidência |
|---|---|---|
| 1. Identificar as RAs com maiores números absolutos | **Atendido** | Ranking das 33 RAs (Modelagem, fig. 1 e 2) |
| 2. Comparar 2024 e 2025 de forma verificável | **Atendido** | Variação por RA (fig. 3), com base reprodutível e validada |
| 3. Gráficos e tabelas claros, com fonte e período | **Atendido** | Figuras com fonte SSP-DF; planilha com dicionário de dados |
| 4. Explicar limitações e não tratar número absoluto como risco | **Atendido** | Seção 5.4 abaixo |

## 5.4 Revisão do processo e limitações

1. **Números absolutos não medem risco.** Ceilândia e Samambaia estão entre as RAs mais populosas do DF. Um ranking por **taxa por 100 mil habitantes** pode mudar a ordem. Essa taxa não foi calculada porque a projeção populacional por RA (PDAD-A 2024, IPEDF) usa 35 RAs, enquanto a SSP usa 33: Arapoanga e Água Quente ainda aparecem dentro de Planaltina e Recanto das Emas. Compatibilizar as duas bases é a principal próxima iteração.
2. **Registro não é o mesmo que ocorrência real.** Os dados medem casos **registrados** pela polícia. Um aumento pode refletir mais denúncias, e não necessariamente mais violência (subnotificação).
3. **Quebra na série histórica.** O total do DF passou de 16.949 (2022) para 21.721 (2024), uma alta de 28%. Não há relatório de 2023 na base, e a partir de 2024 a SSP passou a usar "violência doméstica **ou familiar**". Não é possível separar quanto disso é aumento real e quanto é mudança de critério. Por isso a comparação principal usa só 2024 × 2025, que vêm do mesmo relatório, e a série anterior serve apenas para verificar a estabilidade do ranking.
4. **Dados agregados e revisáveis.** Não há microdados por vítima. A SSP revisa os números com o tempo (ex.: 2019 passou de 16.549 para 16.861 entre dois relatórios).
5. **Extração por OCR.** As tabelas de 2026 estão em imagem. O risco de erro de leitura foi controlado pelas validações da seção 5.2.
6. **Variações percentuais em RAs pequenas** (Candangolândia +50%, SIA +47,5%) envolvem poucas dezenas de casos e devem ser lidas com cautela.

## 5.5 Decisão: implementar ou iterar?

**Implementar** a análise de volume absoluto, pois responde à pergunta com dados validados. **Iterar** em uma segunda rodada para:

- calcular taxas por 100 mil habitantes, compatibilizando a PDAD-A 2024 com as 33 RAs da SSP;
- incluir o relatório anual de 2023, para fechar a série histórica e investigar o salto de 2022 para 2024.
