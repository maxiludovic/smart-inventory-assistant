# 📦 Smart Inventory Assistant

Eine REST-API zur **Lagerverwaltung für kleine Händler**, gebaut mit **Python, Flask und SQLite**.
Händler können Produkte anlegen, Wareneingänge und Verkäufe buchen und sehen sofort,
welche Artikel nachbestellt werden müssen.

> Status: **MVP**, die Kernfunktionen laufen und sind mit 13 automatischen Tests abgesichert.

---

## ✨ Funktionen

- **Produkte verwalten:** anlegen, auflisten, einzeln abrufen (mit Eingabevalidierung)
- **Lagerbewegungen buchen:** Wareneingang (`+10`) und Entnahme (`-3`)
- **Kein negativer Bestand:** die Prüfung ist direkt im SQL-`UPDATE` und damit atomar
- **Historie:** jede Bewegung wird mit Grund und Zeitstempel gespeichert
- **Nachbestell-Alarm:** `GET /products/low-stock` zeigt alle Artikel unter dem Meldebestand, das größte Defizit zuerst

---

## 🔌 API-Endpunkte

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/health` | Status der API |
| `GET` | `/products` | Alle Produkte |
| `POST` | `/products` | Produkt anlegen |
| `GET` | `/products/<id>` | Ein Produkt |
| `POST` | `/products/<id>/stock` | Bestand ändern (`{"change": -3, "reason": "Verkauf"}`) |
| `GET` | `/products/<id>/movements` | Historie der Lagerbewegungen |
| `GET` | `/products/low-stock` | Produkte, die nachbestellt werden sollten |

**Beispiel: Produkt anlegen**
```bash
curl -X POST http://127.0.0.1:5000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Reis 1kg", "sku": "REIS-1", "quantity": 10, "min_quantity": 3, "price": "2.49"}'
```
```json
{"id": 1, "name": "Reis 1kg", "sku": "REIS-1", "quantity": 10, "min_quantity": 3, "price": "2.49"}
```

**Fehlercodes:** `400` ungültige Eingabe oder zu wenig Bestand · `404` Produkt nicht gefunden · `409` SKU existiert bereits

---

## 🧠 Technische Entscheidungen

| Entscheidung | Warum |
|---|---|
| **Preise in Cent** (`INTEGER`) | Fließkommazahlen sind ungenau (`0.1 + 0.2 ≠ 0.3`), Ganzzahlen nicht |
| **Prüfung im SQL-`UPDATE`** (`WHERE quantity + ? >= 0`) | Prüfen und Ändern sind eine atomare Operation, sicher auch bei gleichzeitigen Verkäufen |
| **Transaktion mit `rollback()`** | Bestand und Historie bleiben konsistent: alles oder nichts |
| **Platzhalter `?` in allen SQL-Abfragen** | Schutz vor SQL-Injection |
| **Reines SQL mit `sqlite3`** statt ORM | Volle Kontrolle und Transparenz über jede Abfrage |
| **Application Factory** (`create_app`) | Saubere Trennung, jeder Test bekommt eine eigene leere Datenbank |

---

## 📁 Projektstruktur

```
smartInventoryAssistant/
├── app/
│   ├── __init__.py        # create_app(): Konfiguration, Routen, /health
│   ├── db.py              # Datenbankverbindung pro Anfrage
│   ├── schema.sql         # Tabellen products und stock_movements
│   ├── models/
│   │   ├── product.py     # SQL für Produkte und Nachbestell-Liste
│   │   └── stock.py       # Lagerbewegungen in einer Transaktion
│   └── routes/
│       └── products.py    # HTTP-Endpunkte und Validierung
├── tests/                 # 13 pytest-Tests
├── run.py                 # Startpunkt
└── requirements.txt
```

---

## ▶️ Installation und Start

```bash
git clone https://github.com/maxiludovic/smart-inventory-assistant.git
cd smart-inventory-assistant
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt

python run.py                  # API läuft auf http://127.0.0.1:5000
python -m pytest -v            # Tests ausführen
```

---

## 🗺️ Roadmap

- [ ] Produkte bearbeiten und löschen (`PUT` / `DELETE`)
- [ ] PostgreSQL statt SQLite (Vorbereitung in `docker-compose.yml`)
- [ ] Authentifizierung für mehrere Händler
- [ ] Docker-Image und CI mit GitHub Actions
- [ ] Deployment auf Microsoft Azure
- [ ] Bestellvorschläge auf Basis des Verkaufsverlaufs

---

## 🤖 Entwicklung

Entwickelt mit KI-Unterstützung (Claude). Jeden Schritt habe ich selbst ausgeführt, getestet
und nachvollzogen, die technischen Entscheidungen oben kann ich im Detail erklären.

**Ludovic Tankeu Kepka** · [GitHub](https://github.com/maxiludovic) · [LinkedIn](https://www.linkedin.com/in/ludovic-tankeu-9b5361199)
