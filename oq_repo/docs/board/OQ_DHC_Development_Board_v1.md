# OQ-DHC Development Board – Reference Design v1.0

**Target package:** BGA-144 (12×12, 0.8 mm pitch)  
**Board form factor:** 100 × 80 mm (Eurocard-friendly)  
**Revision:** 1.0 – matches Kernel / Pinout v1.1

---

## 1. Purpose

Das **OQ-DHC Development Board** ist das offizielle Referenz-Mainboard, um den Omni Quantum Dual Helix Core (oder seinen FPGA-/Software-Emulator) in Betrieb zu nehmen. Es stellt bereit:

- Getrennte Analog- und Digital-Stromversorgungen
- Mechanischen S.W.A.T.-Interlock-Pfad (TX-9942-kompatibel)
- Hochgeschwindigkeits-I/O-Ring (UAFF / I-PDU)
- Debug-, Status- und Krypto-Wallet-Schnittstellen
- On-Board-Oszillator-Referenz für ω_c / ω_m

---

## 2. Blockschaltbild (Floorplan)

```
┌─────────────────────────────────────────────────────────────────────┐
│  OQ-DHC DEVELOPMENT BOARD  100 × 80 mm                              │
│                                                                     │
│  ┌──────────────┐   ┌────────────────────────────┐   ┌───────────┐  │
│  │  ANALOG PSU  │   │                            │   │  DIGITAL  │  │
│  │  +3V3_A      │   │     OQ-DHC BGA-144         │   │  PSU      │  │
│  │  LDO + LC    │──►│     (center, 0.8 mm)       │◄──│  +1V8/+3V3│  │
│  │  ultra-low   │   │                            │   │  DC/DC    │  │
│  │  noise       │   └─────────────┬──────────────┘   └───────────┘  │
│  └──────────────┘                 │                                 │
│                                   │ SWAT diff pair                  │
│  ┌──────────────┐                 ▼                                 │
│  │  OSC REF     │          ┌──────────────┐                         │
│  │  98.112 Hz   │          │  TX-9942     │     ┌─────────────────┐ │
│  │  TCXO + PLL  │          │  Relay /     │     │  CRYPTO WALLET  │ │
│  └──────────────┘          │  GST Driver  │     │  Secure Element │ │
│                            └──────────────┘     │  (I²C / SPI)    │ │
│                                                 └─────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  HIGH-SPEED I/O RING  (Samtec / FMC-style connector)         │   │
│  │  13 differential pairs + ref clocks                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │ USB-C      │  │ JTAG /     │  │ Status     │  │ Expansion    │  │
│  │ Debug +    │  │ SWD        │  │ LEDs       │  │ Header 2×20  │  │
│  │ Power      │  │            │  │ (Pt/Ag)    │  │              │  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Stromversorgungs-Domänen

| Domäne | Spannung | Quelle | Entkopplung | Anmerkungen |
|--------|----------|--------|-------------|-------------|
| VCC_ANALOG | 3.3 V | Ultra-low-noise LDO (z. B. LT3045) | 100 nF X7R pro Ball + 10 µF bulk | Sternpunkt-GND unter Package |
| VCC_DIGITAL | 1.8 V Core / 3.3 V I/O | DC/DC + LDO post-reg | 100 nF + 4.7 µF | Getrenntes Digital-GND |
| VCC_SWAT | 5 V | Isolierter Flyback oder USB-Boost | – | Nur für Relais-Spule (galvanisch getrennt) |
| VCC_WALLET | 3.3 V | Eigener LDO vom Digital-Rail | – | Secure-Element Versorgung |

**Wichtige Regel:** Analog-GND und Digital-GND werden **nur an einem Punkt** unter dem BGA-Zentrum verbunden (Star-Point). SWAT-Seite ist opto- oder magnetisch isoliert.

---

## 4. Kritische Netze & Routing-Prioritäten

1. **SWAT-Differentialpaar** (F6/F7 → TX-9942)  
   - Länge matched ±50 µm  
   - Abstand zu HS-I/O ≥ 3× Trace-Breite  
   - Keine Vias wenn möglich

2. **CLK_PHASE_01…12**  
   - Als Low-Skew-Gruppe behandeln  
   - Gleiche Layer, gleiche Via-Count

3. **Analog-Oszillatoren** (A3–A6, L3–L4)  
   - Guard-Ring aus Analog-GND  
   - Keine digitalen Signale in 5 mm Umkreis

4. **HS_IO Ring**  
   - 100 Ω differentielle Impedanz  
   - Länge pro Paar matched  
   - Referenzebene durchgehend

---

## 5. Mechanischer S.W.A.T.-Pfad (TX-9942)

```
OQ-DHC (F6/F7) ──diff──► Isolations-Barrier ──► Relay-Driver ──► Spule
                              │
                              └── Sense (G6) ◄── Kontakt-Rückmeldung
                              └── Force-Open (G7)
