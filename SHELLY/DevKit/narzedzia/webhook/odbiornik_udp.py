# Odbiornik logu UDP modulu Shelly (sys.debug.udp.addr = 192.168.0.57:8514).
# Log UDP zaczyna sie zaraz po polaczeniu z Wi-Fi, wiec widac start modulu, ktorego
# monitor WebSocket nie lapie (laczy sie 20-45 s po starcie). Dziala w kontenerze:
#   docker run -d --name udplog-q11 -e TZ=Europe/Warsaw -p 8514:8514/udp -v <ten folder>:/w \
#     --entrypoint python3 ghcr.io/home-assistant/home-assistant:stable -u /w/odbiornik_udp.py
import datetime
import os
import socket

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "udp_log.txt")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 8514))
with open(LOG, "a", encoding="utf-8") as f:
    while True:
        data, addr = s.recvfrom(4096)
        t = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        for line in data.decode("utf-8", "replace").splitlines():
            f.write(t + " " + line + "\n")
        f.flush()
