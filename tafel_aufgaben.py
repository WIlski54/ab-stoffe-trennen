"""Aufgaben des Arbeitsblatts für die digitale Tafel (Server-Adapter).

Diese Datei gehört zum INHALT des Arbeitsblatts (wie templates/ab_inhalt.html): Wer ein neues AB
baut, ändert hier die Tafel-Fassungen. Die Lösungen bleiben auf dem Server und gehen nie an die
Schüler:innen.

Zwei Dinge sind hier beschrieben:
1. VARIANTEN      – die leeren Tafel-Aufgaben (eine Fassung je Aufgabe) samt Lösung, die live gelöst werden.
                    Das ist der EINZIGE Teil, der für ein neues Arbeitsblatt neu geschrieben wird.
2. AbAdapter      – inhaltsunabhängig: liest die AB-Antworten und füllt damit die Tafel-Aufgaben vor.
                    Regel: Tafel-Feld k einer Aufgabe N = AB-Eingabefeld a<N>.f<k> (Reihenfolge in ab_inhalt.html).
"""
import json

from tafel.aufgaben import feld_ids, zelle

# Es gibt bewusst nur EINE Fassung je Aufgabe (keine Niveaus A/B/C). Die Tafel braucht aber einen Schlüssel
# für den Knopf in der Aufgabenliste; er steht nur dort (Knopftext) und erscheint nicht auf der Tafel.
KNOPF = "an die Tafel"

# ---------- Tafel-Fassungen (leer + Lösung) ----------
# lueckentext: teile (None = Lücke), loesung je Lücke (Liste akzeptierter Antworten), wortbank
# zuordnung:   links (Zeilen), optionen, loesung {zeile: option}
# mc:          frage, optionen, loesung
# richtigfalsch: aussagen [(Text, "richtig"|"falsch")]
# freitext:    frage
def _schalen(*zahlen):
    """„2,1“ darf auch als „2 1“, „2-1“, „2/1“ … geschrieben werden."""
    return [t.join(str(z) for z in zahlen) for t in (",", ", ", " ", "-", "/", ";", "|", ".")]