```

- Bei `PHYSICALLY_DISCONNECTED` fällt die Haltespannung der Spule weg → mechanischer Öffner trennt die Datenleitungen des I/O-Rings und optional die Wallet-Busse.
- Fail-Closed: Stromlos = offen.

---

## 6. Krypto-Wallet-Platzierung

- Secure Element (z. B. ATECC / SE050-Klasse) sitzt **rechts neben dem BGA**, innerhalb der Digital-Domäne.
- Bus (I²C oder SPI) läuft über einen MUX, der vom SWAT-Force-Open-Signal gesperrt werden kann.
- Physische Abschirmung (kleine Blechhaube) empfohlen.

---

## 7. Debug- & Status-Schnittstellen

| Interface | Funktion |
|-----------|----------|
| USB-C | Power + CDC/UART Debug + optional DFU |
| JTAG/SWD | Boundary-Scan / FPGA-Emulator Bring-up |
| 12× Status-LED | Mapping auf System-Status / SWAT / Wallet / 12 Phasen (Platin-Silber-Optik optional) |
| 2×20 Expansion | GPIO, zusätzliche Analog-Testpunkte, EnKF-Register-Spiegel |

---

## 8. Empfohlene Stückliste (Kern)

- BGA-144 Socket oder Direct-Attach (je nach Prototyp-Stufe)
- LT3045 (Analog LDO) + passende Ferrite
- Isolierter 5 V-Modul für SWAT-Relais
- Mechanisches Signal-Relais oder Solid-State mit Fail-Open-Charakteristik
- Secure Element + Level-Shifter
- Samtec Q-Strip oder FMC-LPC für den HS-I/O-Ring
- 98.112 Hz fähiger TCXO + fractional-N PLL (oder DDS)

---

## 9. Design-Flow Empfehlung

1. Import der Pinout-CSV (`docs/bga144_pinout.csv`) in KiCad / Altium  
2. Constraint-Manager: Differentialpaare + Length-Matching für CLK und SWAT  
3. Power-Integrity: getrennte PDNs, PDN-Impedanz < 10 mΩ bis 50 MHz (Digital)  
4. EMI: Titan-Bodenplatte des Packages als zusätzliche Schirmung nutzen  
5. Bring-up: zuerst Digital-Rail + JTAG, dann Analog, zuletzt SWAT-Loopback-Test

---

## 10. Dateien in diesem Repo

| Datei | Inhalt |
|-------|--------|
| `docs/oq_dhc_bga144_pinout_specification.html` | Interaktive Ball-Matrix |
| `docs/bga144_pinout.csv` | Maschinenlesbare Belegung |
| `docs/board/OQ_DHC_Development_Board_v1.md` | Dieses Dokument |
| `sdk/libdhqhk.[ch]` | Host-side Software-Modell des Kernels |

---

*Dieses Board schließt die Lücke zwischen dem gehärteten Software-Kernel und einem realen Hardware-Prototypen. Es ist fertigungsreif spezifiziert und kann direkt in ein EDA-Tool übernommen werden.*
