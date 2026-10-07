# Test pamieci (dokument 04, P4-P5): laptop zmienia pole testowe number:250 co 5 s na kolejne
# wartosci (201, 202, ...; odstep z drugiego argumentu, domyslnie 5 s), a miedzy zmianami co 0,25 s
# sprawdza, czy modul odpowiada.
# Przy zaniku zasilania petla konczy sie sama, wiec po starcie nic nie nadpisuje pola:
# jego wartosc to to, co modul zapisal w pamieci. Na koncu: ile sekund minelo od ostatniej
# zmiany do ostatniej odpowiedzi modulu (zanik nastapil w ciagu 0,25-0,5 s pozniej).
# Kazda zmiana -> logi/pamiec/zmiany_<czas>.txt
import datetime
import json
import os
import sys
import time
import urllib.request

HOST = "http://192.168.0.238/rpc"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logi", "pamiec")
start = int(sys.argv[1]) if len(sys.argv) > 1 else 201
step_s = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0   # odstep miedzy zmianami
os.makedirs(OUT, exist_ok=True)
path = os.path.normpath(os.path.join(OUT, "zmiany_%s.txt" % datetime.datetime.now().strftime("%H%M%S")))


def call(method, params, timeout):
    body = json.dumps({"id": 1, "method": method, "params": params}).encode()
    return json.load(urllib.request.urlopen(urllib.request.Request(HOST, data=body, method="POST"), timeout=timeout))


def now():
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]


v = start
last_set_t = None
last_alive = None
with open(path, "w", encoding="utf-8") as f:
    while v < 1000:
        try:
            call("Number.Set", {"id": 250, "value": v}, 2)
        except Exception as e:  # noqa: BLE001
            f.write("%s %d BLAD %s\n" % (now(), v, e))
            break
        last_set_t = time.monotonic()
        last_alive = last_set_t
        f.write("%s %d ok\n" % (now(), v))
        f.flush()
        dead = False
        while time.monotonic() - last_set_t < step_s:
            time.sleep(0.25)
            try:
                call("Shelly.GetDeviceInfo", {}, 0.6)
                last_alive = time.monotonic()
            except Exception:  # noqa: BLE001
                if time.monotonic() - last_alive > 1.5:
                    dead = True
                    break
        if dead:
            break
        v += 1
    last_ok = v if dead else v - 1
    msg = "KONIEC: ostatnia udana wartosc %d; ostatnia odpowiedz modulu %.2f s po jej ustawieniu" % (
        last_ok, (last_alive - last_set_t) if last_set_t else -1)
    f.write(msg + "\n")
    print(msg, flush=True)
print(path)
