# Test pamieci modulu (dokument 04): migawka wszystkiego, co modul trzyma, i porownanie dwoch migawek.
#   python migawka.py zrob <etykieta>            -> logi/pamiec/migawka_<etykieta>_<czas>.json
#   python migawka.py porownaj <przed.json> <po.json>   -> tabela: co przetrwalo, co nie
# Tylko odczyt (polecenia Get/List). Konfiguracja z modulu nie zawiera hasla Wi-Fi.
import datetime
import json
import os
import sys
import urllib.request

HOST = "http://192.168.0.238/rpc"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logi", "pamiec")


def rpc(method, params=None):
    body = json.dumps({"id": 1, "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(HOST, data=body, method="POST")
    try:
        r = json.load(urllib.request.urlopen(req, timeout=10))
    except Exception as e:  # noqa: BLE001
        return {"_blad": str(e)}
    return r.get("result", {"_blad": r.get("error")})


def components():
    out, off = {}, 0
    while True:
        r = rpc("Shelly.GetComponents", {"dynamic_only": True, "offset": off})
        items = r.get("components", [])
        for c in items:
            out[c["key"]] = {"config": c.get("config"), "status": c.get("status"), "attrs": c.get("attrs")}
        off += len(items)
        if not items or off >= r.get("total", 0):
            return out


def zrob(label):
    snap = {
        "etykieta": label,
        "czas_laptopa": datetime.datetime.now().isoformat(timespec="seconds"),
        "urzadzenie": rpc("Shelly.GetDeviceInfo"),
        "konfiguracja": rpc("Shelly.GetConfig"),
        "sys": rpc("Sys.GetStatus"),
        "kvs": rpc("KVS.GetMany"),
        "harmonogram": rpc("Schedule.List"),
        "webhooki": rpc("Webhook.List"),
        "usluga_info": rpc("Service.GetInfo", {"id": 0}),
        "usluga_stan": rpc("Service.GetStatus", {"id": 0}),
        "pola": components(),
        "polaczenia": {k: rpc(k + ".GetStatus") for k in ("Cloud", "MQTT", "WS")},
    }
    os.makedirs(OUT, exist_ok=True)
    name = "migawka_%s_%s.json" % (label, datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    path = os.path.normpath(os.path.join(OUT, name))
    json.dump(snap, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    s = snap["sys"]
    print("zapisano", path)
    print("  czas pracy %s s, godzina %s, synchronizacja czasu %s, usluga %s, pol %d, KVS %d, zadan %d, webhookow %d" % (
        s.get("uptime"), s.get("time"), s.get("last_sync_ts"), snap["usluga_info"].get("ver"),
        len(snap["pola"]), len(snap["kvs"].get("items", {})), len(snap["harmonogram"].get("jobs", [])),
        len(snap["webhooki"].get("hooks", []))))
    return path


# Czego oczekujemy po zaniku zasilania. Klucz pola -> czy wartosc ma przetrwac.
PERSISTED_VALUES = {"boolean:200", "number:200"}


def porownaj(p1, p2):
    a = json.load(open(p1, encoding="utf-8"))
    b = json.load(open(p2, encoding="utf-8"))
    rows = []

    def row(co, oczek, ok, szczegol=""):
        rows.append((co, oczek, ok, szczegol))

    def same(x, y):
        return json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True)

    ca, cb = a["konfiguracja"], b["konfiguracja"]
    for sekcja in sorted(set(ca) | set(cb)):
        row("konfiguracja: " + sekcja, "zostaje", same(ca.get(sekcja), cb.get(sekcja)))
    row("pamiec klucz-wartosc", "zostaje", same(a["kvs"].get("items"), b["kvs"].get("items")),
        "%d -> %d kluczy" % (len(a["kvs"].get("items", {})), len(b["kvs"].get("items", {}))))
    row("harmonogram", "zostaje", same(a["harmonogram"].get("jobs"), b["harmonogram"].get("jobs")),
        "%d -> %d zadan" % (len(a["harmonogram"].get("jobs", [])), len(b["harmonogram"].get("jobs", []))))
    row("webhooki", "zostaja", same(a["webhooki"].get("hooks"), b["webhooki"].get("hooks")),
        "%d -> %d" % (len(a["webhooki"].get("hooks", [])), len(b["webhooki"].get("hooks", []))))
    ia, ib = a["usluga_info"], b["usluga_info"]
    row("usluga: wersja i kompilacja", "zostaje", (ia.get("ver"), ia.get("build_id")) == (ib.get("ver"), ib.get("build_id")),
        "%s -> %s" % (ia.get("ver"), ib.get("ver")))
    row("usluga: pliki (sha256)", "zostaja", same(a["usluga_stan"].get("files"), b["usluga_stan"].get("files")))
    row("usluga: dziala", "dziala", b["usluga_stan"].get("state") == "running",
        "stan %s, komunikaty %s" % (b["usluga_stan"].get("state"), b["usluga_stan"].get("errors")))
    da, db = a["urzadzenie"], b["urzadzenie"]
    row("urzadzenie: id, firmware, token produktu", "zostaje",
        all(da.get(k) == db.get(k) for k in ("id", "fw_id", "ver", "jti")), "jti %s -> %s" % (da.get("jti"), db.get("jti")))
    pa, pb = a["pola"], b["pola"]
    row("definicje pol", "zostaja", same({k: v["config"] for k, v in pa.items()}, {k: v["config"] for k, v in pb.items()}),
        "%d -> %d pol" % (len(pa), len(pb)))
    for k in sorted(pa):
        va = (pa[k].get("status") or {}).get("value")
        vb = (pb.get(k, {}).get("status") or {}).get("value")
        if isinstance(va, dict) or isinstance(vb, dict):
            continue
        if k in PERSISTED_VALUES:
            row("wartosc %s (%s), zapamietywana" % (k, pa[k]["attrs"].get("role")), "zostaje", va == vb, "%s -> %s" % (va, vb))
        else:
            row("wartosc %s (%s)" % (k, pa[k]["attrs"].get("role")), "od sterownika albo domyslna", None, "%s -> %s" % (va, vb))
    sa, sb = a["sys"], b["sys"]
    row("czas pracy", "od zera", (sb.get("uptime") or 0) < (sa.get("uptime") or 0), "%s -> %s s" % (sa.get("uptime"), sb.get("uptime")))
    row("godzina", "z serwera czasu", bool(sb.get("unixtime")), "synchronizacja %s" % sb.get("last_sync_ts"))
    for k in ("Cloud", "MQTT", "WS"):
        row("polaczenie " + k, "jak przed", same(a["polaczenia"].get(k), b["polaczenia"].get(k)),
            "%s -> %s" % (a["polaczenia"].get(k), b["polaczenia"].get(k)))

    znak = {True: "OK", False: "ZMIANA", None: "-"}
    print("| Co | Oczekiwane | Wynik | Szczegol |")
    print("| --- | --- | --- | --- |")
    for co, oczek, ok, sz in rows:
        print("| %s | %s | %s | %s |" % (co, oczek, znak[ok], sz))
    bad = [r for r in rows if r[2] is False]
    print("\nzmian wbrew oczekiwaniu: %d" % len(bad))


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "zrob":
        zrob(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "porownaj":
        porownaj(sys.argv[2], sys.argv[3])
    else:
        print(__doc__ or "uzycie: migawka.py zrob <etykieta> | porownaj <a.json> <b.json>")
