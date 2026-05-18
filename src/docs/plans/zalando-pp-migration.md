# Zalando CR → PP Migration (irisOne QuickConnect)

**Spec:** https://comercus.com/migration.html  
**Status:** IN PROGRESS — Tasks 1–7 done, Task 8 (Upload) blockiert  
**Erstellt:** 2026-05-18  
**Aktualisiert:** 2026-05-18

---

## Hintergrund

Zalando stellt von Connected Retail (CR) auf Partner Program (PP) via irisOne QuickConnect um.
Der bestehende Feed kann weitgehend wiederverwendet werden — Hauptänderungen sind vier neue
Pflichtfelder im CSV und ein neues Dateinamen-Muster.

---

## Designentscheidung: Parallelbetrieb

Der bestehende CR-Feed bleibt **vollständig unverändert** — kein Eingriff in bestehenden Code.
Stattdessen wird der PP-Feed als **zusätzlicher Output** erzeugt:

```
download_feed()
      │
      ▼
save_original_feed()                    (unverändert)
      │
      ▼
pimp_prices()                           (unverändert → schreibt weiterhin media/pimped/ CSV)
      │
      ├──► upload_pimped_feed(          (Signatur um pp_file_name erweitert)
      │         pimped_file_name,
      │         pp_file_name,           ← NEU
      │         ...)
      │         → speichert FeedUpload mit path_to_pp_csv
      │
      └──► generate_pp_feed()           (NEU → schreibt media/zalando_pp/ CSV)
```

Der PP-Feed wird im Media-Verzeichnis `media/zalando_pp/` abgelegt.
In der bestehenden `price_feed.html`-Tabelle erscheint er als zusätzliche Spalte **pp_csv**.
Upload an irisOne erfolgt in einem separaten Schritt (Task 7), sobald Zugangsdaten vorliegen.

---

## Änderungen im Überblick

### Vier neue Spalten im PP-Feed-CSV

| Neue Spalte | Wert |
|---|---|
| `erp_ean` | Kopie von `ean` |
| `erp_article_number` | Kopie von `article_number` |
| `erp_store_article_location` | Kopie von `store_article_location` (darf leer sein) |
| `classification` | Immer `"default"` |

### Dateiname-Muster (nur PP-Feed)

- **PP-Feed:** `import_full_{timestamp}.csv` (Muster `*_full_*.csv`)
- **CR-Feed:** bleibt unverändert (`{timestamp}.csv`)

---

## Implementierungsplan

### Task 1 — `FeedUpload`-Model erweitern
**Datei:** `zalando/models.py`

Neues optionales Feld `path_to_pp_csv` ergänzen:

```python
class FeedUpload(TimeStampedModel):
    ...
    path_to_pp_csv = models.CharField(max_length=128, blank=True, default="")
```

`blank=True` + `default=""` damit bestehende Einträge ohne Migration-Daten gültig bleiben.

---

### Task 2 — Migration erstellen
```bash
uv run python manage.py makemigrations zalando
```
Generierte Migration committen.

---

### Task 3 — Neue Funktion `generate_pp_feed()` in `feed.py`
**Datei:** `zalando/services/feed.py`

Neue Funktion, die den gepimpten Feed als Input nimmt und daraus den PP-Feed erzeugt.

```python
def generate_pp_feed(pimped_file_name):
    """Read pimped feed and write additional PP feed with 4 extra columns."""
    pp_dir = os.path.join(settings.MEDIA_ROOT, "zalando_pp")
    os.makedirs(pp_dir, exist_ok=True)

    pp_file_name = os.path.join(pp_dir, f"import_full_{now_as_str()}.csv")

    with open(pimped_file_name, "r", encoding="UTF8") as f_in:
        reader = csv.reader(f_in, delimiter=";")
        rows = list(reader)

    with open(pp_file_name, "w", encoding="UTF8") as f_out:
        writer = csv.writer(f_out, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        for idx, row in enumerate(rows):
            if idx == 0:
                writer.writerow(row + [
                    "erp_ean", "erp_article_number",
                    "erp_store_article_location", "classification",
                ])
            else:
                # Columns from pimped feed:
                # store(0) ean(1) price(2) retail_price(3) quantity(4)
                # product_number(5) product_name(6) article_number(7)
                # article_color(8) article_size(9) store_article_location(10)
                writer.writerow(row + [
                    row[1],   # erp_ean
                    row[7],   # erp_article_number
                    row[10],  # erp_store_article_location
                    "default",
                ])

    LOG.info(f"PP feed written: {pp_file_name}")
    return pp_file_name
```

---

### Task 4 — `upload_pimped_feed()` um `path_to_pp_csv` erweitern
**Datei:** `zalando/services/feed.py`

Signatur und `FeedUpload`-Erzeugung um das neue Feld ergänzen:

