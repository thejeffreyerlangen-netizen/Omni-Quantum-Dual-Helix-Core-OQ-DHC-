# Projektstatus: OQ-DHC – Weg zum produktionsreifen Chip-Stack

**Stand:** v1.2 (Digital-Core-MVP im Repo)  
**Klassifikation:** Forschungs- und Simulationsreferenz mit klar definiertem Tapeout-Pfad

---

## Kurzfassung

Dieses Repository ist ein **hybrides Hardware-/Software-Prototyping-Framework** für den Omni Quantum Dual Helix Core (OQ-DHC). Es liefert Golden Model, SDK, Board-/Pinout-Spec, FPGA-Brücken und ab v1.2 einen **synthetisierbaren digitalen Steuerkern**.

Es ist **noch kein** fertiger, foundry-qualifizierter Chip-Stack. Die Struktur ist jedoch so angelegt, dass der Übergang zu FPGA-MVP und digitalem ASIC-Flow (z. B. OpenLane/Sky130) planbar ist.

**Zielbild Produktion:** digitaler Kern + SDK + FPGA-Prototyp + Board v1 – ohne die erste Silizium-Iteration an nicht tapeout-fähige Analog-/Memristor-Blöcke zu koppeln.

---

## Ist-Zustand vs. Produktion

| Schicht | Aktueller Stand | Für Produktion erforderlich |
| -------- | --------------- | --------------------------- |
| Architektur-Spec | Pinout, Domänen, SWAT, Register-Map vorhanden | stabil, versioniert, change-controlled |
| Verhaltensmodell | Python + C-SDK | als Golden Model behalten |
| Digital-RTL | Bridge, GTR-Gating, **oq_dhc_digital_core (MVP)** | erweiterter Steuerkern, Timing-Closure, DFT |
| Verification | Python/C-Tests, SV-Smoke-TBs | cocotb/UVM, Coverage, Formal an Interfaces |
| Backend | nicht angebunden | PDK, Synthesis, P&R, Timing, Power (UPF), DFT |
| Analog/Mixed | nur Spezifikation | echte Blöcke **oder** klare Abgrenzung off-chip / nicht im ersten Die |
| Package/Board | KiCad-Skelett + BGA-144 | Silicon-Bump-Map, SI/PI, Bring-up |
| SDK/Firmware | C gegen Modell | gegen RTL-Sim → FPGA → Silicon |

---

## Was „produktionsreif“ hier bedeutet

1. **Digitaler Tapeout-Pfad** – synthetisierbares RTL, Constraints, Verification, ASIC-Flow (OpenLane/Sky130 oder Foundry).
2. **Analog / Memristor / 3D** – Phase 2 oder externes System; spekulative Physik darf den digitalen Tapeout nicht blockieren.
3. **Ein Golden Model** – Python/C als Referenz; eine Register-/Pin-Spec; RTL, SDK und Doku werden daraus abgeleitet oder streng dagegen geprüft.

---

## Architektur-Richtung

```
Spec (Protocol + Pinout + CSR)
        ↓
Golden Model (Python/C)  ←→  Synthesizable RTL (oq_dhc_digital_core)
        ↓                         ↓
   Host-Tests              SV-TB / cocotb / Formal
                                  ↓
                         FPGA-Prototyp (gleiche CSR/Pins)
                                  ↓
                         ASIC-Flow (OpenLane oder Foundry)
                                  ↓
                         Board v1 an Silicon-Pinout
```

SWAT Fail-Closed und Display-Gating: **digitale FSMs + IO-Zellen** – ohne spekulatives Analog umsetzbar.

---

## Umgesetzter nächster Schritt (im Repo)

| Deliverable | Pfad |
|-------------|------|
| Package + Parameter | `fpga/rtl/digital_core/include/oq_dhc_pkg.sv` |
| SWAT-FSM | `fpga/rtl/digital_core/oq_dhc_swat_fsm.sv` |
| PSI-Registerfile | `fpga/rtl/digital_core/oq_dhc_psi_mem.sv` |
| Residual-Proxy | `fpga/rtl/digital_core/oq_dhc_residual.sv` |
| Phasen-FSM | `fpga/rtl/digital_core/oq_dhc_phase_fsm.sv` |
| CSR-Bank (HOST_REG) | `fpga/rtl/digital_core/oq_dhc_csr_bank.sv` |
| Top Digital Core | `fpga/rtl/digital_core/oq_dhc_digital_core.sv` |
| SV-Testbench | `fpga/sim/digital_core/tb_oq_dhc_digital_core.sv` |
| Sim-Runner | `fpga/sim/digital_core/run_sim.sh` |

Protokoll-Alignment: `src/protocol.py`, `docs/HW_SW_SIGNAL_MAP.md`, `sdk/libdhqhk`, LiteX-Driver.

**Simulation:** `bash fpga/sim/digital_core/run_sim.sh` (erfordert `iverilog`/`vvp` im PATH).

---

## Nächste Meilensteine (Priorität)

1. cocotb-TB gegen dasselbe CSR-Protokoll; Coverage auf STATUS/SWAT-Übergänge  
2. Digital Core als Top in Vivado/LiteX statt nur Soft-Bridge  
3. OpenLane/Sky130-Skelleton **oder** verbindliches „FPGA-only MVP bis Silicon“  
4. Spec-Freeze: Analog = nicht im ersten Die  
5. Board-Rev an eingefrorene Bump-/Ball-Map  