# Die Tafel-Fassungen entsprechen dem AB (gleiche Felder, gleiche Reihenfolge wie in ab_inhalt.html): Was eine Person
# im AB eingetragen hat, steht an der Tafel schon in den Feldern und lässt sich dort bearbeiten – je Aufgabe passend:
#   tabelle (Aufgabe 1, 2, 3) · lueckentext (4) · freitext (5)
# tabelle: spalten, breiten (Gewichte), zeilen = Zellen: str = fester Text, "F" = Eingabefeld, "Z" = Zifferneingabe,
#          "H" = Ankreuzfeld; Felder heißen c0, c1, … in Lesereihenfolge (wie die Eingabefelder im AB).
VARIANTEN = {
    "1": {"titel": "Aufgabe 1 · Reinstoff oder Gemisch?", "typ": "tabelle",
          "frage": "Kreuze an, ob es sich um einen Reinstoff oder um ein Gemisch handelt.",
          "spalten": ["Stoff", "Reinstoff", "Gemisch"], "breiten": [2.4, 1, 1],
          "zeilen": [["Salzwasser", "H", "H"], ["Kochsalz", "H", "H"], ["Müsli", "H", "H"],
                     ["destilliertes Wasser", "H", "H"]],
          "loesung": [["false"], ["true"], ["true"], ["false"], ["false"], ["true"], ["true"], ["false"]]},
    "2": {"titel": "Aufgabe 2 · Trennen im Alltag", "typ": "tabelle",
          "frage": "Ordne jedem Gemisch das passende Trennverfahren zu.",
          "spalten": ["Gemisch", "Trennverfahren"], "breiten": [1.6, 1.4],
          "zeilen": [["Nudeln und Kochwasser", "F"], ["Kaffeepulver und Kaffee", "F"],
                     ["Meerwasser (Salz gewinnen)", "F"], ["Eisennägel im Sand", "F"]],
          "loesung": [["Abgießen", "Abgiessen", "Sieben", "Absieben", "Dekantieren", "abschütten"],
                      ["Filtrieren", "Filtern", "Filtration", "Abfiltrieren"],
                      ["Eindampfen", "Verdampfen", "Verdunsten", "Eindunsten", "Abdampfen"],
                      ["Magnettrennung", "Magnetscheiden", "Magnetscheidung", "Magnet", "mit einem Magneten",
                       "mit Magnet", "Magnetisieren"]]},
    "3": {"titel": "Aufgabe 3 · Salz aus dem Sand holen", "typ": "tabelle",
          "frage": "Tom möchte das Salz aus seinem Salz-Sand-Gemisch zurückgewinnen. Nummeriere die Arbeitsschritte.",
          "spalten": ["Arbeitsschritt", "Nr."], "breiten": [4, 1],
          "zeilen": [["Das Gemisch filtrieren", "Z"], ["Gemisch in ein Becherglas mit Wasser geben", "Z"],
                     ["Das Filtrat eindampfen", "Z"], ["Umrühren, bis sich das Salz gelöst hat", "Z"]],
          "loesung": [["3"], ["1"], ["4"], ["2"]]},
    "4": {"titel": "Aufgabe 4 · Fachbegriffe", "typ": "lueckentext",
          "teile": ["Beim Filtrieren bleibt der Sand als ", None, " im Filter zurück. Die klare Flüssigkeit, die durch "
                    "den Filter läuft, heißt ", None, ". Das Salz ist im Wasser ", None,
                    " und passt deshalb durch den Filter. Beim ", None,
                    " verdampft das Wasser und das Salz bleibt zurück."],
          "loesung": [["Rückstand", "Filterrückstand"], ["Filtrat"], ["gelöst", "aufgelöst"],
                      ["Eindampfen", "Verdampfen", "Erhitzen"]],
          "wortbank": ["Rückstand", "Filtrat", "gelöst", "Eindampfen", "Sieben", "geschmolzen"]},
    "5": {"titel": "Aufgabe 5 · Lenas Versuch", "typ": "freitext",
          "frage": "Lena schüttet das trockene Salz-Sand-Gemisch direkt in den Filter. Unten kommt nichts heraus, und "
                   "das Salz bleibt beim Sand. Erkläre, was Lena falsch gemacht hat und warum man für die Trennung "
                   "Wasser braucht."},
}


def _gemischt(liste):
    """Feste, aber nicht triviale Reihenfolge (die Lösung soll nicht einfach dastehen)."""
    return sorted(liste, key=lambda t: (len(t) * 7 + sum(map(ord, t))) % 11)


def aufgabenliste():
    return [{"aufgabe_id": nr, "titel": v["titel"], "typ": v["typ"],
             "niveaus": [KNOPF]} for nr, v in VARIANTEN.items()]


def aufgabe_leer(aufgabe_id, niveau):
    f = VARIANTEN.get(aufgabe_id)
    if f is None or niveau != KNOPF:
        return None
    typ = f["typ"]
    daten = {"aufgabe_id": aufgabe_id, "niveau": "", "titel": f["titel"], "aufgabentyp": typ}
    if typ == "lueckentext":
        teile, n = [], 0
        for teil in f["teile"]:
            if teil is None:
                teile.append({"feld": f"l{n}"})
                n += 1
            else:
                teile.append({"text": teil})
        daten.update(teile=teile, wortbank=list(f["wortbank"]))
    elif typ == "zuordnung":
        daten.update(zeilen=[{"feld": f"z{i}", "text": t} for i, t in enumerate(f["links"])],
                     optionen=list(f["optionen"]))
    elif typ == "tabelle":
        n, zeilen = 0, []
        for zeile in f["zeilen"]:
            neu = []
            for z in zeile:
                if z in ("F", "Z", "H"):
                    zelle = {"feld": f"c{n}"}
                    n += 1
                    if z == "H":
                        zelle["art"] = "haken"
                    if z == "Z":
                        zelle["zahl"] = True
                    neu.append(zelle)
                else:
                    neu.append({"text": z})
            zeilen.append(neu)
        daten.update(frage=f.get("frage", ""), spalten=list(f["spalten"]),
                     breiten=list(f.get("breiten", [])), zeilen=zeilen, kartenbreite=700)
        if f.get("schrift"):
            daten["schrift"] = f["schrift"]
    elif typ == "schalen":
        daten.update(frage=f["frage"], kern=f["kern"], kartenbreite=640)
    elif typ == "mc":
        daten.update(frage=f["frage"], optionen=list(f["optionen"]))
    elif typ == "richtigfalsch":
        daten.update(aussagen=[{"feld": f"r{i}", "text": t} for i, (t, _) in enumerate(f["aussagen"])])
    else:
        daten.update(frage=f["frage"])
    return daten


