"""
Extração das tabelas de violência doméstica por Região Administrativa (RA)
publicadas pela SSP-DF em PDF.

Fase 3 do CRISP-DM — Preparação dos Dados.

Os relatórios da SSP-DF trazem, na página 1, a "Tabela 1 – Crimes de Violência
Doméstica por Região Administrativa", comparando dois anos (ou dois semestres).
Há dois formatos de PDF:

* relatórios antigos (2020–2023): a tabela é TEXTO -> lida com pdfplumber;
* relatórios novos (RAC 2026): a tabela é IMAGEM -> lida com OCR (Tesseract).

Para cada linha da tabela o código guarda os dois valores (ano anterior e ano
atual) e confere:
  1. se (ano atual - ano anterior) é igual à coluna "Quantit." da própria tabela;
  2. se a soma das RAs é igual à linha TOTAL do relatório.
Qualquer divergência vai para o log de validação, para conferência manual.

Uso:
    python src/extracao.py dados/brutos dados/processados
"""
from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import pdfplumber

# ---------------------------------------------------------------------------
# 1. Padronização dos nomes das Regiões Administrativas
# ---------------------------------------------------------------------------
# A SSP escreve os nomes sem acento e de formas diferentes ao longo dos anos
# ("SOBRADINHO 2", "Sobradinho 2", "Sol Nascente/Por Do Sol"...).
# Todas as variações são convertidas para um nome canônico.
RAS_CANONICAS = [
    "Águas Claras", "Arniqueira", "Brasília", "Brazlândia", "Candangolândia",
    "Ceilândia", "Cruzeiro", "Estrutural", "Fercal", "Gama", "Guará", "Itapoã",
    "Jardim Botânico", "Lago Norte", "Lago Sul", "Núcleo Bandeirante", "Paranoá",
    "Park Way", "Planaltina", "Recanto das Emas", "Riacho Fundo",
    "Riacho Fundo II", "Samambaia", "Santa Maria", "São Sebastião", "SIA",
    "Sobradinho", "Sobradinho II", "Sol Nascente/Pôr do Sol", "Sudoeste",
    "Taguatinga", "Varjão", "Vicente Pires",
]


