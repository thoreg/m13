# Zalando OEA — Order Events API Reaktivierung

**Status:** IN PROGRESS — Tasks 1–8 done, Task 9 (Ops) blockiert bis Zalando-Portal-Zugang vorliegt  
**Erstellt:** 2026-05-19  
**Referenz:** https://docs.partner-solutions.zalan.do/en/oea/index.html

---

## Hintergrund

Die OEA-Integration wurde im Sep 2021 vollständig implementiert und im Feb 2024 wieder
deaktiviert (Commit `3856d8a`: „The data was actually never in use"). Dabei wurden nur
die Tests und Fixture-Dateien gelöscht — der Produktivcode blieb erhalten.

Jetzt soll die Integration reaktiviert und für den PP-Betrieb ertüchtigt werden.

---

## Payload-Struktur (aus Git-Historie rekonstruiert)

### Assigned
```python
{
    'event_id': '215bcb87-...',
    'order_id': '478d3ff7-...',
    'order_number': '10103350851695',
    'state': 'assigned',
    'store_id': '001',
    'timestamp': '2021-09-15T09:09:28.221195Z',
    'items': [{
        'article_location': 'Manufaktur13 - Chop Shop',
        'article_number': 'NECKW-NA',
        'currency': 'EUR',
        'ean': '0781491971467',
        'item_id': 'b634ddef-...',
        'price': 24.95,
        'zalando_article_number': 'MGQ54G005-K110ONE000'
    }]
}
```

### Fulfilled
```python
{
    'event_id': '70947cfd-...',
    'order_id': '478d3ff7-...',
    'order_number': '10103350851622',
    'state': 'fulfilled',
    'store_id': '001',
    'timestamp': '2021-09-16T06:21:39.390060Z',
    'customer_billing_address': {
        'address_line_1': 'Am Anger 28 b',
        'city': 'Eichstätt',
        'country_code': 'DE',
        'first_name': 'R.',
        'last_name': 'K.',
        'zip_code': '85072'
    },
    'delivery_details': {
        'delivery_carrier_name': 'DHL_DE',
        'delivery_tracking_number': '00340414644694802419',
        'return_carrier_name': 'DHL_DE',
        'return_tracking_number': '00340414644694802419',
    },
    'items': [{ ... }]
}
```

### Cancelled / Returned
Erwartete Struktur analog zu `assigned` — kein `delivery_details`, `return_location`
möglicherweise vorhanden bei `returned` (Werte: `"STORE"` oder `"ZALANDO"`).

---

## Bekannte Bugs im bestehenden Code

### Bug 1 — Status-Case-Mismatch (kritisch)
**Datei:** `zalando/services/orders.py:168`

Zalando sendet `state` in Kleinbuchstaben (`"assigned"`, `"fulfilled"`, …).
Das `Order.Status`-Enum erwartet Großbuchstaben (`"ASSIGNED"`, `"FULFILLED"`, …).

```python
# Aktuell (falsch):
order.status = entry["state"]            # speichert "fulfilled" → ungültig

# Fix:
order.status = entry["state"].upper()    # speichert "FULFILLED" → gültig
```

Betrifft alle `Order.objects.get_or_create()`-Calls und alle direkten Assignments.

### Bug 2 — `cancelled` und `returned` werden nicht als processed markiert
**Datei:** `zalando/services/orders.py`

Wenn `state == "cancelled"` oder `state == "returned"`, läuft der Code in den
`delivery_details`-Check, der `mlog.error` schreibt, aber **nie `mark_as_processed()`
aufruft**. Resultat: diese Messages werden bei jedem Lauf erneut verarbeitet
(Endlosschleife).

---

## Implementierungsplan

### Task 1 — URL einkommentieren
**Datei:** `zalando/urls.py:8`

```python
# Vorher:
# path("oea/", views.oea_webhook, name="zalando_oea_webhook"),

# Nachher:
path("oea/", views.oea_webhook, name="zalando_oea_webhook"),
```

Erreichbar danach unter: `https://m13.thoreg.org/z/oea/`

---

### Task 2 — `process_oea_webhook_payload` verdrahten
**Datei:** `zalando/views.py:125–127`

Den Stub mit `process_new_oea_records()` verbinden:

```python
# Import ergänzen:
from zalando.services.orders import process_new_oea_records

@atomic
def process_oea_webhook_payload(payload):
    LOG.info(payload)
    process_new_oea_records()
```

`process_new_oea_records()` verarbeitet alle unprocessed `OEAWebhookMessage`-Einträge
aus der DB — also auch die gerade gespeicherte Nachricht. Synchron im Request-Kontext
ist akzeptabel, da der Operationsaufwand gering ist.

---

### Task 3 — Status-Normalisierung in `process_new_oea_records()`
**Datei:** `zalando/services/orders.py`

An allen drei Stellen, wo `entry["state"]` verwendet wird:

```python
state = entry["state"].upper()   # "fulfilled" → "FULFILLED"

# get_or_create defaults:
"status": state,

# Update nach get_or_create:
order.status = state
```

---

### Task 4 — `cancelled` und `returned` korrekt behandeln
**Datei:** `zalando/services/orders.py`

Nach dem `assigned`-Early-Return-Block einen zweiten Block einfügen:

```python
if order.status in ("CANCELLED", "RETURNED"):
    LOG.info(f"\t\tstatus is {order.status} - mark as processed and continue")
    order.save()
    mark_as_processed(oea_msg)
    continue
```

Damit werden diese Zustände sauber persistiert und nicht endlos re-prozessiert.
Eine tiefere Geschäftslogik (z.B. Lagerbestand-Rückbuchung) kann später ergänzt werden.

---

### Task 5 — Management Command erstellen
**Datei:** `zalando/management/commands/m13_zalando_process_oea_messages.py`

Für manuelle Nachverarbeitung und optionalen Cron-Betrieb:

```python
from django.core.management.base import BaseCommand
from zalando.services.orders import process_new_oea_records

class Command(BaseCommand):
    help = "Process unprocessed OEA webhook messages."

    def handle(self, *args, **options):
        process_new_oea_records()
```

Aufruf: `uv run python manage.py m13_zalando_process_oea_messages`

---

### Task 6 — Fixture wiederherstellen
**Datei:** `zalando/tests/fixtures/oea-msgs-small.fixture.json`

Die Fixture wurde in Commit `3856d8a` gelöscht. Sie muss manuell als JSON neu erstellt
werden mit repräsentativen Testdaten:

- 2× `assigned`-Events (unterschiedliche `order_id`)
- 2× `fulfilled`-Events (je mit `delivery_details` + `customer_billing_address`)
- 1× `cancelled`-Event
- 1× `returned`-Event

Format: Django-Fixture für `zalando.OEAWebhookMessage` mit `payload` als JSONField
und `processed = null`.

```json
[
  {
    "model": "zalando.oeawebhookmessage",
    "pk": 1,
    "fields": {
      "created": "2021-09-15T09:09:28Z",
      "modified": "2021-09-15T09:09:28Z",
      "processed": null,
      "payload": {
        "event_id": "aaa-111",
        "order_id": "order-001",
        "order_number": "10100000000001",
        "state": "assigned",
        "store_id": "001",
        "timestamp": "2021-09-15T09:09:28.000000Z",
        "items": [{"item_id": "item-001", "ean": "0781491971467",
                   "article_number": "TEST-001", "currency": "EUR",
                   "price": 24.95, "article_location": "M13"}]
      }
    }
  }
  // ... weitere Einträge
]
```

---

### Task 7 — Tests wiederherstellen
**Datei:** `zalando/tests/test_orders.py`

Drei Tests, analog zur gelöschten Version (Commit `2ecf578` + `9fbe8f7`):

```python
@pytest.mark.django_db
def test_process_new_oea_records_assigned():
    """assigned-Events erzeugen Order, kein OrderItem."""
    OEAWebhookMessage.objects.all().delete()
    call_command('loaddata', 'zalando/tests/fixtures/oea-msgs-small.fixture.json')
    process_new_oea_records()
    assert Order.objects.filter(status="ASSIGNED").count() == 2
    assert OrderItem.objects.all().count() == 0

@pytest.mark.django_db
def test_process_new_oea_records_fulfilled():
    """fulfilled-Events erzeugen Order + OrderItem + Address."""
    ...
    assert Order.objects.filter(status="FULFILLED").count() == 2
    assert OrderItem.objects.all().count() >= 2
    assert Address.objects.all().count() >= 2

@pytest.mark.django_db
def test_process_new_oea_records_cancelled_returned():
    """cancelled/returned werden korrekt als processed markiert."""
    ...
    assert OEAWebhookMessage.objects.filter(processed=None).count() == 0
```

Alle `OEAWebhookMessage`-Einträge müssen nach `process_new_oea_records()` den
`processed`-Timestamp gesetzt haben.

---

### Task 8 — Admin registrieren
**Datei:** `zalando/admin.py`

```python
from zalando.models import OEAWebhookMessage

@admin.register(OEAWebhookMessage)
class OEAWebhookMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "processed")
    list_filter = ("processed",)
    readonly_fields = ("payload", "created", "modified", "processed")
```

Ermöglicht Ops-Debugging direkt im Django Admin.

---

### Task 9 — Ops: Env-Variable + Zalando-Registrierung
**Kein Code — Infrastruktur-Schritt**

1. Token generieren: `python -c "import secrets; print(secrets.token_hex(32))"`
2. In Produktion setzen: `M13_ZALANDO_OEM_WEBHOOK_TOKEN=<token>`
3. Bei Zalando/irisOne registrieren:
   - Webhook-URL: `https://m13.thoreg.org/z/oea/`
   - Header: `x-api-key: <token>`

**Blockiert durch:** Zalando/irisOne Portal-Zugang erforderlich.

---

### Task 10 — Dry-Run & Abnahme
```bash
# Tests laufen lassen
uv run pytest --import-mode=importlib --ds=m13.config.develop zalando/tests/test_orders.py -v

# Manuell testen (curl mit falschem Token → 403 erwartet)
curl -X POST https://m13.thoreg.org/z/oea/ \
     -H "x-api-key: wrong" \
     -H "Content-Type: application/json" \
     -d '{"state":"assigned"}'

# Manuell testen (curl mit korrektem Token → 200 erwartet)
curl -X POST https://m13.thoreg.org/z/oea/ \
     -H "x-api-key: <token>" \
     -H "Content-Type: application/json" \
     -d '<assigned-payload>'

# Admin prüfen: /addi/zalando/oeawebhookmessage/
```

---

## Abhängigkeiten & offene Fragen

| # | Frage | Status |
|---|---|---|
| 1 | Zalando/irisOne Portal-Zugang für Webhook-Registrierung | Ausstehend |
| 2 | Welche `state`-Werte schickt PP (gleich wie CR: `assigned`, `fulfilled`, …)? | Zu bestätigen |
| 3 | Soll `returned` Lagerbestand rückbuchen? | Offen |
| 4 | Soll `cancelled` eine Benachrichtigung triggern? | Offen |
| 5 | Retention-Policy für `OEAWebhookMessage` (aktuell: 365 Tage) | OK |

---

## Reihenfolge

Tasks 1–8 können sofort umgesetzt werden (kein externer Zugang nötig).  
Task 9 ist blockiert bis Zalando-Portal-Zugang vorliegt.

```
[x] Task 1   URL einkommentieren (urls.py)
[x] Task 2   process_oea_webhook_payload verdrahten (views.py)
[x] Task 3   Status-Normalisierung uppercase (services/orders.py)
[x] Task 4   cancelled/returned korrekt behandeln (services/orders.py)
[x] Task 5   Management Command m13_zalando_process_oea_messages
[x] Task 6   Fixture oea-msgs-small.fixture.json wiederherstellen
[x] Task 7   Tests test_orders.py wiederherstellen (3/3 grün)
[x] Task 8   Admin-Registrierung OEAWebhookMessage
[ ] Task 9   Ops: Env-Variable + Zalando-Registrierung  ← blockiert
[ ] Task 10  Dry-Run & Abnahme
```
