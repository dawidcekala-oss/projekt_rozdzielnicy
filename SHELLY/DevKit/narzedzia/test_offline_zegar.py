"""Test zachowania DevKitu bez serwera czasu i bez chmury (AMPERE POINT, 2026-09-25).

1. zapamietuje ustawienia serwera czasu,
2. wpisuje nieosiagalny serwer 192.0.2.1 (adres testowy, nie istnieje w sieci),
3. restartuje DevKit i czeka, az wroci,
4. sprawdza zegar i rozmowe z Q11 (pola z Q11 musza sie odswiezyc),
5. ustawia czas z laptopa poleceniem Sys.SetTime (tak zrobi most bez internetu),
6. przywraca poprzedni serwer czasu.
"""
import json
import sys
import time
import urllib.request

H = sys.argv[1] if len(sys.argv) > 1 else "192.168.0.238"


def rpc(method, params=None, timeout=10):
    body = json.dumps({"id": 1, "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(f"http://{H}/rpc", data=body, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read().decode())
    if "error" in d:
        raise RuntimeError(d["error"])
    return d.get("result")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


sntp_before = rpc("Sys.GetConfig")["sntp"]
log("serwer czasu przed testem:", sntp_before)
try:
    log("wpisuje nieosiagalny serwer czasu:", rpc("Sys.SetConfig", {"config": {"sntp": {"server": "192.0.2.1"}}}))
    log("restart:", rpc("Shelly.Reboot"))
    time.sleep(8)
    for _ in range(60):
        try:
            st = rpc("Sys.GetStatus", timeout=3)
            break
        except Exception:
            time.sleep(2)
    else:
        raise SystemExit("DevKit nie wrocil w 2 min")
    log(f"DevKit wrocil, uptime {st['uptime']} s, time={st.get('time')}, unixtime={st.get('unixtime')}")
    time.sleep(20)
    st = rpc("Sys.GetStatus")
    log(f"po 20 s: time={st.get('time')}, unixtime={st.get('unixtime')}, last_sync_ts={st.get('last_sync_ts')}")
    mode = rpc("Enum.GetStatus", {"id": 200})
    lim = rpc("Number.GetStatus", {"id": 200})
    log("stan z Q11:", mode, "| limit:", lim)
    now = int(time.time())
    log("Sys.SetTime z laptopa:", rpc("Sys.SetTime", {"unixtime": now}))
    time.sleep(2)
    st = rpc("Sys.GetStatus")
    log(f"po ustawieniu: time={st.get('time')}, unixtime={st.get('unixtime')} (laptop {int(time.time())})")
finally:
    log("przywracam serwer czasu:", rpc("Sys.SetConfig", {"config": {"sntp": sntp_before}}))
    log("serwer czasu po tescie:", rpc("Sys.GetConfig")["sntp"])
