import socket, time
LOGPATH = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_sondy.txt"
KEYS = ('[RX]', 'RAMKA', 'ODPOWIEDZ', '[WiFi]')
while True:
    try:
        s = socket.create_connection(('192.168.0.172', 23), timeout=5)
        s.settimeout(1.0)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print('[ucho] polaczono z sonda', flush=True)
        buf = b''
        cisza = 0.0
        with open(LOGPATH, 'a', encoding='utf-8') as log:
            while True:
                try:
                    d = s.recv(2048)
                    cisza = 0.0
                except socket.timeout:
                    cisza += 1.0
                    # sonda nadaje TX co 3 s i beacon co 2 s; 20 s bez bajtow = polaczenie zwisa
                    if cisza > 20.0:
                        print('[ucho] 20 s ciszy - zrywam i lacze od nowa', flush=True)
                        break
                    continue
                if not d:
                    break
                log.write(d.decode('utf-8', 'replace')); log.flush()
                buf += d
                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    t = line.decode('utf-8', 'replace').strip()
                    if t and any(k in t for k in KEYS):
                        print(t, flush=True)
        try: s.close()
        except Exception: pass
        print('[ucho] rozlaczono - wznawiam...', flush=True)
    except Exception:
        time.sleep(3)