def _chave(nome: str) -> str:
    """Remove acentos, espaços e pontuação: 'São Sebastião' -> 'SAOSEBASTIAO'."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    chave = re.sub(r"[^A-Z0-9]", "", sem_acento.upper())
    return chave.replace("II", "2")


_MAPA_RA = {_chave(n): n for n in RAS_CANONICAS}
_MAPA_RA.update({
    _chave("Varjão do Torto"): "Varjão",
    _chave("Plano Piloto"): "Brasília",
    _chave("SCIA"): "Estrutural",
    _chave("SCIA/Estrutural"): "Estrutural",
    _chave("Sudoeste/Octogonal"): "Sudoeste",
})


def padronizar_ra(nome: str) -> str | None:
    """Devolve o nome canônico da RA ou None se não reconhecer."""
    return _MAPA_RA.get(_chave(nome))


# ---------------------------------------------------------------------------
# 2. Leitura do texto da página (PDF de texto ou OCR)
# ---------------------------------------------------------------------------
def texto_pdf(caminho: Path, pagina: int = 0) -> str:
    with pdfplumber.open(caminho) as pdf:
        return pdf.pages[pagina].extract_text() or ""


def texto_ocr(caminho: Path, pagina: int = 0, dpi: int = 300) -> str:
    """Renderiza a página como imagem e aplica OCR em português."""
    import pypdfium2 as pdfium
    import pytesseract

    pdf = pdfium.PdfDocument(str(caminho))
    imagem = pdf[pagina].render(scale=dpi / 72).to_pil()
    largura, altura = imagem.size
    # recorta a metade esquerda da página, onde fica a tabela, para o OCR não
    # misturar as linhas com o quadro de destaque à direita
    tabela = imagem.crop((0, int(altura * 0.40), int(largura * 0.68), int(altura * 0.92)))
    return pytesseract.image_to_string(tabela, lang="por", config="--psm 6")


# ---------------------------------------------------------------------------
# 3. Interpretação das linhas da tabela
# ---------------------------------------------------------------------------
# Erros comuns de OCR em números: "$1" em vez de "51", "O" em vez de "0"...
_TROCAS_OCR = str.maketrans({"O": "0", "o": "0", "$": "5", "S": "5", "l": "1", "I": "1", "B": "8"})


def _numero(token: str) -> int | None:
    token = token.strip().translate(_TROCAS_OCR)
    token = token.replace("(", "").replace(")", "").replace(".", "")
    return int(token) if re.fullmatch(r"-?\d+", token) else None


_RE_LINHA = re.compile(
    r"^\s*\S+\s+"                         # ordem: "1ª", "12" (OCR)...
    r"(?P<ra>[^\d\s].*?)\s+"              # nome da RA
    r"(?P<a>[\dO$Sl]+)\s+(?P<b>[\dO$Sl]+)\s+"  # valores dos dois períodos
    r"(?P<pct>-?[\d,]+\s?%)\s+"           # variação percentual
    r"(?P<q>\S+)"                         # variação absoluta ("Quantit.")
    r"(?:\s+.*)?$"                        # colunas extras (participação %)
)
_RE_TOTAL = re.compile(r"TOTAL\s+(\d+)\s+(\d+)")
_RE_ANOS = re.compile(r"(20\d{2})\s+(20\d{2})\s+\(%\)")
_RE_ATUALIZACAO = re.compile(r"atualizados\s+em\s+(\d{2}/\d{2}/\d{4})", re.I)


@dataclass
class TabelaExtraida:
    documento: str
    metodo: str
    periodo: str
    anos: tuple[int, int]
    data_atualizacao: str | None
    linhas: list[dict] = field(default_factory=list)
    total_oficial: tuple[int, int] | None = None
    log: list[dict] = field(default_factory=list)


def interpretar(texto: str, documento: str, metodo: str) -> TabelaExtraida:
    anos = _RE_ANOS.search(texto)
    if not anos:
        raise ValueError(f"{documento}: não encontrei o cabeçalho com os dois anos")
    ano_a, ano_b = int(anos.group(1)), int(anos.group(2))
    periodo = "1º semestre" if re.search(r"semestre", texto, re.I) else "Anual"
    atualizacao = _RE_ATUALIZACAO.search(texto)

    tab = TabelaExtraida(
        documento=documento, metodo=metodo, periodo=periodo, anos=(ano_a, ano_b),
        data_atualizacao=atualizacao.group(1) if atualizacao else None,
    )

    for linha in texto.splitlines():
        total = _RE_TOTAL.search(linha)
        if total:
            tab.total_oficial = (int(total.group(1)), int(total.group(2)))
            continue
        m = _RE_LINHA.match(linha)
        if not m:
            continue
        ra = padronizar_ra(m["ra"])
        if ra is None:
            continue
        a, b, q = _numero(m["a"]), _numero(m["b"]), _numero(m["q"])
        tab.linhas.append({"ra_original": m["ra"].strip(), "ra": ra, ano_a: a, ano_b: b})
        if q is None:
            tab.log.append({"documento": documento, "ra": ra, "tipo": "aviso",
                            "mensagem": f"coluna 'Quantit.' ilegível ({m['q']!r}); conferida pelo total"})
        elif b - a != q:
            tab.log.append({"documento": documento, "ra": ra, "tipo": "ERRO",
                            "mensagem": f"{ano_b}-{ano_a} = {b - a}, mas a tabela informa {q}"})

    # --- validações gerais -------------------------------------------------
    nomes = [l["ra"] for l in tab.linhas]
    if len(nomes) != len(set(nomes)):
        tab.log.append({"documento": documento, "ra": "-", "tipo": "ERRO", "mensagem": "RA repetida"})
    if tab.total_oficial is None:
        tab.log.append({"documento": documento, "ra": "-", "tipo": "ERRO", "mensagem": "linha TOTAL não encontrada"})
    else:
        for i, ano in enumerate((ano_a, ano_b)):
            soma = sum(l[ano] for l in tab.linhas)
            ok = soma == tab.total_oficial[i]
            tab.log.append({
                "documento": documento, "ra": "TOTAL", "tipo": "ok" if ok else "ERRO",
                "mensagem": f"{ano}: soma das {len(tab.linhas)} RAs = {soma}; TOTAL do relatório = {tab.total_oficial[i]}",
            })
    return tab


def extrair(caminho: Path) -> TabelaExtraida:
    """Tenta ler a página 1 como texto; se não houver tabela, usa OCR."""
    texto = texto_pdf(caminho)
    if _RE_ANOS.search(texto) and _RE_TOTAL.search(texto):
        return interpretar(texto, caminho.name, "texto (pdfplumber)")
    # tabela em imagem: OCR, mas o período (semestre/anual) vem do texto
    ocr = texto_ocr(caminho)
    periodo_txt = "semestre" if re.search(r"semestre", texto, re.I) else ""
    atualizacao = _RE_ATUALIZACAO.search(texto)
    extra = f"\n{periodo_txt}\natualizados em {atualizacao.group(1)}" if atualizacao else f"\n{periodo_txt}"
    return interpretar(ocr + extra, caminho.name, "OCR (Tesseract)")


# ---------------------------------------------------------------------------
# 4. Montagem da base
# ---------------------------------------------------------------------------
def para_formato_longo(tab: TabelaExtraida) -> pd.DataFrame:
    """Uma linha por (documento, RA, ano)."""
    registros = []
    for l in tab.linhas:
        for ano in tab.anos:
            registros.append({
                "documento": tab.documento, "metodo_extracao": tab.metodo,
                "data_atualizacao": tab.data_atualizacao, "periodo": tab.periodo,
                "ano": ano, "ra_original": l["ra_original"], "ra": l["ra"],
                "registros": l[ano],
            })
    return pd.DataFrame(registros)


def consolidar(longa: pd.DataFrame) -> pd.DataFrame:
    """
    Cada ano aparece em dois relatórios (ex.: 2019 no relatório de 2019 e no de
    2020). A SSP revisa os números, então fica valendo o relatório com a data de
    atualização mais recente.
    """
    df = longa.copy()
    df["_data"] = pd.to_datetime(df["data_atualizacao"], format="%d/%m/%Y")
    df = df.sort_values("_data").drop_duplicates(["periodo", "ano", "ra"], keep="last")
    return df.drop(columns="_data").sort_values(["periodo", "ano", "registros"],
                                                ascending=[True, True, False]).reset_index(drop=True)


def comparar_revisoes(longa: pd.DataFrame) -> pd.DataFrame:
    """Mostra quanto os números de um mesmo ano mudaram entre relatórios."""
    dup = longa.groupby(["periodo", "ano", "ra"]).filter(lambda g: g["documento"].nunique() > 1)
    if dup.empty:
        return pd.DataFrame()
    tabela = dup.pivot_table(index=["periodo", "ano", "ra"], columns="documento", values="registros")
    return tabela.reset_index()


def main(pasta_brutos: str, pasta_saida: str) -> None:
    pasta_brutos, pasta_saida = Path(pasta_brutos), Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    tabelas = [extrair(p) for p in sorted(pasta_brutos.glob("*.pdf"))]

    longa = pd.concat([para_formato_longo(t) for t in tabelas], ignore_index=True)
    log = pd.DataFrame([item for t in tabelas for item in t.log])
    base = consolidar(longa)
    revisoes = comparar_revisoes(longa)

    longa.to_csv(pasta_saida / "extracao_bruta.csv", index=False, encoding="utf-8-sig")
    base.to_csv(pasta_saida / "violencia_domestica_ra.csv", index=False, encoding="utf-8-sig")
    log.to_csv(pasta_saida / "log_validacao.csv", index=False, encoding="utf-8-sig")
    print(log.to_string(index=False))
    print(f"\n{len(base)} linhas na base consolidada -> {pasta_saida/'violencia_domestica_ra.csv'}")
    return tabelas, longa, base, log, revisoes


if __name__ == "__main__":
    main(*sys.argv[1:3])
