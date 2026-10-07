# Serwer czasu (SNTP) z przesunieciem, test C6: podaje czas przesuniety o OFFSET sekund, zeby
# zegar ladowarki doszedl do pelnej godziny w 2 min zamiast czekac do dwoch godzin.
# Zegar laptopa zostaje bez zmian; modul przekazuje sterownikowi to, co dostal od serwera czasu.
# Dziala w kontenerze na porcie 123 zamiast serwera `ntp` (ten trzeba na czas testu zatrzymac):
#   docker run -d --name ntp-przes -p 123:123/udp -v <folder>:/w --entrypoint python3 \
#     ghcr.io/home-assistant/home-assistant:stable -u /w/zegar_przesuniety.py <OFFSET_s>
import socket
import struct
import sys
import time

OFFSET = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
NTP_EPOCH = 2208988800  # sekundy od 1900 do 1970


def ntp_ts(t):
    sec = int(t)
    return struct.pack("!II", sec + NTP_EPOCH, int((t - sec) * 2 ** 32) & 0xFFFFFFFF)


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 123))
print("serwer czasu z przesunieciem %+.0f s" % OFFSET, flush=True)
while True:
    data, addr = s.recvfrom(1024)
    if len(data) < 48:
        continue
    recv = time.time() + OFFSET
    poll = struct.unpack("!b", data[2:3])[0]
    head = struct.pack("!BBbb", (0 << 6) | (4 << 3) | 4, 2, poll, -20)   # LI 0, wersja 4, tryb serwer
    pkt = head + struct.pack("!II", 0, 0) + b"LOCL" + ntp_ts(recv - 1) + data[40:48] + ntp_ts(recv) + ntp_ts(time.time() + OFFSET)
    s.sendto(pkt, addr)
    print("%s zapytanie od %s, podano %s" % (time.strftime("%H:%M:%S"), addr[0], time.strftime("%H:%M:%S", time.localtime(recv))), flush=True)
