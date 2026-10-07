# scala wyniki agentów (journal.jsonl kolejnych workflow) do bom/linki.json.
# Starsze przebiegi (v1, v2) używały innej numeracji pozycji niż bom v3 – mapa REMAP tłumaczy stare id na nowe,
# a pozycje bez odpowiednika są pomijane. Najnowszy przebieg (v3) używa id wprost i nadpisuje starsze.
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = "/root/.claude/projects/-home-user-projekt-rozdzielnicy/0f6dff11-d416-525a-adfd-12a52c2e6931/subagents/workflows"
REMAP_OLD = {2: 2, 51: 4, 52: 7, 53: 3, 54: 9, 11: 10, 12: 11, 23: 18, 28: 23, 31: 31, 32: 32, 33: 33, 34: 34, 35: 35,
             56: 56, 57: 57, 58: 58, 59: 59, 60: 60, 5: 6, 4: 5}
runs = [("wf_a53563b7-67b", REMAP_OLD), ("wf_95156fbe-30e", REMAP_OLD), ("wf_67dcdc1a-b13", None)]
out = {}
for run, remap in runs:
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
                try: i = int(o["id"])
                except Exception: continue
                if remap is not None:
                    if i not in remap: continue
                    i = remap[i]
                out[i] = o
json.dump({str(k): v for k, v in sorted(out.items())}, open(os.path.join(ROOT, "bom", "linki.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("linki:", len(out), "ids:", sorted(out))
