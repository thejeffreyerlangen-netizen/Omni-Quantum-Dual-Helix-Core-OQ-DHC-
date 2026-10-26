# Anhang – Drei Implementierungs-Layer (OQ-DHC)

## Layer 1 – Golden Model & Spezifikation
- **Rolle:** Software-Wahrheit, Protokoll-Freeze  
- **Kern:** Python-Engine, `protocol.py`, C-SDK, Signal-Map  
- **Exit:** Host-Tests grün, CSR/Pin-Semantik versioniert  

## Layer 2 – Synthetisierbares RTL & FPGA
- **Rolle:** Hardware-Wahrheit vor Silicon  
- **Kern:** `oq_dhc_digital_core` (CSR, PSI, SWAT-FSM, Phasen), SV-TB, Vivado/LiteX  
- **Exit:** RTL-Sim OK, FPGA mit gleichem CSR-Verhalten wie Layer 1  

## Layer 3 – ASIC & Board v1
- **Rolle:** Digitaler Tapeout + Bring-up  
- **Kern:** PDK-Flow, Timing/Power/DFT, BGA an eingefrorene Map, SDK gegen Silicon  
- **Exit:** Timing/DFT nach Plan; erster Die **ohne** spekulatives Analog  

**Regel:** Spec nur in Layer 1 ändern; Layer 2 und 3 leiten ab.
