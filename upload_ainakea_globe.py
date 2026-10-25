# -*- coding: utf-8 -*-
"""Upload Location of Aina'akea.png to TALOD via botpasswords."""
import requests

API = "https://talod.miraheze.org/w/api.php"
BOT_USER = "Takeru-Sync@Letta_Takeru"
BOT_PASS = "mt54tvf8s22mcsdu02jf0jknt02ao3pc"

PNG = "B:\\02_GIT CONNECTED\\map\\Location of Aina'akea.png"
DEST = "Location of Aina'akea.png"
DESC = (
    "== Summary ==\n"
    "Orthographic location globe of [[Aina'akea]], [[Abyala]]. "
    "House style: grey ocean gradient, flat land, green highlight, subtle graticule.\n\n"
    "Generated from the adonia-project/map GIS dataset (make_ainakea_globe.py).\n\n"
    "[[Category:Location maps]]"
)

s = requests.Session()
s.headers.update({"User-Agent": "Takeru-Sync/1.0 (ainakea-globe-upload; talod.miraheze.org)"})

r = s.get(API, params={"action": "query", "meta": "tokens", "type": "login", "format": "json"})
lt = r.json()["query"]["tokens"]["logintoken"]
r = s.post(API, data={"action": "login", "lgname": BOT_USER, "lgpassword": BOT_PASS,
                      "lgtoken": lt, "format": "json"})
res = r.json()["login"]
print("login:", res["result"], res.get("lgusername", res.get("reason", "")))
assert res["result"] == "Success", res

r = s.get(API, params={"action": "query", "meta": "tokens", "format": "json"})
csrf = r.json()["query"]["tokens"]["csrftoken"]

with open(PNG, "rb") as f:
    r = s.post(API, data={
        "action": "upload", "filename": DEST, "token": csrf,
        "ignorewarnings": "1", "text": DESC,
        "comment": "Upload location globe of Aina'akea",
        "format": "json",
    }, files={"file": (DEST, f, "image/png")})

out = r.json()
print(out.get("upload", {}).get("result"), "->",
      out.get("upload", {}).get("imageinfo", {}).get("descriptionurl", out))
