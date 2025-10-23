import os
import json
import subprocess
import urllib.request

# 🧬 Forcer l'encodage UTF-8 dans le terminal
os.system("chcp 65001")

# 🎤 Demander le pseudo
print("👤 Entrez votre pseudo Minecraft (sans caractères spéciaux de préférence) :")
username = input("➤ ").strip()
if not username:
    username = "ChatonLeFelin"

# 📂 Dossiers principaux
minecraft_dir = r"C:\Users\veras\AppData\Roaming\.minecraft"
version = "1.21.6"
version_dir = os.path.join(minecraft_dir, "versions", version)
libraries_dir = os.path.join(minecraft_dir, "libraries")
natives_dir = r"C:\Users\veras\Downloads\dll\lwjgl\natives"

# 📜 Charger le fichier JSON
json_path = os.path.join(version_dir, f"{version}.json")
with open(json_path, "r", encoding="utf-8") as f:
    version_data = json.load(f)

# 📦 Collecter les libs
classpath_entries = []

def handle_library(lib):
    try:
        name = lib.get("name", "")
        parts = name.split(":")
        if len(parts) != 3:
            return
        group, artifact, lib_version = parts
        jar_path = os.path.join(
            libraries_dir,
            group.replace(".", os.sep),
            artifact,
            lib_version,
            f"{artifact}-{lib_version}.jar"
        )
        if not os.path.exists(jar_path):
            url = lib["downloads"]["artifact"]["url"]
            os.makedirs(os.path.dirname(jar_path), exist_ok=True)
            print(f"⬇️ Téléchargement : {artifact}-{lib_version}")
            urllib.request.urlretrieve(url, jar_path)
        classpath_entries.append(jar_path)
    except Exception as e:
        print(f"⚠️ Erreur avec {name}: {e}")

for lib in version_data.get("libraries", []):
    handle_library(lib)

# ➕ Ajouter Minecraft JAR
jar_path = os.path.join(version_dir, f"{version}.jar")
classpath_entries.append(jar_path)
classpath = ";".join(classpath_entries)

# 🚀 Commande Java
launch_command = [
    "java",
    f"-Djava.library.path={natives_dir}",
    "-cp", classpath,
    "--enable-native-access=ALL-UNNAMED",
    "net.minecraft.client.main.Main",
    "--username", username,
    "--version", version,
    "--gameDir", minecraft_dir,
    "--assetsDir", os.path.join(minecraft_dir, "assets"),
    "--assetIndex", version_data["assetIndex"]["id"],
    "--uuid", "00000000-0000-0000-0000-000000000000",
    "--accessToken", "0",
    "--userType", "legacy"
]

print(f"\n⏳ Lancement de Minecraft pour {username}... 🐾")
subprocess.run(launch_command)
