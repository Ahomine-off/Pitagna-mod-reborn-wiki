# cat_html_viewer.py
import tkinter as tk
from tkhtmlview import HTMLLabel
import asyncio, threading, sys
from client_cat import cat_request  # ton client pour cat://

class CatBrowserHTML(tk.Tk):
    def __init__(self, start_url=None):
        super().__init__()
        self.title("Cat Browser 🐈‍⬛ - HTML View")
        self.geometry("800x600")

        # UI
        top = tk.Frame(self); top.pack(fill="x")
        self.url_var = tk.StringVar(value=start_url or "cat://localhost:8087/")
        tk.Entry(top, textvariable=self.url_var).pack(side="left", fill="x", expand=True, padx=5, pady=5)
        tk.Button(top, text="Go", command=self.go).pack(side="left", padx=5)

        # Viewer (HTML ou texte)
        self.html_area = HTMLLabel(self, html="<i>Bienvenue !</i>", background="white")
        self.html_area.pack(fill="both", expand=True)
        self.html_area.fit_height()

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        if start_url:
            self.go()

    def go(self):
        url = self.url_var.get().strip()
        self.html_area.set_html(f"<i>Chargement de {url}...</i>")
        asyncio.run_coroutine_threadsafe(self.fetch(url), self.loop)

    async def fetch(self, url):
        try:
            status, reason, headers, body = await cat_request(url)
            content_type = headers.get("Content-Type", "").lower()
            html = body.decode("utf-8", "replace")

            # Rendu HTML ou texte
            if "html" in content_type:
                self.after(0, lambda: self.html_area.set_html(html))
            else:
                safe = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                self.after(0, lambda: self.html_area.set_html(f"<pre>{safe}</pre>"))
        except Exception as e:
            self.after(0, lambda: self.html_area.set_html(f"<b>Erreur :</b><br>{str(e)}"))

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    app = CatBrowserHTML(start_url=url)
    app.mainloop()
