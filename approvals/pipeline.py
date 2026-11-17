"""Ingestion pipeline, generated from ../ingestion/ingestion_book.ipynb by build_approvals.py.
Do not edit by hand: change the ingestion notebook's build script and regenerate."""
# Setup
import os, re, json, html, difflib, hashlib
from pathlib import Path
import numpy as np
import chromadb
from IPython.display import display, HTML

DATA_DIR = next((d for d in [Path("."), Path(__file__).resolve().parent.parent / "ingestion", Path("../ingestion")]
                 if (d / "knowledge_ontology_v1.json").exists()), Path("."))
DOC_1 = DATA_DIR / "RX-EDU-SCRIPT_v3.2.md"
DOC_2 = DATA_DIR / "PHARM-OUTREACH-SCRIPT_v1.7.md"
ONTOLOGY = json.loads((DATA_DIR / "knowledge_ontology_v1.json").read_text())

USE_LLM = bool(os.getenv("ANTHROPIC_API_KEY"))
UPLOADER = "Maya Ortiz, Knowledge Ops author"   # who uploads (supplied at upload, not read from the doc)
LLM_MODEL = "claude-sonnet-5-5"

# Similarity needed before two units are compared at all (cosine, 0-1).
VERBATIM_MATCH = 0.55
GUIDANCE_MATCH = 0.50


# 1. Split a document into knowledge units
VERBATIM_MARK = re.compile(r"^\*\*\[VERBATIM\s*[–-]\s*LEGAL\]\*\*\s*$")
SKIP_SECTIONS = {"revision history"}

def clean(s):
    s = re.sub(r"\*+", "", s)
    return re.sub(r"[ \t]+", " ", s).strip()

def parse_document(path):
    text = path.read_text()
    head = text.split("\n## ")[0]
    meta = {}
    for k, v in re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", head, re.M):
        if k != "Field" and not set(k) <= set("-: "):
            meta[k] = v
    meta["Title"] = re.search(r"^# (.+)$", text, re.M).group(1)
    meta["_raw"] = text
    lob = sorted(set(re.findall(r"\b(MAPD|PDP|DSNP)\b", text)))
    units = []
    for sec in re.split(r"^## ", text, flags=re.M)[1:]:
        heading, _, body = sec.partition("\n")
        num, sec_title = re.match(r"(\d+)\.\s*(.+)", heading.strip()).groups()
        if sec_title.lower() in SKIP_SECTIONS:
            continue
        lines = [l for l in body.split("\n") if l.strip() != "---"]
        verbatims, guidance, i = [], [], 0
        while i < len(lines):
            if VERBATIM_MARK.match(lines[i].strip()):
                i, block = i + 1, []
                while i < len(lines) and lines[i].strip():
                    block.append(lines[i].strip()); i += 1
                verbatims.append(clean(" ".join(block)))
            else:
                guidance.append(lines[i]); i += 1
        for k, v in enumerate(verbatims, 1):
            units.append(dict(section=f"§{num}", title=sec_title, text=v, is_verbatim=True, uid=f"{meta['Document ID']}§{num}.V{k}"))
        g = clean("\n".join(guidance))
        if g:
            units.append(dict(section=f"§{num}", title=sec_title, text=g, is_verbatim=False, uid=f"{meta['Document ID']}§{num}.G"))
    for u in units:
        u.update(doc_id=meta["Document ID"], doc_version=meta["Version"], plan_year=meta.get("Plan year", ""),
                 lob=", ".join(lob), approval_id=meta.get("Legal approval", "").split(" ")[0])
    return meta, units

# 2. Tag each unit against the ontology
TOPIC_KW = ONTOLOGY["classes"]["Topic"]["keywords"]
KB_FOR = {"pharmacy": "pharmacy", "insurance": "insurance", "member_service": "shared_member_service"}

def kw_count(kw, s):
    return len(re.findall(r"\b" + re.escape(kw), s))

