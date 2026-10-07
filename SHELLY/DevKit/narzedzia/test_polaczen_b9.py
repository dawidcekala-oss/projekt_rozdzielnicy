# Test B9: ile polaczen WebSocket naraz przyjmuje modul (ws://192.168.0.238/rpc).
# Otwiera kolejne polaczenia (do MAX), na kazdym pyta o Sys.GetStatus i mierzy czas odpowiedzi.
# Co 5 polaczen sprawdza, czy wszystkie wczesniejsze nadal odpowiadaja. Na koncu zamyka wszystkie.
import asyncio
import json
import sys
import time

import websockets

URL = "ws://192.168.0.238/rpc"
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 30


async def call(ws, i, rid):
    t0 = time.monotonic()
    await ws.send(json.dumps({"id": rid, "src": "b9-%d" % i, "method": "Sys.GetStatus"}))
    while True:
        r = json.loads(await asyncio.wait_for(ws.recv(), 5))
        if r.get("id") == rid:
            return (time.monotonic() - t0) * 1000, ("result" in r)


async def main():
    conns = []
    rid = 1
    for i in range(1, MAX + 1):
        try:
            ws = await asyncio.wait_for(websockets.connect(URL, open_timeout=5, ping_interval=None), 6)
            rid += 1
            ms, ok = await call(ws, i, rid)
            conns.append(ws)
            print("polaczenie %2d: otwarte, odpowiedz %4.0f ms %s" % (i, ms, "" if ok else "(blad)"), flush=True)
        except Exception as e:
            print("polaczenie %2d: ODMOWA/BLAD: %s" % (i, repr(e)[:120]), flush=True)
            break
        if i % 5 == 0:
            alive, times = 0, []
            for j, c in enumerate(conns, 1):
                try:
                    rid += 1
                    ms, ok = await call(c, j, rid)
                    alive += 1
                    times.append(ms)
                except Exception:
                    pass
            print("  kontrola: %d z %d starych odpowiada, sredni czas %.0f ms, najdluzszy %.0f ms" % (
                alive, len(conns), sum(times) / max(1, len(times)), max(times) if times else 0), flush=True)
    for c in conns:
        await c.close()
    print("zamknieto %d polaczen" % len(conns))


asyncio.run(main())
