# MASTER PROMPT — Omni Super Engine v8.2 & Aorta und Brain Cleaner Architektur

> **Zweck dieses Dokuments:** Ein wiederverwendbarer, vollständiger Kontext-Prompt für jede Fortsetzung, Refaktorierung, UI-Arbeit oder Integration.  
> **Sprache:** Deutsch mit dem Nutzer; Code und technische Identifier Englisch.  
> **Stand:** konsolidiertes Master-Archiv (Lineage + Codes + Testdaten).

---

## 1. Projektidentität

Es gibt **zwei** klar getrennte Produktlinien — Namen nicht vermischen:

| Name | Rolle |
|------|--------|
| **Omni Super Engine v8.2** (Core 8) | Generischer quantum-topologischer Physik-Core + Multi-Screen Workbench |
| **Aorta und Brain Cleaner Architektur** | Hämodynamischer Digital Twin (zerebrale + aortale Monte-Carlo-Kernel, Live-Monitor) |

Kein „Omni“-Branding für Aorta/Brain-Artefakte. ZIP- und UI-Titel strikt trennen.

---

## 2. Omni Super Engine v8.2 — Kernauftrag

### 2.1 Engine

- Modul: `SuperEngineOmniCore8Master` in `omni_super_engine_v8_2.py`
- Dimension konfigurierbar (Default 20), Seed konfigurierbar
- Jeder Zyklus: `execute_evolution_cycle(physics_mode, **kwargs)` → Residual, `symplectic_determinant` (Ziel ≈ 1.0), Status, `state_snapshot`
- **Physics Modes:** `standard` | `omega_key` | `navier_stokes` | `ziolkowski` | `path_integral` | `adaptive` | `topology` | `full_v8`
- Module: EnvironmentCarrier (Base-Freq **98.112 Hz**), OmniPhysicsBridge (Symplektik, Omega_key, NS, Ziolkowski), PathIntegralMonitor (PIMC), AdaptiveHyperController (α / freq_scale), HolographicTopologyAnalyzer (Betti/Defect), TensorAccelerationLayer (Laplace/FFT, Torch optional)
- Float64 wo relevant; unbekannte Modes → Fallback `standard` mit klarem Status
- Zero-Dependency-Backend bevorzugt (stdlib `http.server`); NumPy Pflicht; Torch/SciPy optional

### 2.2 Dashboard (5 Screens)

1. **Workbench** — freies Problem-/Gleichungsfeld, **KI-Parse** (Text → Mode/Dimension/State), Datei-Upload (PDF, MD, TXT, JSON, PY, CSV), Parameter, Schnellmodi, KPI
2. **Telemetrie** — Live-Stream + Zyklus-Historie
3. **Phasenraum** — **zwei getrennte** 4D-Phasenräume (A: State/Gradient, B: symplektische Orbit), animierter Kopf, det(J) / Pulse Head
4. **Diagramme** — Residual, det(J), Wall-Time, Status-Verteilung
5. **Ergebnisse** — JSON-Ansicht, Kopieren, Session-Export (Download)

UI: dunkles High-Tech-Theme (Cyan/Amber/Violet auf Navy), monospace für Metriken, klar getrennte Panels — nicht überladen, nicht „Omni Super Engine“-Alt-Workbench-Layout.

### 2.3 API (Minimal)

```
GET  /api/health | /api/telemetry | /api/history | /api/last | /api/context
POST /api/cycle | /api/batch | /api/upload | /api/ai-parse | /api/export | /api/reset
```

Upload + KI-Parse müssen Problemstellungen aus Freitext und Dateien extrahieren (Mode, Dimension, Seed, State, Gleichungen).

---

## 3. Aorta und Brain Cleaner Architektur — Kernauftrag

### 3.1 Kernel (vektorisiert, NumPy)

- `execute_brain_clean_bulk_simulation` — FDA WSS-Cap **20 Pa**, Nitinol-EPD, thermische Last, Residual Λ
- `execute_aortic_bulk_simulation` — FDA WSS-Cap **30 Pa**, Flow-Twin, symplektische Volumenkorrektur
- Bulk: 50k–100k Cases, Gamma-Verteilungen, Success-Rate, Max-WSS, Residual ≤ ~1e-10 Ziel
- `common_utils`: Report-Builder, Caps, Residual-Generator
- Keine Bewertung des medizinischen Inhalts; nur technische Korrektheit und Performance

### 3.2 Monitoring-UI

- Live-Telemetrie-Stream
- Live-Metriken (Success, Max WSS, ΔT, Residual)
- Anatomische Zonen: **Brain Clean Zone** (neuronales/vaskuläres Netz, EPD) und **Aorta Clean Zone** (Aortenbogen, Flow-Jet, WSS) — präzise, high-tech, an 4D-Flow-MRI / Gefäß- und Neural-Referenzen angelehnt
- Optional: 4D-Phasenraum-Visualisierung im gleichen Stil wie Omni-Referenzanimationen (cyan Punkt, farbige Trajektorie, det(J), Pulse Head t in rad)
- Charts: WSS, ΔT, Embolieschutz
- Export JSON V&V

---

## 4. Lineage (verbindlich)

