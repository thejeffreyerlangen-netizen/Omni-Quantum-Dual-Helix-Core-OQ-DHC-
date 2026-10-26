# OQ-DHC Development Board – KiCad Project Skeleton

## Inhalt

```
kicad/oq_dhc_devboard/
├── oq_dhc_devboard.kicad_pro   # Projekt + Netklassen (Power, HS_Diff, SWAT)
├── oq_dhc_devboard.kicad_sch   # Root-Schematic mit BGA-Symbol (Kernpins)
├── oq_dhc_devboard.kicad_pcb   # Board-Outline 100×80 mm + BGA-Platzhalter
└── footprints/
    └── BGA-144_12x12_0.8mm.kicad_mod
```

## Öffnen in KiCad 7 / 8

1. KiCad starten → **Open Project** → `oq_dhc_devboard.kicad_pro`
2. Footprint-Bibliothek hinzufügen:  
   Preferences → Manage Footprint Libraries → Ordner `footprints/` als Project Library
3. Vollständige Pin-Belegung aus `docs/bga144_pinout.csv` importieren  
   (Symbol Editor → Pin Table oder externes Script)

## Netklassen (bereits gesetzt)

| Klasse   | Pattern        | Verwendung              |
|----------|----------------|-------------------------|
| Power    | VCC_*, GND*    | Stromversorgung         |
| HS_Diff  | IO_RING_*, CLK_PHASE_* | Hochgeschwindigkeits-Paare |
| SWAT     | SWAT_*         | Interlock-Differenzpaar |

## Nächste Schritte im EDA-Tool

1. Restliche 144 Pads im Footprint ergänzen (12×12 Raster, 0.8 mm)
2. Symbol um alle Nets aus der CSV erweitern
3. Power-Symbols (VCC_ANALOG, VCC_DIGITAL, GND) platzieren
4. TX-9942 Relais + Isolator als eigene Hierarchical Sheet
5. Length-Matching-Regeln für CLK_PHASE und SWAT aktivieren
6. PDN-Impedanz prüfen (Ziel < 10 mΩ bis 50 MHz digital)

## Hinweis

Das Skelett ist bewusst minimal und gültig. Es dient als importierbarer Startpunkt; die vollständige Verdrahtung und das finale Footprint-Finish erfolgen in KiCad.

## Vollständiges 12×12-Footprint erzeugen

```bash
cd kicad/scripts
python gen_bga144_footprint.py
# optional: --pitch 0.8 --pad 0.4 --out ../oq_dhc_devboard/footprints/BGA-144_12x12_0.8mm.kicad_mod
```

Das Skript schreibt alle **144 Pads** (A1–L12) im 0,8-mm-Raster inkl. Courtyard, Fab-Outline und Pin-1-Marker.
