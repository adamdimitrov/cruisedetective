#!/usr/bin/env python3
"""Make the charts on every statistics page embeddable (link building).

For every <div class="bpa-chart" id="..."> on a published page (sitemap.xml) :
  * writes a standalone embed page to embed/<page path>/<chart id>.html
    (served at /embed/<page path>/<chart id>, frameable from any site, noindex)
  * adds an "Embed this chart" button under the chart, which reveals a
    copy-paste snippet: the iframe plus a plain-text source link back to the
    statistics page (the backlink we want).

Re-run after editing or adding charts or statistics pages (it replaces what it
added before, so it is safe to run any number of times):

    python3 scripts/build_stats_embeds.py
    python3 scripts/build_stats_embeds.py --check   # exit 1 if a page is out of date

Iframe heights come from scripts/stats_embed_heights.json, keyed by chart id:
the tallest rendering of that chart in any language at 360px and 760px wide,
measured in Chrome, plus 20px slack. Charts missing from it get an estimate.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.thecruisedetective.com"
HEIGHTS_FILE = os.path.join(ROOT, "scripts", "stats_embed_heights.json")

# button, copy, copied, note, "Source", "by", credit
LABELS = {
    "en": ("Embed this chart", "Copy code", "Copied!", "Free to use on your site, article or report. Please keep the source link.", "Source", "by The Cruise Detective", "Chart by The Cruise Detective"),
    "fr": ("Intégrer ce graphique", "Copier le code", "Copié !", "Libre d'utilisation sur votre site, article ou rapport. Merci de garder le lien source.", "Source", "par The Cruise Detective", "Graphique : The Cruise Detective"),
    "de": ("Grafik einbetten", "Code kopieren", "Kopiert!", "Frei nutzbar auf Ihrer Website, in Artikeln oder Berichten. Bitte den Quellenlink beibehalten.", "Quelle", "von The Cruise Detective", "Grafik: The Cruise Detective"),
    "es": ("Insertar este gráfico", "Copiar código", "¡Copiado!", "Uso libre en tu web, artículo o informe. Mantén el enlace a la fuente.", "Fuente", "de The Cruise Detective", "Gráfico: The Cruise Detective"),
    "it": ("Incorpora il grafico", "Copia il codice", "Copiato!", "Libero da usare su sito, articolo o report. Mantieni il link alla fonte.", "Fonte", "di The Cruise Detective", "Grafico: The Cruise Detective"),
    "nl": ("Grafiek insluiten", "Code kopiëren", "Gekopieerd!", "Vrij te gebruiken op je site, in artikelen of rapporten. Laat de bronlink staan.", "Bron", "door The Cruise Detective", "Grafiek: The Cruise Detective"),
    "pl": ("Osadź wykres", "Kopiuj kod", "Skopiowano!", "Możesz go używać na stronie, w artykule lub raporcie. Zachowaj link do źródła.", "Źródło", "The Cruise Detective", "Wykres: The Cruise Detective"),
    "ro": ("Încorporează graficul", "Copiază codul", "Copiat!", "Liber de folosit pe site, în articole sau rapoarte. Păstrează linkul către sursă.", "Sursa", "de la The Cruise Detective", "Grafic: The Cruise Detective"),
    "ja": ("グラフを埋め込む", "コードをコピー", "コピーしました", "サイト、記事、レポートで自由に使えます。出典リンクは残してください。", "出典", "The Cruise Detective", "グラフ：The Cruise Detective"),
    "pt": ("Incorporar este gráfico", "Copiar código", "Copiado!", "Uso livre no seu site, artigo ou relatório. Mantenha o link para a fonte.", "Fonte", "da The Cruise Detective", "Gráfico: The Cruise Detective"),
}

MARK_START = "<!--cd-embed-->"
MARK_END = "<!--/cd-embed-->"

EMBED_CSS = """<style id="cd-embed-css">
.bpa-embed{margin:-8px 0 20px}
.bpa-embed-btn{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid #cbd5e1;border-radius:9999px;padding:6px 14px;font:700 12.5px/1.2 inherit;color:#1e3a5f;cursor:pointer}
.bpa-embed-btn:hover{background:#f1f5f9}
.bpa-embed-panel{margin-top:10px;padding:14px;border:1px solid #e2e8f0;border-radius:12px;background:#f8fafc}
.bpa-embed-panel[hidden]{display:none}
.bpa-embed-code{width:100%;box-sizing:border-box;min-height:118px;font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace;color:#0f172a;border:1px solid #cbd5e1;border-radius:8px;padding:10px;background:#fff;resize:vertical}
.bpa-embed-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-top:8px}
.bpa-embed-copy{background:#1e3a5f;color:#fff;border:0;border-radius:8px;padding:8px 14px;font:700 13px/1 inherit;cursor:pointer}
.bpa-embed-note{font-size:12.5px;color:#475569;line-height:1.4;flex:1;min-width:200px}
</style>"""

EMBED_JS = """<script id="cd-embed-js">(function(){
document.addEventListener('click',function(e){
  var b=e.target.closest('.bpa-embed-btn');
  if(b){var p=document.getElementById(b.getAttribute('aria-controls'));if(!p)return;var open=p.hasAttribute('hidden');
    if(open){p.removeAttribute('hidden');}else{p.setAttribute('hidden','');}
    b.setAttribute('aria-expanded',open?'true':'false');
    if(open&&window.gtag){gtag('event','embed_open',{chart_id:b.getAttribute('data-chart')});}
    return;}
  var c=e.target.closest('.bpa-embed-copy');
  if(c){var t=c.closest('.bpa-embed-panel').querySelector('textarea');t.select();
    var done=function(){var l=c.textContent;c.textContent=c.getAttribute('data-done');setTimeout(function(){c.textContent=l;},1800);};
    if(navigator.clipboard){navigator.clipboard.writeText(t.value).then(done,function(){document.execCommand('copy');done();});}
    else{document.execCommand('copy');done();}
    if(window.gtag){gtag('event','embed_copy',{chart_id:c.getAttribute('data-chart')});}}
});})();</script>"""

EMBED_PAGE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title} | The Cruise Detective</title>
<meta name="robots" content="noindex, follow"/>
<link rel="canonical" href="{page_url}"/>
<style>
html,body{{margin:0;padding:0;background:#fff}}
body{{font-family:'Plus Jakarta Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#0f172a}}
.bpa-chart{{margin:0 !important}}
.bpa-credit{{font-size:12px;color:#64748b;margin:8px 4px 0;text-align:right}}
.bpa-credit a{{color:#1e3a5f;font-weight:700;text-decoration:none}}
{chart_css}
</style>
</head>
<body>
{chart}
<div class="bpa-credit"><a href="{page_url}?utm_source=embed&amp;utm_medium=chart&amp;utm_campaign={chart_id}" target="_blank" rel="noopener">{credit}</a></div>
</body>
</html>
"""


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def write(rel, text):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(text)


def published_paths():
    """URL paths listed in sitemap.xml, e.g. /paris-tourism-statistics."""
    sm = read("sitemap.xml")
    out = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", sm):
        path = urllib.parse.unquote(urllib.parse.urlparse(loc.strip()).path).rstrip("/")
        if path:
            out.append(path)
    return out


def stats_pages():
    pages = []
    for path in published_paths():
        rel = path.lstrip("/") + "/index.html"
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        s = read(rel)
        if 'class="bpa-chart" id="' not in s:
            continue
        lang = re.search(r'<html lang="([a-z]+)', s).group(1)
        if lang not in LABELS:
            sys.exit(f"no embed labels for language '{lang}' ({rel}); add it to LABELS")
        crumb = re.search(r'class="ltt-bc-current">([^<]+)<', s)
        name = html.unescape(crumb.group(1)) if crumb else html.unescape(re.search(r"<title>([^<:|]+)", s).group(1))
        name = re.sub(r"\s*[(（]\s*\d{4}\s*[)）]\s*$", "", name).strip()
        pages.append({"file": rel, "path": path, "lang": lang, "page_name": name})
    return pages


def div_end(s, start):
    """Index just past the </div> that closes the <div> opening at `start`."""
    depth = 0
    for m in re.compile(r"<div\b|</div>").finditer(s, start):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return m.end()
    raise ValueError("unbalanced div at %d" % start)


def chart_css(s):
    """The .bpa-* rules of the page (plus their @media wrappers), for the standalone embed."""
    style = re.search(r'<style id="cd-kill-webflow-badge">(.*?)</style>', s, re.S).group(1)
    keep, lines, i = [], style.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("@media"):
            block = [line]
            i += 1
            while i < len(lines) and not lines[i].startswith("}"):
                block.append(lines[i])
                i += 1
            inner = [l for l in block[1:] if l.strip().startswith(".bpa-")]
            if inner:
                keep.append("\n".join([block[0]] + inner + ["}"]))
        elif line.startswith(".bpa-") and not line.startswith((".bpa-embed", ".bpa-toc", ".bpa-tile", ".bpa-cite", ".bpa-sources")):
            keep.append(line)
        i += 1
    return "\n".join(keep)


def estimate_height(chart_html):
    rows = chart_html.count('class="bpa-row"')
    pair = 'class="bpa-pair"' in chart_html
    legend = 'class="bpa-legend"' in chart_html
    return 170 + (40 if legend else 0) + rows * (36 if pair else 32)


def build(page, heights, files):
    lg = LABELS[page["lang"]]
    btn, copy, copied, note, src_word, by, credit = lg
    s = read(page["file"])
    s = re.sub(re.escape(MARK_START) + r".*?" + re.escape(MARK_END), "", s, flags=re.S)
    s = re.sub(r'<style id="cd-embed-css">.*?</style>', "", s, flags=re.S)
    s = re.sub(r'<script id="cd-embed-js">.*?</script>', "", s, flags=re.S)

    css = chart_css(s)
    page_url = SITE + urllib.parse.quote(page["path"])
    source_html = f'{src_word}: <a href="{page_url}">{html.escape(page["page_name"])}</a>, {by}'

    out, last, n = [], 0, 0
    for m in re.finditer(r'<div class="bpa-chart" id="([^"]+)"', s):
        chart_id = m.group(1)
        end = div_end(s, m.start())
        chart = s[m.start():end]
        title = html.unescape(re.search(r'class="bpa-chart-title"[^>]*>([^<]*)<', chart).group(1)).strip()
        embed_rel = "embed" + page["path"] + "/" + chart_id + ".html"
        embed_url = SITE + urllib.parse.quote("/embed" + page["path"] + "/" + chart_id)
        files[embed_rel] = EMBED_PAGE.format(
            lang=page["lang"], title=html.escape(title), page_url=page_url, chart_css=css,
            chart=chart, chart_id=chart_id, credit=credit)
        height = heights.get(chart_id) or estimate_height(chart)
        snippet = (
            f'<iframe src="{embed_url}" title="{html.escape(title)}" width="100%" '
            f'height="{height}" style="border:0;max-width:760px" loading="lazy"></iframe>\n'
            f'<p style="font-size:13px">{source_html}</p>'
        )
        panel_id = "bpa-embed-" + chart_id
        ui = (
            f'{MARK_START}<div class="bpa-embed">'
            f'<button type="button" class="bpa-embed-btn" aria-expanded="false" aria-controls="{panel_id}" data-chart="{chart_id}">'
            f'<span aria-hidden="true">&lt;/&gt;</span> {btn}</button>'
            f'<div class="bpa-embed-panel" id="{panel_id}" hidden>'
            f'<textarea class="bpa-embed-code" readonly aria-label="{btn}">{html.escape(snippet)}</textarea>'
            f'<div class="bpa-embed-row"><button type="button" class="bpa-embed-copy" data-chart="{chart_id}" data-done="{copied}">{copy}</button>'
            f'<span class="bpa-embed-note">{note}</span></div></div></div>{MARK_END}'
        )
        out.append(s[last:end] + ui)
        last = end
        n += 1
    out.append(s[last:])
    s = "".join(out)
    s = s.replace("</head>", EMBED_CSS + "</head>", 1)
    s = s.replace("</body>", EMBED_JS + "</body>", 1)
    files[page["file"]] = s
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report pages that are out of date, write nothing")
    args = ap.parse_args()
    heights = {}
    if os.path.exists(HEIGHTS_FILE):
        with open(HEIGHTS_FILE, encoding="utf-8") as fh:
            heights = json.load(fh)
    files, total, pages = {}, 0, stats_pages()
    for page in pages:
        total += build(page, heights, files)
    stale = [rel for rel, text in files.items()
             if not os.path.exists(os.path.join(ROOT, rel)) or read(rel) != text]
    if args.check:
        for rel in stale:
            print("out of date:", rel)
        print(f"{len(pages)} statistics pages, {total} charts, {len(stale)} file(s) out of date")
        sys.exit(1 if stale else 0)
    for rel in stale:
        write(rel, files[rel])
    print(f"{len(pages)} statistics pages, {total} embeddable charts, {len(stale)} file(s) written")


if __name__ == "__main__":
    main()
