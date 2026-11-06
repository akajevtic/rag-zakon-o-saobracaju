import urllib.request
from html.parser import HTMLParser

URL = "https://www.paragraf.rs/propisi/zakon_o_bezbednosti_saobracaja_na_putevima.html"

class ZakonParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pasusi = []
        self.klasa = None

    def handle_starttag(self,tag,attrs):
        if tag == "p":
            self.klasa = dict(attrs).get("class")
            self.pasusi.append([self.klasa,""])

    def handle_endtag(self,tag):
        if tag == "p":
            self.klasa = None

    def handle_data(self,data):
        if self.klasa in ("clan", "normal"):
            self.pasusi[-1][1] += data

zahtev = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(zahtev).read().decode("utf-8")

parser = ZakonParser()
parser.feed(html)

redovi = []
for klasa, tekst in parser.pasusi:
    if klasa == "samostalni":
        break
    tekst = " ".join(tekst.split())

    if not tekst:
        continue
    if klasa == "clan":
        redovi.append("")
    redovi.append(tekst)

with open("zakon.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(redovi))

print("Clanova:", sum(1 for r in redovi if r.startswith("Član ")))
print("Redova teksta: ",len(redovi))

    