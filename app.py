"""Streamlit UI for the invoice extraction pipeline (redesigned).

Run:  streamlit run app.py
Set PIPELINE_MODULE to your pipeline script's name (without .py).
"""
import html
import importlib
import json
from pathlib import Path

import pandas as pd
import streamlit as st
from pydantic import ValidationError

from schemas.invoice_schema import InvoiceData

PIPELINE_MODULE = "main"  # <- change to your pipeline script's filename (no .py)
P = importlib.import_module(PIPELINE_MODULE)
BASE = Path(__file__).resolve().parent

st.set_page_config(page_title="Invoice Extractor", page_icon="🧾", layout="wide")

# ───────────────────────── Design tokens (light + dark) ─────────────────────────
LIGHT = """
--bg:#F3F5FA; --surface:#FFFFFF; --surface-2:#F7F8FC; --line:#E2E6F0; --ink:#0F172A; --muted:#5C6880;
--brand:#4F46E5; --brand-hover:#4339CC; --on-brand:#FFFFFF; --brand-soft:#ECEBFF;
--ok:#0F7B55; --ok-soft:#DDF5EA; --warn:#A85F00; --warn-soft:#FFF1D1; --bad:#C62828; --bad-soft:#FDE6E6;
--shadow:0 1px 2px rgba(15,23,42,.05),0 8px 24px -12px rgba(15,23,42,.14); --hero-a:#241B6B; --hero-b:#4F46E5; --hero-c:#8B5CF6;
"""
DARK = """
--bg:#0A0E1A; --surface:#121929; --surface-2:#182136; --line:#263150; --ink:#E9EDF7; --muted:#93A0BC;
--brand:#8E8FFF; --brand-hover:#A5A6FF; --on-brand:#0A0E1A; --brand-soft:#232A5A;
--ok:#4ADE9B; --ok-soft:#10382B; --warn:#FBBF4A; --warn-soft:#3B2C0C; --bad:#FF7B7B; --bad-soft:#401818;
--shadow:0 1px 2px rgba(0,0,0,.4),0 12px 30px -14px rgba(0,0,0,.7); --hero-a:#120D3D; --hero-b:#3B34B8; --hero-c:#7A4DE0;
"""

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=DM+Sans:wght@400;500;600&display=swap');
:root{--r-sm:8px;--r-md:12px;--r-lg:20px;--ease:cubic-bezier(.22,.8,.3,1);--spring:cubic-bezier(.34,1.56,.64,1)}
@property --n{syntax:'<integer>';initial-value:0;inherits:false}
html,body,.stApp{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp{background:var(--bg);transition:background .35s var(--ease)}
h1,h2,h3,.display{font-family:'Sora',sans-serif!important;letter-spacing:-.02em;color:var(--ink)}
#MainMenu,footer{visibility:hidden}
[data-testid=stHeader]{background:transparent}
.block-container{max-width:1120px;padding-top:2.2rem;padding-bottom:4rem}
[data-testid=stSidebar]{background:var(--surface);border-right:1px solid var(--line)}
.stApp p,.stApp label,.stApp li,[data-testid=stWidgetLabel] *,[data-testid=stCaptionContainer] *{color:var(--ink)}
[data-testid=stCaptionContainer] *{color:var(--muted)}
:focus-visible{outline:2px solid var(--brand)!important;outline-offset:2px}

/* ── Buttons: explicit bg + text colour so they are always legible ── */
.stApp button,.stApp [data-testid^="stBaseButton"]{
  background:var(--surface)!important;color:var(--ink)!important;border:1px solid var(--line)!important;
  border-radius:10px!important;font-weight:600!important;position:relative;overflow:hidden;
  transition:transform .2s var(--spring),box-shadow .25s var(--ease),border-color .2s,background .2s!important}
.stApp button p,.stApp button span,.stApp button div{color:inherit!important}
.stApp button:hover{transform:translateY(-2px);border-color:var(--brand)!important;box-shadow:var(--shadow);color:var(--brand)!important;background:var(--surface-2)!important}
.stApp button:active{transform:translateY(0) scale(.97)}
.stApp [data-testid="stBaseButton-primary"],.stApp [data-testid="stBaseButton-primaryFormSubmit"]{
  background:var(--brand)!important;border-color:var(--brand)!important;color:var(--on-brand)!important}
.stApp [data-testid="stBaseButton-primary"]:hover,.stApp [data-testid="stBaseButton-primaryFormSubmit"]:hover{
  background:var(--brand-hover)!important;color:var(--on-brand)!important}
.stApp [data-testid="stBaseButton-primary"]::after,.stApp [data-testid="stBaseButton-primaryFormSubmit"]::after{
  content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.35) 50%,transparent 65%);
  transform:translateX(-120%)}
