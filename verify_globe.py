import requests

r = requests.get(
    "https://talod.miraheze.org/w/api.php",
    params={
        "action": "query",
        "titles": "File:Location of Aina'akea.png",
        "prop": "imageinfo",
        "iiprop": "size|mime|url",
        "format": "json",
    },
    headers={"User-Agent": "Takeru-Sync/1.0"},
)
info = list(r.json()["query"]["pages"].values())[0]["imageinfo"][0]
print(info["width"], "x", info["height"], info["mime"], info["size"], "bytes")
print(info["url"])
