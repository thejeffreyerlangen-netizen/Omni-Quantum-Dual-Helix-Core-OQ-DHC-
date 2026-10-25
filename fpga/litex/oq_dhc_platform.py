#!/usr/bin/env python3
"""
LiteX platform description for the OQ-DHC FPGA Emulation Bridge.

This is a generic / board-agnostic platform that exposes the SWAT,
clock-phase, oscillator-proxy and host-register interfaces. Bind it to a
real board by overriding _io or by using a vendor platform and connecting
the bridge as a LiteX module.
"""

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD


_io = [
    # System
    ("clk100", 0, Pins("E3"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("C2"), IOStandard("LVCMOS33")),

    # SWAT interlock (example pins – remap to your carrier)
    ("swat", 0,
        Subsignal("relais_p", Pins("D4")),
        Subsignal("relais_n", Pins("D3")),
        Subsignal("sense",    Pins("F4")),
        Subsignal("force",    Pins("F3")),
        IOStandard("LVCMOS33"),
    ),

    # Status LEDs (encode SWAT / system)
    ("user_led", 0, Pins("G6"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("G5"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("G4"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("G3"), IOStandard("LVCMOS33")),

    # Serial for host/debug
    ("serial", 0,
        Subsignal("tx", Pins("D10")),
        Subsignal("rx", Pins("A9")),
        IOStandard("LVCMOS33"),
    ),
]


class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9 / 100e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a35tcsg324-1", _io, toolchain=toolchain)

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", "bscan_spi_xc7a35t.bit")
