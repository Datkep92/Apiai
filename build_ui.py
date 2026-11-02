#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, json, urllib.request, os

SRC_FULL = "https://llmperks.com/llms-full.txt"
SRC_SHORT = "https://llmperks.com/llms.txt"
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "index.html")
TPL = os.path.join(BASE, "template.html")

ALIASES = {
    "openrouter": "openrouter",
    "groq": "groq",
    "google ai studio": "gemini",
    "mistral ai": "mistral",
    "together ai": "together",
    "cohere": "cohere",
    "cerebras": "cerebras",
    "cloudflare workers ai": "cloudflare",
    "hugging face": "huggingface",
    "orcarouter": "orcarouter",
    "nvidia build": "nvidia",
    "tokenrouter": "tokenrouter",
    "vercel ai gateway": "vercel",
    "nous portal": "nous",
    "unorouter": "unorouter",
    "opencode zen": "opencode",
}

def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")

def parse_providers(text):
    providers = []
    for line in text.splitlines():
        if line.startswith("- [") and "Base URL:" in line:
            m = re.match(r"^- \[([^\]]+)\]\(([^)]+)\): .*Base URL: (https?://\S+)", line)
            if m:
                label, url, base = m.groups()
                key = ALIASES.get(label.strip().lower(), label.strip().lower().replace(" ", ""))
                providers.append({"name": key, "label": label.strip(), "url": url.strip(), "base": base.strip().rstrip(".")})
    return providers

def parse_models(text):
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
    full = fetch(SRC_FULL)
    short = fetch(SRC_SHORT)
    providers = parse_providers(short)
    models = parse_models(full)
    data = json.dumps({"providers": providers, "models": models}, ensure_ascii=False)
    with open(TPL, encoding="utf-8") as f:
        tpl = f.read()
    html = tpl.replace("__DATA__", data)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrote", OUT, "models:", len(models), "providers:", len(providers))

if __name__ == "__main__":
    main()
