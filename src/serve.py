"""本機啟動器：固定網址，重複開啟時直接回到既有網站。"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
from urllib.request import urlopen
import webbrowser

ROOT = Path(__file__).resolve().parent.parent
URL = 'http://127.0.0.1:8766/'

def main():
    try:
        server = ThreadingHTTPServer(('127.0.0.1', 8766), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    except OSError:
        try:
            with urlopen(URL, timeout=2) as response:
                page = response.read(8192).decode('utf-8')
            if 'Sprite Lab' in page and './src/app.js' in page:
                print('動畫工作台已啟動，正在為你開啟。')
                webbrowser.open(URL)
                return
        except Exception:
            pass
        input('本機網址被其他程式佔用，請關閉該程式再試。按 Enter 關閉。')
        return
    print('動畫工作台已開啟：'+URL, flush=True)
    print('使用期間請保留這個視窗，按 Control-C 可停止。', flush=True)
    webbrowser.open(URL)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
