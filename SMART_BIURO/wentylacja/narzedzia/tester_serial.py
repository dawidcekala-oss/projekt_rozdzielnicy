import serial, sys, time
LOG = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_tester_biurkowy.txt"
cmdfile = sys.argv[1] if len(sys.argv) > 1 else None
last_cmd = ''
while True:
    try:
        port = serial.Serial('COM6', 115200, timeout=1)
    except Exception:
        time.sleep(2); continue
    print('[reader] COM6 otwarty', flush=True)
    log = open(LOG, "a", encoding="utf-8")
    log.write(f"\n=== sesja {time.strftime('%H:%M:%S')} ===\n"); log.flush()
    try:
        while True:
            line = port.readline().decode('utf-8', 'replace').strip()
            if line:
                log.write(line + "\n"); log.flush()
                print(line, flush=True)
            if cmdfile:
                try:
                    c = open(cmdfile).read().strip()
                    if c and c != last_cmd:
                        last_cmd = c
                        port.write(c[-1].encode()); port.flush()
                except FileNotFoundError:
                    pass
    except Exception:
        print('[reader] COM6 odpadl - czekam na powrot', flush=True)
        try: port.close()
        except Exception: pass
        log.close()
        time.sleep(2)