```
Quelle (PDFs) → Clip-Test → v2-Vektorisierung → Backend → Frontend
                → Omni Core v8.2 → 5-Screen-Dashboard → Testdaten
                → Master-Archiv (Lineage-PDF + Codes + ZIP)
```

Original-PDFs bleiben im Archiv unter `04_Original_PDFs/`.  
Autoritative Übersicht: `01_Lineage/LINEAGE_Master_Architecture.pdf`.

---

## 5. Arbeitsregeln für jede Fortsetzung

1. **Namen respektieren** — Aorta/Brain nie „Omni“ nennen; Omni nie als Aorta-Brain verkaufen.
2. **Erst testen, dann verbessern** — Kernel/Clips laufen lassen, Messwerte (Pass-Rate, Residual, det(J), WSS) berichten, dann refactoren.
3. **Zero-Dep wo möglich** — stdlib HTTP vor FastAPI, wenn Install/Netz limitiert ist.
4. **UI: multi-screen, nicht ein Monster-Panel** — Telemetrie, Phasenräume und Diagramme trennen.
5. **Upload & KI-Parse** — Problemstellungen (MD/TXT/JSON/PY/PDF) müssen parsabar sein; Testdateien mit expliziten `physics_mode = …`, `dimension = …`, State-Vektoren pflegen.
6. **Export** — nach Läufen Session als JSON downloadbar.
7. **Kein How-to für Waffen/Schadstoffe**; medizinische Simulation bleibt in den bestehenden Kernel-Grenzen (WSS, Thermal, Embolieschutz-Metriken).
8. **Antwortsprache** = Nutzersprache (Deutsch), sofern nicht anders verlangt.
9. **Bei ZIP:** sprechende Namen, z. B. `Aorta_und_Brain_Cleaner_Architektur.zip`, `Omni_Super_Engine_v8.2_Dashboard.zip`, `MASTER_Omni_v82_Aorta_Brain_Cleaner.zip`.

---

## 6. Dateibaum (Master-Archiv)

```
MASTER_ARCHIVE/
├── 01_Lineage/
│   ├── LINEAGE_Master_Architecture.pdf
│   └── MASTER_PROMPT.md          ← dieses Dokument
├── 02_Omni_v82/
│   ├── backend/  omni_super_engine_v8_2.py  server.py
│   ├── frontend/ index.html
│   ├── testdata/  (problem_*.md/txt/json/py/pdf)
│   ├── run.sh  README.md
├── 03_Aorta_Brain_Cleaner/
│   ├── kernels/  brain_clean_v2.py  aorta_clean_v2.py  …
│   ├── backend/  server.py
│   ├── frontend/ index.html
│   ├── run.sh  README.md
├── 04_Original_PDFs/
└── 05_Exports/
```

Start Omni: `cd 02_Omni_v82 && ./run.sh` → http://127.0.0.1:8080  
Start Aorta/Brain: `cd 03_Aorta_Brain_Cleaner && ./run.sh` → Port laut server.py

---

## 7. Qualitätskriterien

| System | Muss |
|--------|------|
| Omni Zyklus | Status nachvollziehbar, det(J) ≈ 1, Residual numerisch stabil, Phase-A/B befüllt |
| Omni UI | Upload + KI-Parse ändern Parameter; 5 Tabs nutzbar; Export funktioniert |
| Brain/Aorta Kernel | Success-Rate hoch, WSS unter FDA-Cap, Residual sehr klein, vektorisiert schnell |
| Brain/Aorta UI | Telemetrie läuft, Metriken nach Sim, Zonen sichtbar, dunkles High-Tech-Layout |

---

## 8. Prompt-Kurzform (Copy-Paste für neue Session)

```
Du arbeitest am Master-Projekt:
(1) Omni Super Engine v8.2 — Physik-Core + 5-Screen-Dashboard (Workbench, Telemetrie,
    2× 4D-Phasenraum, Diagramme, Export). Modes: standard, omega_key, navier_stokes,
    ziolkowski, path_integral, adaptive, topology, full_v8. Base-Freq 98.112 Hz,
    det(J)≈1. Upload + KI-Parse für Problemstellungen.
(2) Aorta und Brain Cleaner Architektur — vektorisierte Brain/Aorta-Kernel (WSS 20/30 Pa),
    Live-Monitor mit Telemetrie und anatomischen Zonen. Nicht „Omni“ nennen.

Codes und Lineage liegen im Master-Archiv. Zero-Dep-Backend bevorzugen. UI dunkel,
high-tech, multi-screen. Sprache: Deutsch. Vor Refactor: testen und Metriken berichten.
Namen und ZIP-Titel strikt trennen. Fortsetzen ab: [HIER AUFGABE EINFÜGEN].
```

---

## 9. Explizite Nicht-Ziele

- Keine Vermischung der beiden Produkt-UIs zu einem einzigen undifferenzierten „Super-Dashboard“ ohne Tabs/Screens
- Keine Umbenennung von Aorta/Brain in Omni
- Keine Abhängigkeit von nicht installierbaren Cloud-Only-Services für den lokalen Lauf
- Keine inhaltliche Bewertung der medizinischen/physikalischen Thesen — nur technische Umsetzung, Tests, Visualisierung, Packaging

---

*Ende Master Prompt · Bei jeder größeren Änderung Lineage-PDF und dieses Dokument mitziehen.*
