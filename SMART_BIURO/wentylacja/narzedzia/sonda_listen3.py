# -*- coding: utf-8 -*-
"""Nasluch sondy v3 z kanalem komend.
Uzycie: python sonda_listen3.py <plik_komend>
Kazda zmiana zawartosci pliku komend -> jego ostatnia linia leci do sondy (telnet)."""
import socket, sys, time, os

LOGPATH = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_sondy.txt"
KEYS = ('[RX]', 'RAMKA', '[CMD]', 'TX-CMD', '[WiFi]')
CMD = sys.argv[1] if len(sys.argv) > 1 else None
ostatnia_cmd = None

while True:
    try:
        s = socket.create_connection(('192.168.0.172', 23), timeout=5)
        s.settimeout(0.5)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print('[ucho] polaczono z sonda', flush=True)
        buf = b''
        cisza = 0.0
        with open(LOGPATH, 'a', encoding='utf-8') as log:
            while True:
                # komendy
                if CMD and os.path.exists(CMD):
                    try:
                        tresc = open(CMD, encoding='utf-8').read().strip()
                        if tresc and tresc != ostatnia_cmd:
                            ostatnia_cmd = tresc
                            linia = tresc.splitlines()[-1].strip()
                            s.sendall((linia + '\n').encode())
                            print(f'[ucho] wyslano komende: {linia}', flush=True)
                    except Exception:
                        pass
                # odbior
                try:
                    d = s.recv(2048)
                    cisza = 0.0
                except socket.timeout:
                    cisza += 0.5
                    if cisza > 20.0:
                        print('[ucho] 20 s ciszy - zrywam i lacze od nowa', flush=True)
                        break
                    continue
                if not d:
                    break
                log.write(d.decode('utf-8', 'replace')); log.flush()
                buf += d
                while b'\n' in buf:
                    ln, buf = buf.split(b'\n', 1)
                    t = ln.decode('utf-8', 'replace').strip()
                    if t and any(k in t for k in KEYS):
                        print(t, flush=True)
        try: s.close()
        except Exception: pass
        print('[ucho] rozlaczono - wznawiam...', flush=True)
    except Exception:
        time.sleep(3)