.stApp [data-testid="stBaseButton-primary"]:hover::after,.stApp [data-testid="stBaseButton-primaryFormSubmit"]:hover::after{
  transform:translateX(120%);transition:transform .7s var(--ease)}

/* Segmented nav */
[data-testid=stSegmentedControl]{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:4px;width:max-content;margin-bottom:1.2rem}
[data-testid=stSegmentedControl] button{border:0!important;background:transparent!important;border-radius:10px!important;padding:.35rem 1.1rem!important;color:var(--muted)!important}
[data-testid=stSegmentedControl] button:hover{transform:none;box-shadow:none;color:var(--ink)!important}
[data-testid="stBaseButton-segmented_controlActive"]{background:var(--brand)!important;color:var(--on-brand)!important;box-shadow:var(--shadow)}
[data-testid="stBaseButton-segmented_controlActive"]:hover{color:var(--on-brand)!important}

/* Inputs */
[data-baseweb=input],[data-baseweb=select]>div,[data-baseweb=textarea]{background:var(--surface)!important;border-color:var(--line)!important;border-radius:10px!important}
[data-baseweb=input] input,[data-baseweb=select] *{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;background:transparent!important}
[data-baseweb=popover] ul,[data-baseweb=popover] [role=listbox]{background:var(--surface)!important}
[data-baseweb=popover] li{color:var(--ink)!important}
[data-baseweb=popover] li:hover{background:var(--brand-soft)!important}
[data-baseweb=slider] [role=slider]{background:var(--brand)!important;box-shadow:0 0 0 4px var(--brand-soft)}
[data-testid=stSliderThumbValue]{color:var(--brand)!important}
[data-testid=stFileUploaderDropzone]{background:var(--surface);border:1.5px dashed var(--line);border-radius:var(--r-lg);padding:1.6rem;transition:all .3s var(--ease)}
[data-testid=stFileUploaderDropzone]:hover{border-color:var(--brand);background:var(--brand-soft);transform:scale(1.005)}
[data-testid=stFileUploaderDropzone] *{color:var(--ink)}
[data-testid=stExpander]{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md)}
[data-testid=stExpander] summary,[data-testid=stExpander] summary *{color:var(--ink)!important}
[data-testid=stForm]{border:0;padding:0}
[data-testid=stAlert]{border-radius:var(--r-md)}
.stProgress>div>div>div>div{background:linear-gradient(90deg,var(--brand),#A78BFA,var(--brand));background-size:200% 100%;animation:flow 1.6s linear infinite}
@keyframes flow{to{background-position:-200% 0}}

/* ── Hero ── */
.hero{position:relative;overflow:hidden;display:flex;justify-content:space-between;align-items:center;gap:2rem;
  padding:2.4rem 2.6rem;border-radius:var(--r-lg);color:#fff;margin-bottom:1.3rem;
  background:linear-gradient(120deg,var(--hero-a),var(--hero-b),var(--hero-c),var(--hero-b));background-size:300% 300%;
  animation:aurora 14s ease-in-out infinite,rise .7s var(--ease) both;box-shadow:var(--shadow)}
.hero::before{content:"";position:absolute;width:320px;height:320px;right:-60px;top:-120px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.28),transparent 65%);animation:drift 9s ease-in-out infinite alternate}
.hero h1{color:#fff!important;font-size:2.4rem;line-height:1.12;margin:0 0 .6rem;padding:0;max-width:30rem}
.hero p{margin:0;max-width:32rem;color:rgba(255,255,255,.82)!important;font-size:1.04rem;line-height:1.55}
.stage{position:relative;flex:none;width:210px;height:170px;z-index:1}
.doc{position:absolute;left:20px;top:0;width:150px;height:170px;border-radius:12px;background:rgba(255,255,255,.14);
  backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.35);padding:18px 16px;display:flex;flex-direction:column;gap:12px;overflow:hidden}
