import os, argparse
from jinja2 import Environment, FileSystemLoader
from docx import Document

env = Environment(loader=FileSystemLoader("docgen/templates"))

def render_docx(template_name, context, out_path):
    tpl = env.get_template(template_name)
    content = tpl.render(**context)
    doc = Document()
    for line in content.splitlines():
        doc.add_paragraph(line)
    doc.save(out_path)

def load_glossary():
    path = "docgen/glossary.yaml"
    if not os.path.exists(path):
        return {}
    import yaml
    with open(path,"r",encoding="utf-8") as f:
        import yaml as y
        return y.safe_load(f) or {}

def default_context():
    g = load_glossary()
    return {
        "company": g.get("company","ACME Pharma"),
        "system_name": g.get("system_name","GxP Doc Assistant"),
        "scope": g.get("scope","GxP documentation support tool"),
        "reg_refs": g.get("reg_refs", ["EU GMP Annex 11", "21 CFR Part 11", "GAMP 5"]),
        "roles": g.get("roles", ["QA","CSV","IT","Business Owner"]),
        "version": g.get("version", "0.1"),
        "title": g.get("title", None)
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="source", default="pr")
    ap.add_argument("--out", dest="out", default="docs/")
    args = ap.parse_args()

    ctx = default_context()
    os.makedirs(args.out, exist_ok=True)

    docs = [
        ("URS_template.docx.j2",  "URS.docx"),
        ("FS_template.docx.j2",   "FS.docx"),
        ("DS_template.docx.j2",   "DS.docx"),
        ("SOP_template.docx.j2",  "SOP_GxP_Doc_Generation.docx"),
        ("IQ_template.docx.j2",   "IQ_Protocol.docx"),
        ("OQ_template.docx.j2",   "OQ_Protocol.docx"),
        ("PQ_template.docx.j2",   "PQ_Protocol.docx"),
    ]

    for tpl, out in docs:
        render_docx(tpl, ctx, os.path.join(args.out, out))

    print(f"Generated {len(docs)} documents in {args.out}")