def rule_tags(u, meta):
    t, b = u["title"].lower(), u["text"].lower()
    scores = {tp: sum(5 * kw_count(k, t) + kw_count(k, b) for k in kws) for tp, kws in TOPIC_KW.items()}
    topic = max(scores, key=scores.get) if max(scores.values()) else "member_service.call_handling"
    if u["is_verbatim"]:
        utype = "verbatim_legal"
    elif re.search(r"\$\d|\d+% coinsurance", u["text"]):
        utype = "benefit_fact"
    elif "coverage rules" in t:
        utype = "policy_rule"
    elif any(w in t for w in ("purpose", "escalation", "disposition", "premium", "do-not-call")):
        utype = "procedure"
    else:
        utype = "script_step"
    return dict(unit_type=utype, topic=topic)

def llm_json(prompt):
    import anthropic
    msg = anthropic.Anthropic().messages.create(model=LLM_MODEL, max_tokens=6000,
                                                messages=[{"role": "user", "content": prompt}])
    txt = msg.content[0].text
    return json.loads(re.search(r"[\[{].*[\]}]", txt, re.S).group(0))

def llm_tags(units):
    allowed = {"unit_type": list(ONTOLOGY["classes"]["UnitType"]["values"]), "topic": list(TOPIC_KW)}
    payload = [{"uid": u["uid"], "title": u["title"], "text": u["text"][:1500]} for u in units]
    prompt = (f"Tag each knowledge unit using ONLY these values: {json.dumps(allowed)}. "
              f"Return a JSON list of objects with keys uid, unit_type, topic.\n\n{json.dumps(payload)}")
    out = {r["uid"]: r for r in llm_json(prompt)}
    return out, allowed

def tag_units(units, meta):
    llm = {}
    if USE_LLM:
        try:
            llm, allowed = llm_tags(units)
        except Exception as e:
            print(f"Claude tagging failed, using rules instead: {e}")
    channel = "outbound" if "outbound" in meta.get("Audience", "").lower() else "advocate_desktop"
    for u in units:
        tags = rule_tags(u, meta)
        r = llm.get(u["uid"], {})
        if r.get("topic") in TOPIC_KW: tags["topic"] = r["topic"]
        if r.get("unit_type") in ONTOLOGY["classes"]["UnitType"]["values"]: tags["unit_type"] = r["unit_type"]
        if u["is_verbatim"]:                       # policy beats model: marked verbatim is always legal verbatim
            tags["unit_type"] = "verbatim_legal"
        ut = tags["unit_type"]
        tags["compliance_class"] = ("legal" if ut == "verbatim_legal" else
                                    "regulatory_cms" if ut in ("benefit_fact", "policy_rule") or tags["topic"] == "pharmacy.drug_payment_stages" else
                                    "operational")
        tags["kb"] = KB_FOR[tags["topic"].split(".")[0]]
        tags["channel"] = channel
        tags["approval_gate"] = ONTOLOGY["approval_policy"][tags["compliance_class"]]
        u.update(tags)
    return units

# 3. Knowledge store (Chroma) and display helpers

class WordingEmbedding:
    """Character 3-5-gram hashing embedding. It is sensitive to exact wording, which is what
    near-duplicate legal text needs, and needs no model download. Semantic embeddings
    belong to the search phase, not to dedup at ingestion."""
    def __init__(self, dim=4096):
        self.dim = dim
    def __call__(self, texts):
        out = []
        for doc in texts:
            v = np.zeros(self.dim)
            s = " " + re.sub(r"\s+", " ", doc.lower()) + " "
            for n in (3, 4, 5):
                for i in range(len(s) - n + 1):
                    v[int(hashlib.md5(s[i:i+n].encode()).hexdigest()[:8], 16) % self.dim] += 1
            out.append((v / (np.linalg.norm(v) or 1)).tolist())
        return out

embed = WordingEmbedding()
client = chromadb.EphemeralClient()
try:
    client.delete_collection("knowledge_units")
except Exception:
    pass
store = client.create_collection("knowledge_units", metadata={"hnsw:space": "cosine"}, embedding_function=None)

def publish(units, approver, approval_id):
    store.add(ids=[u["uid"] for u in units], embeddings=embed([u["text"] for u in units]), documents=[u["text"] for u in units],
              metadatas=[{k: u[k] for k in ("doc_id", "doc_version", "section", "title", "unit_type", "topic", "kb",
                                             "compliance_class", "plan_year", "channel", "is_verbatim")}
                         | {"status": "published", "approved_by": approver, "approval_id": approval_id} for u in units])

