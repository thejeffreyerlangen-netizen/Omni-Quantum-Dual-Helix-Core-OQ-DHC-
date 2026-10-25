#!/usr/bin/env python3
"""
LiteX wrapper module around the SystemVerilog OQ-DHC FPGA bridge.

Exposes a CSR bank so the LiteX CPU (or host via UARTWishboneBridge)
can drive execute/reset, inject state_psi words, and read SWAT status,
residual and cycle count.
"""

from migen import *
from litex.soc.interconnect.csr import *


class OQDHCBridge(Module, AutoCSR):
    def __init__(self, platform, pads=None):
        self.platform = platform

        # --- Control / status CSRs ---
        self._control = CSRStorage(fields=[
            CSRField("execute", size=1, offset=0, pulse=True,
                     description="Pulse: run one tact cycle"),
            CSRField("reset",   size=1, offset=1, pulse=True,
                     description="Pulse: soft-reset kernel state"),
        ])
        self._status = CSRStatus(fields=[
            CSRField("swat",   size=2, offset=0,
                     description="0=CONNECTED 1=PHYSICALLY_DISCONNECTED"),
            CSRField("system", size=2, offset=2,
                     description="0=VERIFIED_STABLE 1=LOCKDOWN"),
            CSRField("wallet", size=2, offset=4,
                     description="0=SECURE 1=ISOLATED_AND_LOCKED"),
        ])
        self._residual = CSRStatus(16, description="Mean-abs residual proxy")
        self._cycle    = CSRStatus(32, description="Executed tact cycles")

        # --- state_psi write window ---
        self._psi_addr = CSRStorage(8, description="Index 0..47 into state_psi")
        self._psi_data = CSRStorage(16, description="Signed 16-bit value to write")
        self._psi_we   = CSRStorage(fields=[
            CSRField("write", size=1, offset=0, pulse=True,
                     description="Pulse: write psi_data to psi_addr"),
        ])

        # Signals to/from SV core
        host_valid  = Signal()
        host_addr   = Signal(8)
        host_wdata  = Signal(32)
        host_ready  = Signal()
        host_rdata  = Signal(32)
        swat_enc    = Signal(2)
        sys_enc     = Signal(2)
        wal_enc     = Signal(2)

        # Simple host transaction FSM:
        # idle -> write_ctrl / write_psi / read_status -> wait_ready -> idle
        fsm = FSM(reset_state="IDLE")
        self.submodules += fsm

        do_exec   = Signal()
        do_reset  = Signal()
        do_psi_wr = Signal()
        do_status = Signal()

        self.sync += [
            do_exec.eq(self._control.fields.execute),
            do_reset.eq(self._control.fields.reset),
            do_psi_wr.eq(self._psi_we.fields.write),
        ]

        # Status sampling every cycle from last host_rdata when addr was 0x04 etc.
        # For simplicity we also wire status fields combinatorially from core outputs.
        self.comb += [
            self._status.fields.swat.eq(swat_enc),
            self._status.fields.system.eq(sys_enc),
            self._status.fields.wallet.eq(wal_enc),
        ]

        # Residual / cycle updated when we issue a status read (addr 0x08 / 0x0C)
        # Minimal path: after every execute we issue internal reads.
        read_phase = Signal(2)

        fsm.act("IDLE",
            If(do_exec | do_reset,
                NextState("WR_CTRL")
            ).Elif(do_psi_wr,
                NextState("WR_PSI")
            )
        )
        fsm.act("WR_CTRL",
            host_valid.eq(1),
            host_addr.eq(0x00),
            host_wdata.eq(Cat(do_exec, do_reset, Replicate(0, 30))),
            If(host_ready,
                NextState("RD_STATUS")
            )
        )
        fsm.act("WR_PSI",
            host_valid.eq(1),
            host_addr.eq(0x10 + self._psi_addr.storage),
            host_wdata.eq(Cat(self._psi_data.storage, Replicate(0, 16))),
            If(host_ready,
                NextState("IDLE")
            )
        )
        fsm.act("RD_STATUS",
            host_valid.eq(1),
            host_addr.eq(0x04),
            If(host_ready,
                NextState("RD_RESIDUAL")
            )
        )
        fsm.act("RD_RESIDUAL",
            host_valid.eq(1),
            host_addr.eq(0x08),
            If(host_ready,
                NextValue(self._residual.status, host_rdata[:16]),
                NextState("RD_CYCLE")
            )
        )
        fsm.act("RD_CYCLE",
            host_valid.eq(1),
            host_addr.eq(0x0C),
            If(host_ready,
                NextValue(self._cycle.status, host_rdata),
                NextState("IDLE")
            )
        )

        # Pad defaults
        relais_p = getattr(pads, "relais_p", Signal()) if pads else Signal()
        relais_n = getattr(pads, "relais_n", Signal()) if pads else Signal()
        sense    = getattr(pads, "sense", Signal(reset=1)) if pads else Signal(reset=1)
        force    = getattr(pads, "force", Signal()) if pads else Signal()

        self.specials += Instance(
            "oq_dhc_fpga_bridge",
            i_clk_100m          = ClockSignal(),
            i_rst_n             = ~ResetSignal(),
            o_swat_relais_out_p = relais_p,
            o_swat_relais_out_n = relais_n,
            i_swat_sense        = sense,
            o_swat_force_open   = force,
            i_host_valid        = host_valid,
            i_host_wdata        = host_wdata,
            i_host_addr         = host_addr,
            o_host_ready        = host_ready,
            o_host_rdata        = host_rdata,
            o_swat_status_enc   = swat_enc,
            o_system_status_enc = sys_enc,
            o_wallet_lock_enc   = wal_enc,
            # unused outputs tied off
            o_osc_carrier_p     = Signal(),
            o_osc_carrier_n     = Signal(),
            o_osc_mod_p         = Signal(),
            o_osc_mod_n         = Signal(),
            o_clk_phase         = Signal(12),
            i_io_ring_in        = Signal(13),
            o_io_ring_out       = Signal(13),
            o_io_ring_oe        = Signal(),
        )

        platform.add_source(str(
            __import__("pathlib").Path(__file__).resolve().parent.parent
            / "rtl" / "oq_dhc_fpga_bridge.sv"
        ))