.doc i{display:block;height:8px;border-radius:4px;background:rgba(255,255,255,.45);animation:glow 3.6s ease-in-out infinite}
.doc i:nth-child(1){width:50%;animation-delay:.3s}.doc i:nth-child(2){width:92%;animation-delay:.8s}
.doc i:nth-child(3){width:75%;animation-delay:1.3s}.doc i:nth-child(4){width:85%;animation-delay:1.8s}
.doc i:nth-child(5){width:42%;margin-left:auto;animation-delay:2.3s}
.doc b{position:absolute;left:0;right:0;height:38px;top:-38px;background:linear-gradient(180deg,transparent,rgba(255,255,255,.5),transparent);
  border-bottom:2px solid #fff;animation:scan 3.6s ease-in-out infinite}
.chip{position:absolute;padding:.22rem .65rem;border-radius:99px;font-size:.78rem;font-weight:700;background:#fff;color:#0F7B55;
  box-shadow:0 8px 20px rgba(0,0,0,.25);animation:bob 3.2s ease-in-out infinite}
.chip.a{right:0;top:26px}.chip.b{left:0;bottom:22px;color:#A85F00;animation-delay:-1.4s}
@keyframes scan{0%{top:-38px}65%,100%{top:170px}}
@keyframes glow{0%,100%{background:rgba(255,255,255,.4)}50%{background:#fff}}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@keyframes aurora{0%,100%{background-position:0 50%}50%{background-position:100% 50%}}
@keyframes drift{to{transform:translate(-60px,50px) scale(1.2)}}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}

/* ── KPI strip ── */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:.9rem;margin-bottom:1.3rem}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);padding:1rem 1.2rem;box-shadow:var(--shadow);
  display:flex;flex-direction:column;gap:.1rem;transition:transform .3s var(--spring)}
.kpi:hover{transform:translateY(-3px)}
.kpi span:last-child{color:var(--muted);font-size:.88rem}
.count{--n:var(--to);font-family:'Sora',sans-serif;font-size:2rem;font-weight:700;line-height:1.15;animation:count 1.2s var(--ease) both;counter-reset:n var(--n)}
.count::after{content:counter(n)}
.kpi.ok .count{color:var(--ok)}.kpi.warn .count{color:var(--warn)}.kpi.bad .count{color:var(--bad)}
@keyframes count{from{--n:0}to{--n:var(--to)}}

/* ── Pipeline stepper ── */
.proc{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);padding:1.1rem 1.3rem;margin:.6rem 0;box-shadow:var(--shadow);animation:rise .4s var(--ease) both}
.proc-name{font-weight:600;margin-bottom:.9rem}
.steps{display:flex;align-items:center}
.step{display:flex;align-items:center;gap:.55rem;flex:1;color:var(--muted);font-size:.9rem;white-space:nowrap}
.step:last-child{flex:0}
.step::after{content:"";flex:1;height:2px;margin:0 .7rem;background:var(--line);transform-origin:left}
.step:last-child::after{display:none}
.dot{width:26px;height:26px;border-radius:50%;border:2px solid var(--line);display:grid;place-items:center;font-size:.8rem;font-weight:700;color:var(--on-brand);flex:none}
.step.active{color:var(--ink);font-weight:600}
.step.active .dot{border-color:var(--brand-soft);border-top-color:var(--brand);animation:spin .8s linear infinite}
.step.done{color:var(--ink)}
.step.done .dot{background:var(--brand);border-color:var(--brand);animation:pop .45s var(--spring)}
.step.done::after{background:var(--brand);animation:draw .5s var(--ease)}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes pop{0%{transform:scale(.5)}100%{transform:scale(1)}}
@keyframes draw{from{transform:scaleX(0)}}

/* ── Confidence ledger ── */
.ledger{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);overflow:hidden;margin:.6rem 0 1.2rem;box-shadow:var(--shadow)}
.row{display:grid;grid-template-columns:190px 1fr 230px;gap:1.1rem;align-items:start;padding:.9rem 1.2rem;border-bottom:1px solid var(--line);
  border-left:3px solid transparent;animation:rise .5s var(--ease) both;animation-delay:calc(var(--i) * 45ms);transition:background .2s,padding-left .25s var(--ease)}
