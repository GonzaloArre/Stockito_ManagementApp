#!/usr/bin/env python3
"""
STOCKITO - programa en Python (solo biblioteca estandar).

  * Sirve la misma pantalla de siempre (stockito.html) sin tocar su diseno ni su logica.
  * Guarda los datos en una base SQLite (stockito.db) en vez de en el navegador.
  * Hace una copia de seguridad diaria (guarda las ultimas 30).
  * Si se abre dos veces, la segunda solo vuelve a abrir la ventana.

Uso:
  python stockito.py            -> arranca y abre la ventana
  python stockito.py --cerrar   -> cierra el programa que esta corriendo
  python stockito.py --puerto 9000 --no-abrir

Seguridad: escucha SOLO en esta computadora (127.0.0.1). Las contrasenas y permisos se
verifican en la pantalla, asi que NO hay que exponerlo a la red ni a internet.
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import urllib.request
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
INSTALADO = bool(getattr(sys, "frozen", False))  # True cuando corre como stockito.exe
RECURSOS = Path(getattr(sys, "_MEIPASS", BASE))  # carpeta donde esta stockito.html
if INSTALADO and sys.platform == "win32":
    DATOS = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "STOCKITO"
else:
    DATOS = BASE
DATOS.mkdir(parents=True, exist_ok=True)

DB = DATOS / "stockito.db"
COPIAS = DATOS / "copias_de_seguridad"
HTML = RECURSOS / "stockito.html"
LOCK = threading.Lock()
MAX_BYTES = 20 * 1024 * 1024
SERVIDOR = None

# Las dos unicas lineas de la pantalla que guardan datos en el navegador.
# Python las reemplaza al servir la pagina; stockito.html queda intacto.
CARGAR = "let S;try{S=JSON.parse(localStorage.getItem('caja3'))}catch(e){}"
GUARDAR = "const save=()=>{try{localStorage.setItem('caja3',JSON.stringify(S))}catch(e){}};"
GUARDAR_NUEVO = (
    "const save=()=>{fetch('/api/state',{method:'POST',headers:{'Content-Type':'application/json'},"
    "body:JSON.stringify(S)}).catch(()=>{try{toast('No se pudo guardar. Revisa que el programa siga abierto')}catch(e){}})};"
)


def decir(*partes):
    if sys.stdout:  # en la version instalada no hay consola
        print(*partes)


def aviso(texto):
    """Muestra un mensaje: en consola, o como ventana de Windows si no hay consola."""
    if sys.stdout:
        print(texto)
    elif sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, texto, "STOCKITO", 0x10)
        except Exception:
            pass


def conectar():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL, actualizado TEXT)")
    return c


def leer_estado():
    with LOCK:
        c = conectar()
        try:
            fila = c.execute("SELECT v FROM kv WHERE k='state'").fetchone()
        finally:
            c.close()
    return fila[0] if fila else "null"


def guardar_estado(raw):
    with LOCK:
        c = conectar()
        try:
            c.execute(
                "INSERT INTO kv(k, v, actualizado) VALUES('state', ?, datetime('now','localtime')) "
                "ON CONFLICT(k) DO UPDATE SET v=excluded.v, actualizado=excluded.actualizado",
                (raw,),
            )
            c.commit()
        finally:
            c.close()


def pagina():
    html = HTML.read_text(encoding="utf-8")
    if CARGAR not in html or GUARDAR not in html:
        raise SystemExit("stockito.html no es la version esperada: no se encontraron las lineas de guardado.")
    estado = leer_estado().replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return html.replace(CARGAR, "let S=" + estado + ";").replace(GUARDAR, GUARDAR_NUEVO)


def copia_diaria():
    if not DB.exists():
        return
    COPIAS.mkdir(exist_ok=True)
    destino = COPIAS / f"stockito-{date.today():%Y-%m-%d}.db"
    if not destino.exists():
        shutil.copy2(DB, destino)
    for vieja in sorted(COPIAS.glob("stockito-*.db"))[:-30]:
        vieja.unlink()


def abrir(url):
    """En Windows intenta abrirlo como ventana de aplicacion (sin pestanas ni barra de direcciones)."""
    if sys.platform == "win32":
        for var in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"):
            raiz = os.environ.get(var)
            if not raiz:
                continue
            for rel in (r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe"):
                exe = Path(raiz) / rel
                if exe.exists():
                    try:
                        subprocess.Popen([str(exe), "--app=" + url])
                        return
                    except OSError:
                        pass
    webbrowser.open(url)


def ya_abierto(puerto):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{puerto}/api/state", timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False


def pedir_cierre(puerto):
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{puerto}/api/apagar", data=b"{}", method="POST")
        with urllib.request.urlopen(req, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


class Manejador(BaseHTTPRequestHandler):
    server_version = "Stockito"

    def log_message(self, *args):
        pass

    def _enviar(self, codigo, cuerpo, tipo):
        datos = cuerpo if isinstance(cuerpo, bytes) else cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        ruta = self.path.split("?")[0]
        if ruta in ("/", "/index.html"):
            self._enviar(200, pagina(), "text/html; charset=utf-8")
        elif ruta == "/api/state":
            self._enviar(200, leer_estado(), "application/json")
        else:
            self._enviar(404, "No encontrado", "text/plain; charset=utf-8")

    def do_POST(self):
        origen, host = self.headers.get("Origin"), self.headers.get("Host")
        if origen and origen != f"http://{host}":  # evita que otra pagina escriba o cierre el programa
            return self._enviar(403, "Origen no permitido", "text/plain; charset=utf-8")
        if self.path == "/api/apagar":
            self._enviar(200, '{"ok":true}', "application/json")
            threading.Thread(target=SERVIDOR.shutdown, daemon=True).start()
            return
        if self.path != "/api/state":
            return self._enviar(404, "No encontrado", "text/plain; charset=utf-8")
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_BYTES:
            return self._enviar(413, "Tamano invalido", "text/plain; charset=utf-8")
        raw = self.rfile.read(n).decode("utf-8")
        try:
            json.loads(raw)
        except ValueError:
            return self._enviar(400, "JSON invalido", "text/plain; charset=utf-8")
        guardar_estado(raw)
        self._enviar(200, '{"ok":true}', "application/json")


def main():
    global SERVIDOR
    if sys.stdout:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="STOCKITO")
    ap.add_argument("--puerto", type=int, default=8765)
    ap.add_argument("--no-abrir", action="store_true", help="no abrir la ventana automaticamente")
    ap.add_argument("--cerrar", action="store_true", help="cierra el programa que esta corriendo")
    a = ap.parse_args()
    url = f"http://127.0.0.1:{a.puerto}"

    if a.cerrar:
        decir("STOCKITO cerrado." if pedir_cierre(a.puerto) else "STOCKITO no estaba abierto.")
        return
    if ya_abierto(a.puerto):  # ya esta corriendo: solo mostrar la ventana
        if not a.no_abrir:
            abrir(url)
        return
    try:
        if not HTML.exists():
            raise SystemExit("Falta el archivo stockito.html junto al programa.")
        pagina()
    except SystemExit as e:
        aviso(str(e))
        return
    copia_diaria()
    try:
        SERVIDOR = ThreadingHTTPServer(("127.0.0.1", a.puerto), Manejador)
    except OSError:
        aviso(f"No se pudo usar el puerto {a.puerto}. Cerra otros programas o usa --puerto con otro numero.")
        return

    decir("STOCKITO funcionando en", url)
    decir("Datos guardados en:", DB)
    decir("Para cerrar el programa: Ctrl + C.")
    if not a.no_abrir:
        threading.Timer(0.8, lambda: abrir(url)).start()
    try:
        SERVIDOR.serve_forever()
    except KeyboardInterrupt:
        decir("\nPrograma cerrado.")


if __name__ == "__main__":
    main()
