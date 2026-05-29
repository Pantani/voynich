"""Keep only the current human-facing tool set and generate a single entry page."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ActiveToolPage:
    filename: str
    title: str
    role: str
    next_step: str


@dataclass(frozen=True)
class CleanupResult:
    removed: list[str]
    already_absent: list[str]


ACTIVE_TOOL_PAGES = [
    ActiveToolPage(
        filename="rota_42g_ferramentas_ativas_r32.html",
        title="R42G - Painel unico",
        role="Comecar aqui e navegar sem se perder.",
        next_step="Abra a R42K para escolher o proximo alvo com menos atrito.",
    ),
    ActiveToolPage(
        filename="rota_42k_fila_priorizada_revisao_visual_r32.html",
        title="R42K - Fila priorizada",
        role="Ordenar as pendencias da R42F usando os fragmentos visuais da R42J.",
        next_step="Abra a R42L para confirmar a sugestao antes de mexer na R42F.",
    ),
    ActiveToolPage(
        filename="rota_42l_confirmacao_linhas_sugeridas_r32.html",
        title="R42L - Confirmar sugestao",
        role="Confirmar ou rejeitar a linha sugerida pela fila, com recortes e alternativas lado a lado.",
        next_step="Abra a R42M para conferir a captura fina antes de aplicar na R42F.",
    ),
    ActiveToolPage(
        filename="rota_42m_captura_fina_linhas_r32.html",
        title="R42M - Captura fina",
        role="Alinhar recortes mais estreitos usando a uniao dos fragmentos visuais.",
        next_step="Use como lupa; confirme a decisao na R42L/R42F.",
    ),
    ActiveToolPage(
        filename="rota_42f_escolha_linhas_visuais_sem_zona_r32.html",
        title="R42F - Escolher linha visual",
        role="Escolher a linha correta vendo recortes reais da pagina, sem precisar ler codigo EVA.",
        next_step="Clique no recorte que bate, depois copie/baixe o CSV.",
    ),
    ActiveToolPage(
        filename="rota_42d_sugestoes_opencv_linhas_r32.html",
        title="R42D - Sugestoes OpenCV",
        role="Transformar escolhas de linha e zonas pequenas em sugestoes pendentes para conferir.",
        next_step="Reexecute depois de preencher a R42F.",
    ),
    ActiveToolPage(
        filename="rota_42j_fragmentos_visuais_opencv_r32.html",
        title="R42J - Fragmentos visuais",
        role="Fazer uma analise mais fina por computer vision dentro de cada linha visual.",
        next_step="Use como lupa de fragmentos, depois volte para R42F ou R42C.",
    ),
    ActiveToolPage(
        filename="rota_42c_calibrador_linhas_baseline_r32.html",
        title="R42C - Calibrar linha fina",
        role="Ajustar a linha real com dois pontos e conferir pela lupa de recorte.",
        next_step="Confirme ou ajuste a baseline antes de usar na revisao final.",
    ),
    ActiveToolPage(
        filename="rota_42b_pacote_html_preenchimento_humano_r32.html",
        title="R42B - Preencher revisao R32",
        role="Fazer a decisao final olhando primeiro os recortes reais da pagina.",
        next_step="Use depois que as linhas estiverem mais faceis de localizar.",
    ),
    ActiveToolPage(
        filename="rota_42e_mapa_opencv_linhas_visuais_r32.html",
        title="R42E - Mapa de linhas OpenCV",
        role="Auditar as linhas visuais detectadas pela maquina quando algo parecer estranho.",
        next_step="Use como apoio, nao como decisao final.",
    ),
]


OBSOLETE_HTML_TOOLS = [
    "imagens_preview.html",
    "rota_9_revisao_manual.html",
    "rota_19_pacote_visual_direto_p0_p1.html",
    "rota_23_pacote_html_preenchimento_r21.html",
    "rota_28_pacote_anotacao_visual_formas_exatas.html",
    "rota_29_fila_fontes_imagem_formas_exatas.html",
    "rota_32_pacote_html_anotacao_visual_prontos.html",
    "rota_42_pacote_html_yale_iiif_highres_r32.html",
]


def render_dashboard_html() -> str:
    cards = "\n".join(
        f"""
        <a class="tool-card" href="{page.filename}">
          <span class="tool-title">{page.title}</span>
          <span class="tool-role">{page.role}</span>
          <span class="tool-next">{page.next_step}</span>
        </a>""".rstrip()
        for page in ACTIVE_TOOL_PAGES
    )
    active_list = "\n".join(f"<li>{page.title}</li>" for page in ACTIVE_TOOL_PAGES)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ferramentas ativas R32</title>
  <style>
    :root {{
      color-scheme: light;
      --paper: #f7f3ea;
      --ink: #22201d;
      --muted: #6f6a61;
      --line: #d7cdbd;
      --accent: #28776f;
      --accent-soft: #e4f1ee;
      --card: #fffaf2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--paper);
      color: var(--ink);
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 44px;
    }}
    header {{
      display: grid;
      gap: 10px;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--line);
    }}
    .eyebrow {{
      color: var(--accent);
      font-weight: 800;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(30px, 5vw, 58px);
      line-height: 0.98;
      letter-spacing: 0;
    }}
    p {{
      margin: 0;
      max-width: 760px;
      color: var(--muted);
      line-height: 1.5;
      font-size: 17px;
    }}
    .start {{
      margin: 18px 0 24px;
      padding: 14px 16px;
      border: 1px solid #a7cfc8;
      background: var(--accent-soft);
      border-radius: 8px;
      color: #184c47;
      font-weight: 750;
    }}
    .tools {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
    }}
    .tool-card {{
      display: grid;
      gap: 10px;
      min-height: 178px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--card);
      color: inherit;
      text-decoration: none;
    }}
    .tool-card:focus,
    .tool-card:hover {{
      outline: 3px solid rgba(40, 119, 111, 0.22);
      border-color: #8bbdb6;
    }}
    .tool-title {{
      font-size: 20px;
      font-weight: 850;
      line-height: 1.1;
    }}
    .tool-role {{
      color: var(--ink);
      line-height: 1.35;
    }}
    .tool-next {{
      align-self: end;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.35;
    }}
    section {{
      margin-top: 24px;
      display: grid;
      gap: 10px;
    }}
    h2 {{
      margin: 0;
      font-size: 20px;
    }}
    ol, ul {{
      margin: 0;
      padding-left: 22px;
      color: var(--muted);
      line-height: 1.6;
    }}
    code {{
      font: inherit;
      font-weight: 800;
      color: #443d35;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="eyebrow">Rota 42G</div>
      <h1>Ferramentas ativas</h1>
      <p>Esta e a entrada unica do fluxo atual. As ferramentas antigas foram removidas da pasta de paginas para nao confundir a revisao humana.</p>
    </header>
    <div class="start">Novo modo facil: use a R42K para escolher o alvo, a R42L para confirmar a sugestao, a R42M para conferir a captura fina, e depois aplique na R42F.</div>
    <div class="tools" aria-label="Ferramentas unicas atuais">
{cards}
    </div>
    <section>
      <h2>Ordem simples</h2>
      <ol>
        <li><code>R42K</code>: pegar o proximo alvo mais facil da fila.</li>
        <li><code>R42L</code>: confirmar se a linha sugerida realmente bate.</li>
        <li><code>R42M</code>: conferir a captura fina gerada pelos fragmentos.</li>
        <li><code>R42F</code>: aplicar a escolha de linha visual correta.</li>
        <li><code>R42D</code>: deixar o OpenCV transformar isso em sugestao pendente.</li>
        <li><code>R42J</code>: usar fragmentos visuais como lupa quando a linha ainda estiver dificil.</li>
        <li><code>R42C</code>: confirmar ou ajustar a linha fina.</li>
        <li><code>R42B</code>: fazer a revisao humana final.</li>
      </ol>
    </section>
    <section>
      <h2>O que ficou ativo</h2>
      <ul>
{active_list}
      </ul>
    </section>
  </main>
</body>
</html>
"""


