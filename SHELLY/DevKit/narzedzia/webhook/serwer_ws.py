# Serwer testowy dla wychodzacego WebSocket modulu Shelly (test B8).
# Modul sam laczy sie z ws://192.168.0.57:8098/shelly (ws.server w module). Serwer:
#   - zapisuje kazda ramke od modulu (ws_log.txt),
#   - 5 s po polaczeniu pyta o dane urzadzenia, 10 s po polaczeniu wysyla limit 10 A,
#     20 s po polaczeniu przywraca limit z chwili polaczenia.
# Dziala w kontenerze z obrazu Home Assistant (aiohttp jest w obrazie):
#   docker run -d --name ws-q11 -e TZ=Europe/Warsaw -p 8098:8098 -v <ten folder>:/w \
#     --entrypoint python3 ghcr.io/home-assistant/home-assistant:stable -u /w/serwer_ws.py
import asyncio
import datetime
import json
import os

from aiohttp import WSMsgType, web

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ws_log.txt")


def log(msg):
    line = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3] + " " + msg
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


async def handler(request):
    ws = web.WebSocketResponse(heartbeat=None)
    await ws.prepare(request)
    log("POLACZENIE od %s, naglowki: %s" % (request.remote, dict(request.headers)))
    state = {"limit": None}

    async def send(obj):
        log("-> " + json.dumps(obj))
        await ws.send_str(json.dumps(obj))

    async def script():
        await asyncio.sleep(5)
        await send({"id": 1, "src": "ampere-serwer", "method": "Shelly.GetDeviceInfo"})
        await send({"id": 2, "src": "ampere-serwer", "method": "Number.GetStatus", "params": {"id": 200}})
        await asyncio.sleep(5)
        await send({"id": 3, "src": "ampere-serwer", "method": "Number.Set", "params": {"id": 200, "value": 10}})
        await asyncio.sleep(10)
        if state["limit"] is not None:
            await send({"id": 4, "src": "ampere-serwer", "method": "Number.Set",
                        "params": {"id": 200, "value": state["limit"]}})

    task = asyncio.ensure_future(script())
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                log("<- " + msg.data[:600])
                try:
                    d = json.loads(msg.data)
                    if d.get("id") == 2 and "result" in d:
                        state["limit"] = d["result"].get("value")
                except ValueError:
                    pass
            elif msg.type == WSMsgType.BINARY:
                log("<- (binarne) %d B" % len(msg.data))
            else:
                log("ramka typu %s" % msg.type)
    finally:
        task.cancel()
        log("ROZLACZENIE")
    return ws


app = web.Application()
app.router.add_get("/shelly", handler)
app.router.add_get("/", handler)
log("serwer start")
web.run_app(app, host="0.0.0.0", port=8098, print=None)