.row:last-child{border-bottom:0}
.row:hover{background:var(--surface-2);padding-left:1.5rem}
.row.bad{border-left-color:var(--bad);background:var(--bad-soft)}
.row.warn{border-left-color:var(--warn);background:var(--warn-soft)}
.row .k{font-weight:600}
.row .v{word-break:break-word;font-variant-numeric:tabular-nums;color:var(--ink)}
.nil{color:var(--muted);font-style:italic}
.conf{display:flex;align-items:center;gap:.7rem}
.gauge{flex:1;height:8px;border-radius:5px;background:var(--line);overflow:hidden}
.gauge span{display:block;height:100%;width:var(--w);border-radius:5px;transform-origin:left;animation:fill 1.1s var(--ease) both;animation-delay:calc(var(--i) * 45ms + 150ms)}
.ok .gauge span{background:var(--ok)}.warn .gauge span{background:var(--warn)}.bad .gauge span{background:var(--bad)}
@keyframes fill{from{transform:scaleX(0)}}
.pct{font-variant-numeric:tabular-nums;font-weight:700;min-width:3.2rem;text-align:right;color:var(--ink)}
details{margin-top:.45rem;color:var(--muted);font-size:.88rem}
summary{cursor:pointer;color:var(--brand);font-weight:600;width:max-content}
details[open] .why{animation:rise .3s var(--ease) both}
.why{padding:.4rem 0 0;line-height:1.5;color:var(--muted)}
.why b{color:var(--ink)}
.pill{display:inline-block;padding:.2rem .7rem;border-radius:99px;font-size:.8rem;font-weight:700;background:var(--brand-soft);color:var(--brand)}
.pill.ok{background:var(--ok-soft);color:var(--ok)}.pill.warn{background:var(--warn-soft);color:var(--warn)}.pill.bad{background:var(--bad-soft);color:var(--bad)}
.pill.stamp{animation:stamp .6s var(--spring) both}
@keyframes stamp{0%{transform:scale(2.4) rotate(-14deg);opacity:0}100%{transform:scale(1) rotate(-3deg);opacity:1}}
.head{display:flex;align-items:center;gap:.8rem;flex-wrap:wrap;margin:.8rem 0 .2rem}
.head h3{margin:0;padding:0}
.empty{border:1.5px dashed var(--line);border-radius:var(--r-lg);padding:2.4rem;text-align:center;color:var(--muted);background:var(--surface);animation:rise .5s var(--ease) both}
.empty .ico{font-size:2.2rem;display:block;animation:bob 3s ease-in-out infinite}
.empty b{display:block;color:var(--ink);font-size:1.1rem;margin:.4rem 0 .3rem}

/* Export table */
.tbl-wrap{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);box-shadow:var(--shadow);margin-bottom:1rem;animation:rise .5s var(--ease) both}
.tbl-wrap table{border-collapse:collapse;width:100%;font-size:.9rem}
.tbl-wrap th{background:var(--surface-2);color:var(--muted);text-align:left;padding:.7rem 1rem;font-weight:600;white-space:nowrap;border-bottom:1px solid var(--line)}
.tbl-wrap td{padding:.65rem 1rem;color:var(--ink);border-bottom:1px solid var(--line);white-space:nowrap}
.tbl-wrap tr:last-child td{border-bottom:0}
.tbl-wrap tbody tr:hover td{background:var(--brand-soft)}

@media (max-width:760px){
  .hero{flex-direction:column;align-items:flex-start}.stage{display:none}.kpis{grid-template-columns:repeat(2,1fr)}
  .row{grid-template-columns:1fr;gap:.4rem}.steps{flex-direction:column;align-items:flex-start;gap:.5rem}.step::after{display:none}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.count::after{content:counter(n)}}
