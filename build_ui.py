#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, json, urllib.request, os

SRC = "https://llmperks.com/llms-full.txt"
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "index.html")
TPL = os.path.join(BASE, "template.html")

def fetch():
    with urllib.request.urlopen(SRC, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")

def parse(text):
    models = []
    cur = None
    for line in text.splitlines():
        if line.startswith("## "):
            if cur:
                models.append(cur)
            cur = {"name": line[3:].strip(), "dev": "", "type": "", "aa": "", "params": "", "endpoints": []}
        elif cur is None:
            continue
        elif line.startswith("Developer:"):
            cur["dev"] = line.split(":",1)[1].strip()
        elif line.startswith("Type:"):
            cur["type"] = line.split(":",1)[1].strip()
        elif line.startswith("Parameters:"):
            cur["params"] = line.split(":",1)[1].strip()
        elif line.startswith("AA Intelligence Index:"):
            cur["aa"] = line.split(":",1)[1].strip()
        elif line.startswith("- ") and ":" in line:
            m = re.match(r"^- (\w+): id=(.*?); context=(.*?); url=(.*)$", line)
            if m:
                prov, mid, ctx, url = m.groups()
                cur["endpoints"].append({"provider": prov, "id": mid.strip(), "context": ctx.strip(), "url": url.strip()})
    if cur:
        models.append(cur)
    return models

def main():
    text = fetch()
    models = parse(text)
    data = json.dumps(models, ensure_ascii=False)
    with open(TPL, encoding="utf-8") as f:
        tpl = f.read()
    html = tpl.replace("__DATA__", data)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrote", OUT, "models:", len(models))

if __name__ == "__main__":
    main()
