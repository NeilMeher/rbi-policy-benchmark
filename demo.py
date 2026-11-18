"""Build the offline policy evidence explorer."""
import html
from pathlib import Path

from benchmark import Ranker, CUTOFF, predict, read_data, rule

ROOT = Path(__file__).resolve().parent


def build(path):
    rows = read_data()
    ranker = Ranker([row for row in rows if row["date"] < CUTOFF])
    slides = []
    options = []
    for i, row in enumerate(rows):
        day = row["date"]
        options.append(f'<option value="{i}">{day}</option>')
        predictions = []
        for name, score in (("Rules", rule), ("Naive Bayes", ranker.score)):
            prediction = predict(row, score)
            sentence = html.escape(row["digest"][prediction["evidence"]])
            predictions.append(f'<section><h3>{name}</h3><p>{prediction["action"]}</p>'
                               f'<p>{sentence}</p></section>')
        hidden = " hidden" if i else ""
        slides.append(f'<article id="decision-{i}"{hidden}><h2>{day}</h2>'
                      f'<p>Gold label: {row["action"]} · {row["rate_bps"]/100:.2f}% · '
                      f'{row["change_bps"]:+d} basis points</p>'
                      f'<p>{html.escape(row["rationale"])}</p><div class="grid">{"".join(predictions)}</div>'
                      f'<p><a href="{html.escape(row["source"], quote=True)}">Open the RBI source</a>'
                      f' · {html.escape(row["locator"])}</p></article>')
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RBI policy evidence</title><style>
body{font-family:system-ui,sans-serif;color:#193145;background:#f3f6f8;max-width:62rem;margin:4rem auto;padding:0 1rem;line-height:1.55}
h1{font-size:clamp(2rem,6vw,3.5rem);line-height:1.1;letter-spacing:-.05em}select{font:inherit;margin:.6rem;padding:.4rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));gap:1rem}
section{background:white;border:1px solid #ced8e0;border-radius:.6rem;padding:1rem}a{color:#075c66}
</style></head><body><h1>RBI policy evidence</h1>
<p>Inspect the policy repo decision and compare the sentences selected by two extractors.</p>
<label for="meeting">Decision date</label><select id="meeting">""" + "".join(options) + """</select>
<div aria-live="polite">""" + "".join(slides) + """</div><script>
const select = document.querySelector("#meeting");
function show(){for (const card of document.querySelectorAll("article")) card.hidden = card.id !== "decision-" + select.value;}
const initial = new URLSearchParams(location.search).get("date");
const option = [...select.options].find(item => item.textContent === initial);
if (option) {select.value = option.value; show();}
select.addEventListener("change", show);
</script></body></html>"""
    path.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    build(ROOT / "index.html")
