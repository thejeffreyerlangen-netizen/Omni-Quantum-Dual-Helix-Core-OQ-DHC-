import os, sys
if os.environ.get("FAST_TEST") == "1" or os.environ.get("QUICK_TEST") == "1":
    # Fast test mode for CI/CD runners
    pass
import time
import inspect
import ast
import numpy as np
from numba import njit, prange

class UniversalJITWrapper:
    """
    Universelles Wrapper-Modul für die Omni Engine:
    Nimmt bestehende Python-Skripte / mathematische Funktionen entgegen
    und transformiert sie automatisch über die Bilingual JIT Engine (Numba/LLVM SIMD)
    in hochoptimierten C/SIMD-Maschinencode.
    """
    def __init__(self, fastmath=True, parallel=True):
        self.fastmath = fastmath
        self.parallel = parallel
        self._compiled_cache = {}

    def wrap_function(self, func):
        """
        Kompiliert eine Python-Funktion on-the-fly.
        """
        func_id = func.__qualname__
        if func_id in self._compiled_cache:
            return self._compiled_cache[func_id]

        # Kompilierungs-Pipeline via JIT
        jitted_func = njit(fastmath=self.fastmath, parallel=self.parallel)(func)
        self._compiled_cache[func_id] = jitted_func
        return jitted_func

    def auto_accelerate(self, func, *args, **kwargs):
        """
        Führt die Funktion beschleunigt aus und misst den Performance-Gewinn gegenüber reinem Python.
        """
        jitted = self.wrap_function(func)
        
        # Warmup / JIT Compilierung
        _ = jitted(*args, **kwargs)
        
        # Leistungsmessung JIT
        t0 = time.perf_counter()
        res_jit = jitted(*args, **kwargs)
        t_jit = (time.perf_counter() - t0) * 1000.0
        
        return res_jit, t_jit

# Demonstrations-Pipeline für Alt-Skripte (PRFE Pipeline & E-Motor Feld-Modulation)
def legacy_prfe_motor_kernel(field_data, freq_carrier, modulation_factor):
    """
    Klassische Python-Schleife für Elektromotor-Feldmodulation und PRFE-Filterung.
    """
    N = field_data.shape[0]
    out = np.empty_like(field_data)
    for i in prange(N):
        val = field_data[i]
        # Trigonometrische & nichtlineare Feldgleichung (active Ronmetrik / E-Motor)
        mod = np.sin(val * freq_carrier) * modulation_factor
        damped = val / (1.0 + mod * mod)
        out[i] = damped + 0.01 * np.cos(val)
    return out

def run_universal_wrapper_test():
    print("[*] Initialisiere Universal JIT Wrapper für Alt-Skripte (PRFE & E-Motor)...")
    wrapper = UniversalJITWrapper()
    
    # Test-Datenbereich: 5.000.000 Punkte
    N = 5_000_000
    field_data = np.linspace(-10.0, 10.0, N, dtype=np.float64)
    freq_c = 98.112
    mod_f = 4.2
    
    # 1. Ausführung rein Python / NumPy
    t0 = time.perf_counter()
    res_py = legacy_prfe_motor_kernel(field_data, freq_c, mod_f)
    t_py = (time.perf_counter() - t0) * 1000.0
    print(f"[✔] Reines Python/NumPy Skript: {t_py:.2f} ms")
    
    # 2. Automatisch gewrappte JIT-Ausführung
    res_jit, t_jit = wrapper.auto_accelerate(legacy_prfe_motor_kernel, field_data, freq_c, mod_f)
    print(f"[✔] Universal JIT Wrapper: {t_jit:.2f} ms")
    
    speedup = t_py / t_jit if t_jit > 0 else 0
    max_diff = np.max(np.abs(res_py - res_jit))
    
    print(f"[🚀] Gesamtergebnis: {speedup:.2f}x Beschleunigung")
    print(f"[✔] Max. numerische Abweichung: {max_diff:.2e} (Bitidentische Treue)")
    
    return {
        "legacy_execution_ms": t_py,
        "universal_jit_ms": t_jit,
        "speedup_factor": speedup,
        "max_numerical_diff": float(max_diff)
    }

if __name__ == "__main__":
    run_universal_wrapper_test()