# --- display helpers ---
PILL = {"verbatim_legal": "#b25e09", "legal": "#b25e09", "regulatory_cms": "#7a4fa3", "operational": "#5c6661",
        "benefit_fact": "#2f6b4f", "policy_rule": "#2f6b4f", "script_step": "#3c6e91", "procedure": "#3c6e91", "definition": "#3c6e91"}
CSS = """<style>
.kt{border-collapse:collapse;font:13px/1.45 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;width:100%}
.kt th{text-align:left;font-weight:600;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:#5c6661;border-bottom:2px solid #c9cfcb;padding:6px 8px}
.kt td{border-bottom:1px solid #e3e6e4;padding:6px 8px;vertical-align:top}
.pill{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11.5px;color:#fff;white-space:nowrap}
.mono{font-family:ui-monospace,Menlo,monospace;font-size:12px}
.card{border:1px solid #c9cfcb;border-radius:8px;padding:12px 14px;margin:10px 0;font:13px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif}
.card h4{margin:0 0 6px;font-size:14px}
del{background:#fde2e1;color:#9b1c1c;text-decoration:line-through}
ins{background:#dcf2e3;color:#14532d;text-decoration:none}
</style>"""

def pill(text, color=None):
    return f'<span class="pill" style="background:{color or PILL.get(text, "#5c6661")}">{html.escape(text)}</span>'

from datetime import datetime

DOC_TYPES = {"script": "Call script", "article": "Knowledge article", "benefit": "Benefit document", "policy": "Policy"}

def doc_category(meta):
    kind = next((v for k, v in DOC_TYPES.items() if k in meta["Title"].lower()), "Document")
    direction = "outbound" if "outbound" in meta.get("Audience", "").lower() else "inbound"
    return f"{kind} · {direction} · {meta.get('Knowledge base', '')}"

def humanize(topic):
    return topic.split(".")[1].replace("_", " ")

def summarize(meta, units):
    """Two-sentence summary. Claude writes it when available; otherwise built from metadata and tags."""
    if USE_LLM:
        try:
            r = llm_json("Summarize this document for a knowledge author in exactly two short sentences: what it is "
                         "and who uses it, then what it covers and anything compliance-sensitive. "
                         'Return JSON {"summary": "..."}.\n\n' + meta["_raw"][:12000])
            return r["summary"]
        except Exception as e:
            print(f"Claude summary failed, using template: {e}")
    topics = {}
    for u in units:
        topics[u["topic"]] = topics.get(u["topic"], 0) + 1
    top = [humanize(t) for t, _ in sorted(topics.items(), key=lambda kv: -kv[1])[:4]]
    nv = sum(u["is_verbatim"] for u in units)
    lob = units[0]["lob"] if units else ""
    return (f"{doc_category(meta).split(' · ')[0]} for {meta.get('Audience', 'advocates').lower()} on {lob} plans, "
            f"plan year {meta.get('Plan year', '?')}, owned by {meta.get('Owner', '?')}. "
            f"Covers {len(topics)} topics (mainly {', '.join(top)}) in {len(units)} units, "
            f"{nv} of them legal verbatim lines that must be read word for word.")

