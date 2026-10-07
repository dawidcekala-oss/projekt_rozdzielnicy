# scala wyniki agentów (journal.jsonl obu workflow) do bom/linki.json – nowsze (v2) nadpisują starsze
import json, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = "/root/.claude/projects/-home-user-projekt-rozdzielnicy/0f6dff11-d416-525a-adfd-12a52c2e6931/subagents/workflows"
runs = ["wf_a53563b7-67b", "wf_95156fbe-30e"]  # kolejność: v1 potem v2 (v2 nadpisuje)
out = {}
for run in runs:
    p = os.path.join(base, run, "journal.jsonl")
    if not os.path.exists(p): continue
    for line in open(p, encoding="utf-8"):
        try: j = json.loads(line)
        except Exception: continue
        if j.get("type") != "result": continue
        r = j.get("result")
        if not isinstance(r, dict): continue
        groups = [r] if "oferty" in r else r.get("grupy", [])
        for g in groups:
            for o in g.get("oferty", []):
                try: out[int(o["id"])] = o
                except Exception: pass
json.dump({str(k): v for k, v in sorted(out.items())}, open(os.path.join(ROOT, "bom", "linki.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("linki:", len(out), "ids:", sorted(out))
