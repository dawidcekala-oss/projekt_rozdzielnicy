# Odbiornik webhookow z modulu Shelly (test B5). Dziala w kontenerze Docker z obrazu
# Home Assistant (ma Pythona), bo zapora Windows blokuje polaczenia przychodzace do
# programow na laptopie, a porty wystawione przez Docker przechodza.
#   docker run -d --name webhook-q11 -p 8099:8099 -v <ten folder>:/w \
#     --entrypoint python3 ghcr.io/home-assistant/home-assistant:stable -u /w/odbiornik_webhook.py
# Kazde wywolanie: czas, adres nadawcy, metoda, sciezka z parametrami, tresc -> webhooki.log
import datetime
import http.server
import os

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webhooki.log")


class H(http.server.BaseHTTPRequestHandler):
    def _handle(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        line = "%s %s %s %s %s" % (
            datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3],
            self.client_address[0], self.command, self.path, body)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line, flush=True)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    do_GET = _handle
    do_POST = _handle

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(("0.0.0.0", 8099), H).serve_forever()