def show_doc_header(meta, units, uploader=UPLOADER):
    uploaded = datetime.now().strftime("%Y-%m-%d %H:%M")
    field = lambda label, value, src: (f'<div><div style="font-size:11px;color:#5c6661;text-transform:uppercase;letter-spacing:.05em">'
                                       f'{label} <span style="text-transform:none;letter-spacing:0">· {src}</span></div>'
                                       f'<div style="font-weight:600">{html.escape(value)}</div></div>')
    grid = "".join([
        field("Author", meta.get("Author", "not stated"), "from doc"),
        field("Source / owner", meta.get("Owner", "not stated"), "from doc"),
        field("Uploaded by", uploader, "at upload"),
        field("Uploaded at", uploaded, "at upload"),
        field("Version", f"v{meta.get('Version', '?')} · effective {meta.get('Effective date', '?')}", "from doc"),
        field("Category", doc_category(meta), "inferred"),
        field("Plan year", meta.get("Plan year", "?"), "from doc"),
        field("Legal approval", meta.get("Legal approval", "none"), "from doc"),
    ])
    display(HTML(CSS + f"""
    <div class="card" style="border-left:5px solid #2f6b4f">
      <div class="mono" style="color:#5c6661">{html.escape(meta['Document ID'])}</div>
      <h3 style="margin:2px 0 10px;font-size:17px">{html.escape(meta['Title'])}</h3>
      <div style="display:grid;grid-template-columns:repeat(4,minmax(150px,1fr));gap:10px 18px">{grid}</div>
      <div style="margin-top:12px;padding:10px 12px;background:#f6f7f5;border-radius:6px">
        <div style="font-size:11px;color:#5c6661;text-transform:uppercase;letter-spacing:.05em;margin-bottom:2px">Summary · {"Claude" if USE_LLM else "generated from tags"}</div>
        {html.escape(summarize(meta, units))}
      </div>
    </div>"""))

def show_units(units):
    head = "<tr><th>Unit</th><th>Section</th><th>Type</th><th>Compliance</th><th>Topic</th><th>KB</th><th>Channel</th><th>LOB</th><th>Plan yr</th><th>Approval gate</th><th>Text (start)</th></tr>"
    rows = ""
    for u in units:
        rows += (f'<tr><td class="mono">{u["uid"]}</td><td>{u["section"]} {html.escape(u["title"])}</td><td>{pill(u["unit_type"])}</td>'
                 f'<td>{pill(u["compliance_class"])}</td><td class="mono">{u["topic"]}</td><td>{u["kb"]}</td><td>{u["channel"]}</td>'
                 f'<td>{u["lob"]}</td><td>{u["plan_year"]}</td><td>{u["approval_gate"]}</td>'
                 f'<td>{html.escape(u["text"][:90])}{"…" if len(u["text"]) > 90 else ""}</td></tr>')
    display(HTML(CSS + f'<table class="kt">{head}{rows}</table>'))

def word_diff(old, new):
    a, b = old.split(), new.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if op == "equal":
            out.append(html.escape(" ".join(a[i1:i2])))
        if op in ("delete", "replace"):
            out.append(f"<del>{html.escape(' '.join(a[i1:i2]))}</del>")
        if op in ("insert", "replace"):
            out.append(f"<ins>{html.escape(' '.join(b[j1:j2]))}</ins>")
    return " ".join(out)


CHANNEL_SPECIFIC = set(ONTOLOGY["classes"]["Topic"].get("channel_specific", []))
RETIRED = [l["term"] for l in ONTOLOGY["lexicon"] if "Retired" in l.get("note", "")] + ["coverage gap"]
ACTION = {
    "EXACT_DUPLICATE":      ("#5c6661", "Link to existing unit. No new unit created.", "AI"),
    "LEGAL_WORDING_DIFFERS": ("#b25e09", "Route to Legal with diff. Approved wording stays live until Legal decides.", "Legal (human only)"),
    "SAME_MEANING":         ("#3c6e91", "Propose merge into the existing unit.", "Author confirms"),
    "VARIANT":              ("#2f6b4f", "Keep both, scoped by plan year / channel.", "Author confirms"),
    "CONTRADICTION":        ("#b42318", "Block publish. Conflict of authority.", "Content owner / Legal (human only)"),
    "STALE":                ("#7a4fa3", "Retired concept. Propose update to the approved wording.", "Author drafts, Legal approves"),
    "NEW_UNIT":             ("#1d2320", "Send to approval gate.", "Approver for its compliance class"),
}

def numbers(text):
    t = re.sub(r"(?m)^\s*\d+\.\s", "", text)                 # list markers
    t = re.sub(r"(?i)\b(section|tier|§)\s*\d+", "", t)         # references and labels, not facts
    return set(re.findall(r"\$[\d,]+|\d+%|\d+(?:-day)?", t))