def loesung(aufgabe_id, niveau):
    f = VARIANTEN.get(aufgabe_id)
    if f is None or f["typ"] == "freitext":
        return None
    typ = f["typ"]
    if typ == "lueckentext":
        return {f"l{i}": list(alt) for i, alt in enumerate(f["loesung"])}
    if typ == "tabelle":
        return {f"c{i}": list(alt) for i, alt in enumerate(f["loesung"])}
    if typ == "schalen":
        return {f"s{i}": list(alt) for i, alt in enumerate(f["loesung"])}
    if typ == "zuordnung":
        return {f"z{i}": [f["loesung"][t]] for i, t in enumerate(f["links"])}
    if typ == "mc":
        return {"wahl": [f["loesung"]]}
    if typ == "richtigfalsch":
        return {f"r{i}": [u] for i, (_, u) in enumerate(f["aussagen"])}
    return None


# ---------- Antworten aus dem AB (Karten und vorbelegte Tafel-Aufgaben) ----------
# Dieser Teil ist INHALTSUNABHÄNGIG – er liest nur VARIANTEN. Regel: Die Felder einer Tafel-Aufgabe stehen in derselben
# Reihenfolge wie die Eingabefelder (input/textarea) dieser Aufgabe in ab_inhalt.html (AB-Feld a<N>.f<k> = k-tes Tafel-Feld).
# Sonderfälle: Schalenmodell (typ "schalen") liest das Widget a<N>.w1, Freitext (typ "freitext") das Feld a<N>.f1.
class _Anonym:
    id, name, ist_lehrer = "", "", False


