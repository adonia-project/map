import json, urllib.request, urllib.parse
UA = "Takeru-Sync/1.0 (Letta Code; talod.miraheze.org)"
API = "https://talod.miraheze.org/w/api.php"
req = urllib.request.Request(API + "?" + urllib.parse.urlencode(
    {"action":"query","prop":"revisions","titles":"Kaftia","rvprop":"content","format":"json"}),
    headers={"User-Agent": UA})
r = json.loads(urllib.request.urlopen(req).read().decode())
text = list(r["query"]["pages"].values())[0]["revisions"][0]["*"]
lines = [l for l in text.split("\n") if "{{flag|" in l]
print("flag rows:", len(lines))
for l in lines[:3]:
    print(repr(l[:400]))
    print("CELLS:", [c.strip()[:40] for c in l.split("||")][:8])
    print("=====")