def nearest(u):
    if store.count() == 0:
        return None, 0.0
    # Legal verbatim is only compared within the same topic; guidance is compared across topics.
    where = ({"$and": [{"is_verbatim": True}, {"topic": u["topic"]}]} if u["is_verbatim"] else {"is_verbatim": False})
    r = store.query(query_embeddings=embed([u["text"]]), n_results=1, where=where)
    if not r["ids"][0]:
        return None, 0.0
    m = dict(r["metadatas"][0][0], uid=r["ids"][0][0], text=r["documents"][0][0])
    return m, 1 - r["distances"][0][0]

def rule_judgement(u, m):
    retired = [t for t in RETIRED if t in u["text"].lower()]
    if retired and m["plan_year"] > u["plan_year"]:
        return "STALE", f"Mentions retired concept ({', '.join(retired)}); approved unit is plan year {m['plan_year']}."
    a, b = numbers(m["text"]), numbers(u["text"])
    if (a - b) and (b - a):                         # both sides state figures, and they disagree
        if u["unit_type"] == "benefit_fact" and m["plan_year"] != u["plan_year"]:
            return "VARIANT", f"Figures differ ({', '.join(sorted(a ^ b))}) but plan years differ ({u['plan_year']} vs {m['plan_year']})."
        return "CONTRADICTION", f"Same subject, different facts: {', '.join(sorted(a - b))} (approved) vs {', '.join(sorted(b - a))} (new)."
    if u["topic"] in CHANNEL_SPECIFIC and u["channel"] != m.get("channel", u["channel"]):
        return "VARIANT", f"Channel-specific content ({u['channel']} vs {m['channel']}); both can stand."
    return "SAME_MEANING", "Same subject, no conflicting figures, different wording."

def llm_judgement(u, m):
    prompt = ("You compare a NEW knowledge unit with an APPROVED one on the same subject. Classify as one of "
              "SAME_MEANING, VARIANT (both valid in different scopes, e.g. plan year or channel), CONTRADICTION "
              "(incompatible facts or rules), STALE (new unit describes something the approved unit says is retired), NEW_UNIT "
              "(different subject). Return JSON {\"category\":..., \"reason\": one sentence}.\n\n"
              f"APPROVED (plan year {m['plan_year']}): {m['text'][:2000]}\n\nNEW (plan year {u['plan_year']}): {u['text'][:2000]}")
    r = llm_json(prompt)
    return (r["category"], r["reason"]) if r.get("category") in ACTION else rule_judgement(u, m)

def judge(u):
    m, sim = nearest(u)
    threshold = VERBATIM_MATCH if u["is_verbatim"] else GUIDANCE_MATCH
    if m is None or sim < threshold:
        return dict(unit=u, match=m, sim=sim, category="NEW_UNIT", reason="No published unit is close enough.")
    if " ".join(u["text"].lower().split()) == " ".join(m["text"].lower().split()):
        return dict(unit=u, match=m, sim=sim, category="EXACT_DUPLICATE", reason="Identical wording.")
    if u["is_verbatim"]:                            # deterministic: any change to legal verbatim goes to Legal
        newer = m["plan_year"] > u["plan_year"]
        return dict(unit=u, match=m, sim=sim, category="LEGAL_WORDING_DIFFERS",
                    reason=f"Legal verbatim differs from approved {m['uid']} ({m['approval_id']})."
                           + (" The approved version is newer, so the new wording is drift." if newer else ""))
    cat, reason = rule_judgement(u, m)
    if USE_LLM:
        try:
            cat, reason = llm_judgement(u, m)
        except Exception as e:
            reason += f" (Claude unavailable: {e})"
    return dict(unit=u, match=m, sim=sim, category=cat, reason=reason)




def run_ingestion():
    """Doc 1 becomes the approved baseline in Chroma; doc 2 is split, tagged and judged against it."""
    meta1, units1 = parse_document(DOC_1)
    units1 = tag_units(units1, meta1)
    publish(units1, approver="Legal (simulated)", approval_id=meta1["Legal approval"].split(" ")[0])
    meta2, units2 = parse_document(DOC_2)
    units2 = tag_units(units2, meta2)
    findings = [judge(u) for u in units2]
    return dict(meta1=meta1, units1=units1, meta2=meta2, units2=units2, findings=findings)