```python
def upload_pimped_feed(pimped_file_name, status_code_validation, dto,
                       validation_result, pp_file_name=""):  # NEU
    ...
    fupload = FeedUpload(
        ...
        path_to_pp_csv=pp_file_name,   # NEU
    )
    fupload.save()
```

Defaultwert `""` hält den bestehenden Test `test_m13_zalando_feed_update` grün.

---

### Task 5 — Management Command erweitern
**Datei:** `zalando/management/commands/m13_zalando_feed_update.py`

`generate_pp_feed()` importieren, aufrufen und Ergebnis an `upload_pimped_feed()` weitergeben:

```python
from zalando.services.feed import (
    download_feed,
    generate_pp_feed,    # NEU
    pimp_prices,
    save_original_feed,
    upload_pimped_feed,
)

# Im handle():
pimped_file_name = pimp_prices(dto.lines)
pp_file_name = generate_pp_feed(pimped_file_name)    # NEU

...

upload_pimped_feed(
    pimped_file_name,
    200,
    dto,
    validation_result,
    pp_file_name,    # NEU
)
```

---

### Task 6 — Template `price_feed.html` erweitern
**Datei:** `zalando/templates/zalando/price_feed.html`

In der bestehenden Tabelle `_last_5_feed_uploadz` eine neue Spalte **pp_csv** nach `pimped_csv`
einfügen:

```html
<!-- Header -->
<th>pp_csv</th>

<!-- Zeile -->
<td>
  {% if f.path_to_pp_csv %}
    <a href="/media/{{ f.path_to_pp_csv|slice:'35:' }}">Link</a>
  {% else %}
    —
  {% endif %}
</td>
```

Ältere `FeedUpload`-Einträge ohne PP-Pfad zeigen `—` statt einem toten Link.

---

### Task 7 — Tests schreiben
**Datei:** `zalando/tests/test_services_feed.py`

Neuen Test `test_generate_pp_feed()` hinzufügen:
- Erzeugt eine temporäre pimped-CSV mit Testdaten (11 Spalten, Semikolon-getrennt)
- Ruft `generate_pp_feed()` auf
- Prüft Output-CSV: 15 Spalten, Header korrekt, `erp_ean == ean`,
  `erp_article_number == article_number`, `erp_store_article_location == store_article_location`,
  `classification == "default"`
- Prüft Dateiname enthält `import_full_`

Bestehende Tests (`test_pimp_prices`, `test_m13_zalando_feed_update`) bleiben **unverändert**.

---

### Task 8 — Upload an irisOne QuickConnect
**Datei:** `zalando/services/feed.py`

Sobald Zugangsdaten vorliegen: neue Funktion `upload_pp_feed(pp_file_name)` nach dem
Muster von `upload_pimped_feed()`. Wird als separater Schritt im Management Command aufgerufen.

**Blockiert durch:** Endpunkt-URLs und Auth-Daten von irisOne/Zalando ausstehend.

---

### Task 9 — Dry-Run & manuelle Abnahme
```bash
uv run python manage.py m13_zalando_feed_update --dry=1
```
Prüfen:
- `media/pimped/` CSV: unverändert (11 Spalten, alter Dateiname ohne `_full_`)
- `media/zalando_pp/` CSV: 15 Spalten, `import_full_*`-Dateiname, korrekte `erp_*`-Werte
- `price_feed.html`: neue Spalte **pp_csv** erscheint mit klickbarem Link

---

## Abhängigkeiten & offene Fragen

| # | Frage | Status |
|---|---|---|
| 1 | Konkrete irisOne QuickConnect Endpunkt-URLs | Ausstehend |
| 2 | Auth-Methode für PP (API Key? OAuth? SFTP?) | Ausstehend |
| 3 | Validation-Endpoint bei PP verfügbar? | Unklar |
| 4 | SFTP nötig (Feed > 10 MB)? | Prüfen |
| 5 | Go-Live-Datum | Ausstehend |

---

## Reihenfolge

Tasks 1–7 können sofort umgesetzt werden (keine externen Abhängigkeiten).  
Task 8 ist blockiert bis Zugangsdaten vorliegen.

```
[x] Task 1  FeedUpload-Model erweitern (path_to_pp_csv)
[x] Task 2  Migration erstellen (0044_feedupload_path_to_pp_csv.py)
[x] Task 3  generate_pp_feed() implementieren
[x] Task 4  upload_pimped_feed() um pp_file_name erweitern
[x] Task 5  Management Command erweitern
[x] Task 6  price_feed.html — neue Spalte pp_csv
[x] Task 7  Tests schreiben (3/3 grün)
[ ] Task 8  Upload an irisOne  ← blockiert
[ ] Task 9  Dry-Run / Abnahme
```
