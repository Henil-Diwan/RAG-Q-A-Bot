import base64
import os
import string
import sys
import urllib.request
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = "http://www.plantuml.com/plantuml/png/"

_plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + "-_"
_b64_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
_b64_to_plant = bytes.maketrans(_b64_alphabet.encode(), _plantuml_alphabet.encode())


def encode(text: str) -> str:
    deflated = zlib.compress(text.encode("utf-8"))[2:-4]
    return base64.b64encode(deflated).translate(_b64_to_plant).decode("ascii")


def render(puml_path: str) -> str:
    with open(puml_path, "r", encoding="utf-8") as f:
        text = f.read()
    url = SERVER + encode(text)
    png_path = os.path.splitext(puml_path)[0] + ".png"
    req = urllib.request.Request(url, headers={"User-Agent": "puml-render/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    with open(png_path, "wb") as f:
        f.write(data)
    return png_path


def main() -> int:
    failures = 0
    for name in sorted(os.listdir(HERE)):
        if not name.endswith(".puml"):
            continue
        path = os.path.join(HERE, name)
        try:
            out = render(path)
            print(f"OK  {name} -> {os.path.basename(out)} ({os.path.getsize(out)} bytes)")
        except Exception as e:
            failures += 1
            print(f"ERR {name}: {e}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
