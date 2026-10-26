#!/usr/bin/env python3
"""
LiteX SoC target that includes the OQ-DHC FPGA Emulation Bridge.

Examples:
  python target_oq_dhc.py --build
  python target_oq_dhc.py --build --load
  python target_oq_dhc.py --uart-name=serial --build
"""

import argparse
import os
import sys

# Allow running from fpga/litex without install
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from migen import *
from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from oq_dhc_platform import Platform
from oq_dhc_bridge_module import OQDHCBridge


class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), **kwargs):
        platform = Platform()

        SoCCore.__init__(
            self,
            platform,
            sys_clk_freq,
            ident="OQ-DHC LiteX SoC with FPGA Emulation Bridge",
            **kwargs,
        )

        # Clock / reset
        self.submodules.crg = CRG(
            platform.request("clk100"),
            ~platform.request("cpu_reset"),
        )

        # Status LEDs
        self.submodules.leds = LedChaser(
            pads=platform.request_all("user_led"),
            sys_clk_freq=sys_clk_freq,
        )

        # OQ-DHC Bridge (SWAT pads if present)
        try:
            swat_pads = platform.request("swat")
        except Exception:
            swat_pads = None
        self.submodules.oq_dhc = OQDHCBridge(platform, pads=swat_pads)


def main():
    parser = argparse.ArgumentParser(description="OQ-DHC LiteX Target")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load", action="store_true", help="Load bitstream")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))

    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))


if __name__ == "__main__":
    main()