---

## Fazit für Stakeholder

| Aussage | Bewertung |
|---------|-----------|
| Brauchbares Engineering-Rahmenwerk | Ja |
| Klare Spec- und Modell-Basis | Ja |
| Synthetisierbarer Digital-MVP im Repo | Ja (v1.2) |
| Produktionsreifer Chip-Stack | Nein – geplanter Übergang |
| Erste Die-Scope ohne spekulatives Analog | Empfohlen und hier so ausgerichtet |

*Dieses Dokument ist die projektmanagement-taugliche Statusfassung; technische Details stehen in README, HW_SW_SIGNAL_MAP und den RTL-Quellen.*

---

## Anhang A – Drei Implementierungs-Layer

Der Weg zum produktionsreifen Stack ist in **drei Layer** gegliedert. Jeder Layer hat klare Lieferobjekte, Schnittstellen und Exit-Kriterien. Analog/Memristor liegt bewusst **außerhalb** von Layer 1 (erster Die).

### Layer 1 – Golden Model & Spezifikation (Software-Wahrheit)

| Aspekt | Inhalt |
|--------|--------|
| Zweck | Referenzverhalten, Host-Tests, Protokoll-Freeze |
| Artefakte | `src/core_engine.py`, `src/protocol.py`, `src/facade.py`, `sdk/libdhqhk.*`, `docs/HW_SW_SIGNAL_MAP.md` |
| Schnittstelle | CSR/`HOST_REG`, Status-Enums (SWAT/SYS/WALLET), PSI[48] |
| Exit-Kriterium | `make test` grün; Register-Map und Pin-Semantik versioniert und change-controlled |

### Layer 2 – Synthetisierbares RTL & FPGA-Prototyp (Hardware-Wahrheit vor Silicon)

| Aspekt | Inhalt |
|--------|--------|
| Zweck | Gleiches Protokoll wie Layer 1, synthetisierbar, auf FPGA bring-up-fähig |
| Artefakte | `fpga/rtl/digital_core/*` (CSR, PSI-Mem, SWAT-FSM, Phase-FSM, Residual), SV-TB, Vivado/LiteX-Anbindung |
| Schnittstelle | identische Adressen `0x00…0x10+`, SWAT-Pins, `clk_phase[11:0]` |
| Exit-Kriterium | RTL-Sim (TB) bestanden; FPGA-Bitstream mit gleichem CSR-Verhalten wie Golden Model |

### Layer 3 – ASIC-Flow & Board an Silicon (Produktion)

| Aspekt | Inhalt |
|--------|--------|
| Zweck | Tapeout-fähiger digitaler Die + Board v1 |
| Artefakte | PDK-Flow (z. B. OpenLane/Sky130 oder Foundry), Constraints, Timing/Power/DFT, finales BGA-/Bump-Map, Bring-up-Firmware |
| Schnittstelle | eingefrorene Ball-Map aus Layer-2-Pinout; SDK gegen Silicon |
| Exit-Kriterium | Timing clean, Scan/DFT nach Plan, Board-Bring-up gegen gemessene IO; **kein** spekulatives Analog im ersten Die |

### Abhängigkeiten zwischen den Layern

```
Layer 1 (Spec + Golden Model)
    ↓  gleiche CSR / Status / PSI
Layer 2 (RTL + FPGA)
    ↓  eingefrorene Pin-/Ball-Map
Layer 3 (ASIC + Board v1)
```

Abweichungen nur über versionierte Spec-Änderung in Layer 1; Layer 2/3 folgen, nicht umgekehrt.


---

## CMOS-Sensor-Anbindung (Layer 1)

Sony-Klassen-Profile (IMX742 / IMX711 / LYTIA-L910) liegen als **Stress-Vektoren** in `src/cmos_fusion.py` und `tests/test_cmos_fusion.py`.

- Digitisierte/emulierte Spannungsfenster → PSI-Injektion + SWAT-Peak-Guard (3,0 V)
- **Nicht** Teil des ersten Die: ADC-lose Memristor-Direktkopplung bleibt Phase 2 / spekulativ
- C-API: `qhk_ingest_sensor_frame()` in `sdk/libdhqhk.h`


---

## v1.3 – Field-API, Sensor-Stream, E2E

| Komponente | Pfad |
|------------|------|
| Field telemetry (Python) | `src/field_telemetry.py`, `OQDHCFacade.get_field_params()` |
| CMOS ingest + field | `OQDHCFacade.ingest_cmos()` |
| C-API | `qhk_get_field_params()`, `qhk_ingest_sensor_frame()` |
| Sensor stream RTL | `fpga/rtl/digital_core/oq_dhc_sensor_stream.sv` |
| System top | `fpga/rtl/digital_core/oq_dhc_system_top.sv` (Core+Stream+GTR gate) |
| E2E tests | `tests/test_e2e.py` |
| Demo | `scripts/demo_pipeline.py` → `artifacts_out/demo_report.json` |

Host-Shadow-Register (Software, künftige CSR-Erweiterung): `FIELD_DET/ENERGY/SEAL*` in `protocol.HOST_REG`.