"""

dark = st.session_state.get("dark", False)  # toggle widget below writes this key
st.markdown(f"<style>:root{{{DARK if dark else LIGHT}}}{BASE_CSS}</style>", unsafe_allow_html=True)


# ───────────────────────── Helpers ─────────────────────────
def md(s: str):
    """Render HTML safely through markdown (strips indentation/blank lines)."""
    st.markdown("\n".join(l.strip() for l in s.splitlines() if l.strip()), unsafe_allow_html=True)


esc = lambda v: html.escape(str(v))
STEPS = ["Read PDF", "Extract text", "Extract fields", "Score confidence"]
STATUS = {"review": ("Awaiting review", ""), "accepted": ("Accepted", "ok stamp"),
          "rejected": ("Rejected", "warn"), "failed": ("Failed", "bad")}

st.session_state.setdefault("records", {})
st.session_state.setdefault("view", "Upload")
if "goto" in st.session_state:  # navigation requested by a previous step
    st.session_state.view = st.session_state.pop("goto")
records = st.session_state.records


def stepper(name, active):
    items = ""
    for i, label in enumerate(STEPS):
        state = "done" if i < active else "active" if i == active else "todo"
        items += f'<div class="step {state}"><span class="dot">{"✓" if state == "done" else ""}</span>{label}</div>'
    return f'<div class="proc"><div class="proc-name">{esc(name)}</div><div class="steps">{items}</div></div>'


def kpi_strip():
    vals = [r["status"] for r in records.values()]
    cells = [("Uploaded", len(vals), ""), ("Awaiting review", vals.count("review"), "warn"),
             ("Accepted", vals.count("accepted"), "ok"), ("Failed", vals.count("failed"), "bad")]
    inner = "".join(f'<div class="kpi {t}"><span class="count" style="--to:{n}"></span><span>{l}</span></div>'
                    for l, n, t in cells)
    md(f'<div class="kpis">{inner}</div>')


def ledger(inv_dict, assessment, threshold):
    rows = ""
    for i, (field, value) in enumerate(inv_dict.items()):
        d = assessment.fields.get(field)
        val = '<span class="nil">Not found</span>' if value in (None, "") else esc(value)
        if d is None:
            tier, conf, why = "", '<span class="pill">Not assessed</span>', ""
        else:
            c = d.confidence
            tier = "ok" if c >= 0.9 else "warn" if c >= threshold else "bad"
            conf = (f'<div class="gauge"><span style="--w:{c * 100:.0f}%"></span></div>'
                    f'<span class="pct">{c * 100:.0f}%</span>')
            ev = esc(d.evidence) if d.evidence else "No supporting text"
            why = (f'<details><summary>Evidence</summary><div class="why"><b>Found:</b> {ev}<br>'
                   f'<b>Why:</b> {esc(d.reason)}</div></details>')
        rows += (f'<div class="row {tier}" style="--i:{i}"><div class="k">{esc(field)}</div>'
                 f'<div class="v">{val}{why}</div><div class="conf">{conf}</div></div>')
    md(f'<div class="ledger">{rows}</div>')


def empty(icon, title, text):
    md(f'<div class="empty"><span class="ico">{icon}</span><b>{title}</b>{text}</div>')


def run_extraction(files):
    docs_dir = BASE / "documents"
    docs_dir.mkdir(exist_ok=True)
    slot, bar = st.empty(), st.progress(0.0)
    for n, f in enumerate(files, start=1):
        (docs_dir / f.name).write_bytes(f.getbuffer())
        try:
            slot.markdown(stepper(f.name, 0), unsafe_allow_html=True)
            doc = P.load_document(str(Path("documents") / f.name))
            slot.markdown(stepper(f.name, 1), unsafe_allow_html=True)
            text = P.extract_text(doc)
            slot.markdown(stepper(f.name, 2), unsafe_allow_html=True)
            invoice = P.extract_invoice_information(text)
            slot.markdown(stepper(f.name, 3), unsafe_allow_html=True)
            assessment = P.assess_invoice_confidence(text, invoice)
            slot.markdown(stepper(f.name, 4), unsafe_allow_html=True)
            records[f.name] = {"status": "review", "invoice": invoice, "assessment": assessment}
        except Exception as e:  # keep the batch going
            records[f.name] = {"status": "failed", "error": str(e)}
        bar.progress(n / len(files))
    st.session_state.goto = "Review"
    st.rerun()


def accept(name, invoice):
    stem = Path(name).stem
    P.export_json(invoice, stem)
    P.export_csv(invoice, stem)
    records[name].update(final=invoice, status="accepted")
    st.toast(f"{name} accepted and saved", icon="✅")


def accepted_rows():
    out = []
    for name, r in records.items():
        if r["status"] == "accepted":
            d = r["final"].model_dump(by_alias=True, mode="json")
            d["Source File"] = name
            out.append(d)
    return out


# ───────────────────────── Sidebar ─────────────────────────
with st.sidebar:
    st.markdown("### 🧾 Invoice Extractor")
    st.caption("PDF → structured data, with a human check on anything uncertain.")
    threshold = st.slider("Review threshold", 0.50, 0.95, 0.80, 0.05,
                          help="Fields scoring below this are flagged for manual review.")
    if st.button("Clear session", use_container_width=True):
        records.clear()
        st.session_state.goto = "Upload"
        st.rerun()

# ───────────────────────── Hero + theme toggle ─────────────────────────
top, tog = st.columns([6, 1.2])
tog.toggle("🌙 Dark mode", key="dark")

md("""<div class="hero"><div><h1>Turn invoice PDFs into verified data</h1>
<p>Upload your invoices, check only the fields the model is unsure about, then export clean JSON and CSV.</p></div>
<div class="stage"><div class="doc"><i></i><i></i><i></i><i></i><i></i><b></b></div>
<span class="chip a">98% ✓</span><span class="chip b">62% check</span></div></div>""")

if records:
    kpi_strip()

view = st.segmented_control("Step", ["Upload", "Review", "Export"], key="view", label_visibility="collapsed")

# ───────────────────────── Upload ─────────────────────────
if view == "Upload":
    files = st.file_uploader("Invoice PDFs", type="pdf", accept_multiple_files=True,
                             help="You can add several invoices at once.")
    if files and st.button(f"Extract {len(files)} invoice{'s' if len(files) > 1 else ''}", type="primary"):
        run_extraction(files)
    if not files:
        empty("📄", "No invoices yet", "Drop one or more PDF files above to begin.")

# ───────────────────────── Review ─────────────────────────
elif view == "Review":
    if not records:
        empty("🔍", "Nothing to review", "Upload invoices first, then come back here.")
    else:
        name = st.selectbox("Invoice", list(records), format_func=lambda n: f"{n}  ·  {STATUS[records[n]['status']][0]}")
        rec = records[name]
        label, tone = STATUS[rec["status"]]
        if rec["status"] == "failed":
            md(f'<div class="head"><h3>{esc(name)}</h3><span class="pill bad">Failed</span></div>')
            st.error(f"Extraction failed: {rec['error']}. Fix the cause and upload the file again.")
        else:
            invoice = rec.get("final", rec["invoice"])
            inv_dict = invoice.model_dump(by_alias=True, mode="json")
            flagged = P.identify_fields_for_review(rec["assessment"])
            flagged = [f for f in flagged if rec["assessment"].fields[f].confidence < threshold]
            note = f'{len(flagged)} field{"s" if len(flagged) != 1 else ""} to check' if flagged else "All fields look reliable"
            md(f'<div class="head"><h3>{esc(name)}</h3><span class="pill {tone}">{label}</span>'
               f'<span class="pill {"bad" if flagged else "ok"}">{note}</span></div>')
            ledger(inv_dict, rec["assessment"], threshold)

            if rec["status"] == "review":
                a, b, _ = st.columns([1.3, 1, 3])
                if a.button("Accept and save", type="primary", key=f"acc_{name}"):
                    accept(name, invoice)
                    st.rerun()
                if b.button("Reject", key=f"rej_{name}"):
                    rec["status"] = "rejected"
                    st.toast(f"{name} rejected", icon="🚫")
                    st.rerun()
                with st.expander("Correct values before saving"):
                    with st.form(f"edit_{name}"):
                        cols, edited = st.columns(2), {}
                        for i, (k, v) in enumerate(inv_dict.items()):
                            edited[k] = cols[i % 2].text_input(k, "" if v is None else str(v))
                        if st.form_submit_button("Save corrections", type="primary"):
                            updated = {k: (e.strip() or None) for k, e in edited.items()}
                            try:
                                accept(name, InvoiceData.model_validate(updated))
                                st.rerun()
                            except ValidationError as e:
                                st.error(f"Some values are not valid:\n\n{e}")
            else:
                if st.button("Reopen for review", key=f"re_{name}"):
                    rec["status"] = "review"
                    st.rerun()

# ───────────────────────── Export ─────────────────────────
else:
    rows = accepted_rows()
    if not rows:
        empty("📦", "No accepted invoices", "Accept at least one invoice in Review to export it.")
    else:
        df = pd.DataFrame(rows)
        # Themed HTML table (st.dataframe ignores custom CSS variables)
        md(f'<div class="tbl-wrap">{df.fillna("").to_html(index=False, border=0, escape=True)}</div>')
        a, b, c, _ = st.columns([1.2, 1.2, 1.5, 2])
        a.download_button("Download CSV", df.to_csv(index=False).encode(), "all_invoices.csv", "text/csv", type="primary")
        b.download_button("Download JSON", json.dumps(rows, indent=2).encode(), "all_invoices.json", "application/json")
        if c.button("Save to outputs folder"):
            P.export_consolidated_csv(rows)
            st.toast("Saved outputs/all_invoices.csv", icon="💾")