class AbAdapter:
    """Liest die Antworten einer Person aus der Tabelle `antworten` und liefert sie als Tafel-Karten bzw. Tafel-Aufgaben."""

    def __init__(self, get_db, anzahl_aufgaben):
        self.get_db = get_db
        self.anzahl = anzahl_aufgaben

    # ----- Tafel-Seite (leere Aufgaben, Lösungen) -----
    def aufgabenliste(self):
        return aufgabenliste()

    def aufgabe_leer(self, aufgabe_id, niveau):
        return aufgabe_leer(aufgabe_id, niveau)

    def loesung(self, aufgabe_id, niveau):
        return loesung(aufgabe_id, niveau)

    def niveau_des_schuelers(self, schueler_id, aufgabe_id):
        return KNOPF

    # ----- Antworten der Schüler:innen -----
    def _felder(self, schueler_id):
        db = self.get_db()
        try:
            return {r[0]: r[1] for r in db.execute(
                "SELECT feld, wert FROM antworten WHERE schueler_id=?", (schueler_id,)).fetchall()}
        finally:
            db.close()

    @staticmethod
    def _schalen(felder, nr):
        """Elektronen je Schale aus dem Schalenmodell-Widget des ABs (Punkte {r: Schale, w: Winkel})."""
        try:
            punkte = json.loads(felder.get(f"a{nr}.w1") or "[]")
        except ValueError:
            punkte = []
        zaehler = [0, 0, 0]
        for p in punkte if isinstance(punkte, list) else []:
            if isinstance(p, dict) and isinstance(p.get("r"), int) and 0 <= p["r"] < 3:
                zaehler[p["r"]] += 1
        return zaehler

    def aufgabe_befuellt(self, schueler_id, aufgabe_id, person):
        """Die Tafel-Aufgabe, in der schon steht, was die Person im AB eingetragen hat (None, wenn es keine
        Tafel-Fassung gibt). Die Felder bleiben an der Tafel bearbeitbar."""
        nr = str(aufgabe_id)
        objekt = aufgabe_leer(nr, KNOPF)
        if objekt is None:
            return None
        felder = self._felder(schueler_id)
        typ = objekt["aufgabentyp"]
        vorhanden = {}
        if typ == "schalen":
            for k, n in enumerate(self._schalen(felder, nr)):
                if n:
                    vorhanden[f"s{k}"] = str(min(n, 18))
        elif typ == "freitext":
            wert = (felder.get(f"a{nr}.f1") or "").strip()
            if wert:
                vorhanden["text"] = wert[:2000]
        else:                                                        # Lückentext, Tabelle, …: Feld k = AB-Feld k
            for k, fid in enumerate(feld_ids(objekt), start=1):
                wert = (felder.get(f"a{nr}.f{k}") or "").strip()
                if zelle(objekt, fid).get("art") == "haken":         # Ankreuzfeld: nur „angekreuzt“ übernehmen
                    wert = "true" if wert == "true" else ""
                elif wert == "false":
                    wert = ""
                if wert:
                    vorhanden[fid] = wert[:60]
        objekt["felder"] = {k: {"wert": w, "von_id": person.id, "von": person.name, "status": None, "alt": None}
                            for k, w in vorhanden.items()}
        objekt["quelle"] = schueler_id
        return objekt

    @staticmethod
    def _karte_inhalt(o):
        """Antwort als Karte (Lückentext → Segmente, Tabelle → Zeilenpaare, sonst Text)."""
        wert = lambda fid: ((o.get("felder") or {}).get(fid) or {}).get("wert", "")  # noqa: E731
        typ = o["aufgabentyp"]
        if typ == "lueckentext":
            return "lueckentext", {"segmente": [{"luecke": wert(t["feld"]) or "…"} if "feld" in t else {"text": t["text"]}
                                                 for t in o["teile"]]}
        if typ == "tabelle":
            def zeige(z):
                if "feld" not in z:
                    return z.get("text", "")
                w = wert(z["feld"])
                return ("✓" if w == "true" else "–") if z.get("art") == "haken" else (w or "…")
            paare = []
            for zeile in o["zeilen"]:
                if zeile and "feld" not in zeile[0]:
                    paare.append([zeile[0]["text"], " · ".join(zeige(z) for z in zeile[1:])])
                else:
                    paare += [[(o["spalten"][i] if i < len(o["spalten"]) else ""), zeige(z)] for i, z in enumerate(zeile)]
            return "zuordnung", {"paare": paare}
        if typ == "schalen":
            n = [int(wert(f"s{k}") or 0) for k in range(3)]
            return "freitext", {"text": f"{sum(n)} Elektronen gesetzt (" + " · ".join(f"Schale {k + 1}: {x}" for k, x in enumerate(n)) + ")"}
        return "freitext", {"text": wert("text") or "…"}

    def aufgaben_des_schuelers(self, schueler_id):
        ergebnis = []
        for nr, v in VARIANTEN.items():
            o = self.aufgabe_befuellt(schueler_id, nr, _Anonym)
            typ, inhalt = self._karte_inhalt(o)
            ergebnis.append({"aufgabe_id": nr, "titel": v["titel"], "typ": typ, "niveau": "",
                             "bearbeitet": bool(o["felder"]), "inhalt": inhalt})
        return ergebnis

    def aufgabe_des_schuelers(self, schueler_id, aufgabe_id):
        return next((a for a in self.aufgaben_des_schuelers(schueler_id) if a["aufgabe_id"] == str(aufgabe_id)), None)