def render_markdown_report(html_path: Path, cleanup: CleanupResult) -> str:
    active = "\n".join(f"- `{page.filename}`: {page.title}" for page in ACTIVE_TOOL_PAGES)
    removed = "\n".join(f"- `{name}`" for name in cleanup.removed) or "- nenhum nesta execucao"
    absent = "\n".join(f"- `{name}`" for name in cleanup.already_absent) or "- nenhum"
    return "\n".join(
        [
            "# Rota 42G: painel unico de ferramentas ativas R32",
            "",
            "Objetivo: remover do caminho as ferramentas HTML antigas e deixar uma entrada unica para o fluxo atual R42B-L.",
            "",
            f"HTML: `{html_path}`.",
            "",
            "Ferramentas ativas:",
            "",
            active,
            "",
            "Ferramentas antigas removidas nesta execucao:",
            "",
            removed,
            "",
            "Ferramentas antigas que ja estavam ausentes:",
            "",
            absent,
            "",
            "Leitura: esta limpeza nao altera evidencia, traducao ou planilhas de anotacao. Ela apenas reduz a superficie humana para as ferramentas atuais.",
        ]
    )


def remove_obsolete_html_tools(docs_dir: Path) -> CleanupResult:
    removed: list[str] = []
    already_absent: list[str] = []
    for filename in OBSOLETE_HTML_TOOLS:
        path = docs_dir / filename
        if path.exists():
            path.unlink()
            removed.append(filename)
        else:
            already_absent.append(filename)
    return CleanupResult(removed=removed, already_absent=already_absent)


def write_dashboard(docs_dir: Path) -> tuple[Path, Path, CleanupResult]:
    docs_dir.mkdir(parents=True, exist_ok=True)
    html_path = docs_dir / "rota_42g_ferramentas_ativas_r32.html"
    md_path = docs_dir / "rota_42g_ferramentas_ativas_r32.md"
    cleanup = remove_obsolete_html_tools(docs_dir)
    html_path.write_text(render_dashboard_html(), encoding="utf-8")
    md_path.write_text(render_markdown_report(html_path, cleanup), encoding="utf-8")
    return html_path, md_path, cleanup


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-dir",
        default=str(ROOT / "docs"),
        help="Directory containing the generated HTML documentation tools",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    html_path, md_path, cleanup = write_dashboard(Path(args.docs_dir))
    print(f"active_tools={len(ACTIVE_TOOL_PAGES)}")
    print(f"removed_obsolete={len(cleanup.removed)}")
    print(f"already_absent={len(cleanup.already_absent)}")
    print(f"html={html_path.resolve()}")
    print(f"md={md_path.resolve()}")


if __name__ == "__main__":
    main()
