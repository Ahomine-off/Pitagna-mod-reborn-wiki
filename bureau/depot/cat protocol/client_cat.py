# client.py
import asyncio, ssl
from urllib.parse import urlparse

async def cat_request(url, method="GET", body=b"", headers=None, timeout=10, tls=False):
    headers = headers or {}
    u = urlparse(url)
    assert u.scheme == "cat", "URL doit être cat://"
    host = u.hostname or "localhost"
    port = u.port or (8443 if tls else 8087)
    path = u.path or "/"
    if u.query:
        path += "?" + u.query

    ssl_ctx = None
    if tls:
        ssl_ctx = ssl.create_default_context()
        # en dev: ssl_ctx.check_hostname = False; ssl_ctx.verify_mode = ssl.CERT_NONE

    reader, writer = await asyncio.open_connection(host, port, ssl=ssl_ctx, server_hostname=host if tls else None)
    try:
        # Build request
        lines = [f"{method} {path} CAT/1.0\r\n"]
        headers = {**{"Host": host, "Accept": "*/*"}, **headers}
        if body:
            headers["Content-Length"] = str(len(body))
        for k, v in headers.items():
            lines.append(f"{k}: {v}\r\n")
        lines.append("\r\n")
        writer.write("".join(lines).encode("utf-8") + body)
        await writer.drain()

        # Read status line
        status_line = (await reader.readline()).decode("utf-8").rstrip("\r\n")
        proto, status, *rest = status_line.split(" ", 2)
        reason = rest[0] if rest else ""
        # Headers
        resp_headers = {}
        while True:
            line = await reader.readline()
            if line in (b"\r\n", b"\n", b""):
                break
            k, _, v = line.decode("utf-8").partition(":")
            resp_headers[k.strip().title()] = v.strip()
        length = int(resp_headers.get("Content-Length", "0"))
        body = await reader.readexactly(length) if length else b""
        return int(status), reason, resp_headers, body
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    import asyncio, sys
    url = sys.argv[1] if len(sys.argv) > 1 else "cat://localhost:8087/hello"
    status, reason, headers, body = asyncio.run(cat_request(url))
    print(f"Status: {status} {reason}")
    for k, v in headers.items():
        print(f"{k}: {v}")
    if body:
        print()
        try:
            print(body.decode("utf-8"))
        except:
            print(f"<{len(body)} bytes>")
