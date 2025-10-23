import asyncio
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs
from email.utils import formatdate

MAX_HEADER_SIZE = 16 * 1024
MAX_BODY_SIZE = 4 * 1024 * 1024
DOC_ROOT = Path(__file__).parent / "public"

STATUS_TEXT = {
    200: "OK", 204: "No Content", 301: "Moved Permanently",
    304: "Not Modified", 400: "Bad Request", 404: "Not Found", 405: "Method Not Allowed",
    411: "Length Required", 413: "Payload Too Large", 500: "Internal Server Error"
}

def http_date():
    return formatdate(usegmt=True)

async def read_line(reader):
    line = await reader.readline()
    if not line:
        return None
    if len(line) > MAX_HEADER_SIZE:
        raise ValueError("Header line too long")
    return line.rstrip(b"\r\n").decode("utf-8", "replace")

async def read_headers(reader):
    headers = {}
    total = 0
    while True:
        line = await reader.readline()
        total += len(line)
        if total > MAX_HEADER_SIZE:
            raise ValueError("Headers too large")
        if line in (b"\r\n", b"\n", b""):
            break
        k, _, v = line.decode("utf-8", "replace").partition(":")
        headers[k.strip().title()] = v.strip()
    return headers

async def read_body(reader, headers):
    length = int(headers.get("Content-Length", "0") or "0")
    if length < 0:
        raise ValueError("Invalid Content-Length")
    if length > MAX_BODY_SIZE:
        raise ValueError("Body too large")
    if length == 0:
        return b""
    return await reader.readexactly(length)

def build_response(status, headers=None, body=b""):
    reason = STATUS_TEXT.get(status, "OK")
    headers = dict(headers or {})
    headers.setdefault("Date", http_date())
    headers.setdefault("Cat-Version", "1.1")
    headers.setdefault("Content-Length", str(len(body)))
    lines = [f"CAT/1.0 {status} {reason}\r\n"]
    for k, v in headers.items():
        lines.append(f"{k}: {v}\r\n")
    lines.append("\r\n")
    head = "".join(lines).encode("utf-8")
    return head + body

def safe_path(url_path: str) -> Path:
    # Décode et sécurise contre l'escape du docroot
    p = unquote(url_path or "/")
    if not p.startswith("/"):
        p = "/" + p
    full = (DOC_ROOT / p.lstrip("/")).resolve()
    if not str(full).startswith(str(DOC_ROOT.resolve())):
        return DOC_ROOT / "__forbidden__"
    return full

def guess_type(p: Path) -> str:
    ctype, _ = mimetypes.guess_type(str(p))
    return ctype or "application/octet-stream"

def dir_listing(path: Path, url_path: str) -> bytes:
    entries = []
    for child in sorted(path.iterdir()):
        name = child.name + ("/" if child.is_dir() else "")
        entries.append(name)
    listing = "Directory: {}\n\n{}\n".format(url_path, "\n".join(entries))
    return listing.encode("utf-8")

async def handle_route(method, path, headers, body):
    # Routes simples
    if path == "/":
        data = b"Bienvenue sur cat://\n"
        return 200, {"Content-Type": "text/plain; charset=utf-8"}, data

    if path == "/hello":
        who = "cat"
        # Query ?name=...
        name = headers.get("__query_name__")
        if name:
            who = name
        data = f"Hello, {who}!\n".encode("utf-8")
        return 200, {"Content-Type": "text/plain; charset=utf-8"}, data

    if path == "/ping" or method == "PING":
        return 204, {}, b""

    if path == "/echo" and method == "POST":
        return 200, {"Content-Type": headers.get("Content-Type", "application/octet-stream")}, body

    # Fichiers statiques
    target = safe_path(path)
    if target.name == "__forbidden__":
        return 404, {"Content-Type": "text/plain; charset=utf-8"}, b"Not Found\n"

    if target.is_dir():
        # Rediriger /dir vers /dir/ (301)
        if not path.endswith("/"):
            return 301, {"Location": path + "/"}, b""
        for idx in ("index.txt", "index.html"):
            ip = target / idx
            if ip.exists():
                data = ip.read_bytes()
                return 200, {"Content-Type": guess_type(ip)}, data
        # Listing basique
        return 200, {"Content-Type": "text/plain; charset=utf-8"}, dir_listing(target, path)

    if target.exists() and target.is_file():
        data = target.read_bytes()
        return 200, {"Content-Type": guess_type(target)}, data

    return 404, {"Content-Type": "text/plain; charset=utf-8"}, b"Not Found\n"

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    keep_alive = True
    try:
        while keep_alive:
            req_line = await read_line(reader)
            if req_line is None:
                break
            parts = req_line.split()
            if len(parts) != 3 or parts[2] != "CAT/1.0":
                writer.write(build_response(400, {"Content-Type": "text/plain; charset=utf-8"}, b"Invalid request line\n"))
                await writer.drain()
                break
            method, url_path, _ = parts

            headers = await read_headers(reader)
            # Keep-Alive gestion
            connection = headers.get("Connection", "").lower()
            if connection == "close":
                keep_alive = False

            # Parsing query simple
            u = urlparse(url_path)
            path = u.path or "/"
            qs = parse_qs(u.query or "")
            # On passe un "header virtuel" pour /hello
            if "name" in qs:
                headers["__query_name__"] = qs["name"][0]

            # Corps
            body = b""
            if method in ("POST",):
                body = await read_body(reader, headers)

            # Méthodes autorisées
            if method not in ("GET", "HEAD", "POST", "PING"):
                resp = build_response(405, {"Content-Type": "text/plain; charset=utf-8"}, b"Method Not Allowed\n")
                writer.write(resp); await writer.drain()
                break

            # Route
            status, resp_headers, data = await handle_route(method, path, headers, body)

            # HEAD: pas de corps
            out_body = b"" if method == "HEAD" else data
            resp_headers.setdefault("Connection", "keep-alive" if keep_alive else "close")
            writer.write(build_response(status, resp_headers, out_body))
            await writer.drain()

            if not keep_alive:
                break

    except Exception as e:
        err = f"Server error: {e}\n".encode()
        writer.write(build_response(500, {"Content-Type": "text/plain; charset=utf-8", "Connection": "close"}, err))
        await writer.drain()
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass

async def main(host="127.0.0.1", port=8087):
    DOC_ROOT.mkdir(exist_ok=True)
    server = await asyncio.start_server(handle_client, host, port)
    addr = ", ".join(str(s.getsockname()) for s in server.sockets)
    print(f"cat:// server listening on {addr}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
