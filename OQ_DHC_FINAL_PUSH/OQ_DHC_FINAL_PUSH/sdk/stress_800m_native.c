/* Native 800M tact-cycle stress via libdhqhk (no Python loop). */
#define _POSIX_C_SOURCE 199309L
#include "libdhqhk.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

static void load_sine(qhk_core_t *core) {
    for (int i = 0; i < OQ_DHC_DIMENSION; ++i) {
        core->state_psi[i] = sin(2.0 * 3.14159265358979323846 * (double)i / (double)OQ_DHC_DIMENSION);
    }
}

int main(int argc, char **argv) {
    long long n = 800000000LL;
    long long report_every = 5000000LL;
    if (argc > 1) n = atoll(argv[1]);
    if (argc > 2) report_every = atoll(argv[2]);

    qhk_core_t core;
    if (qhk_initialize_kernel(&core) != QHK_OK) {
        fprintf(stderr, "init failed\n");
        return 1;
    }
    load_sine(&core);

    printf("========================================================================\n");
    printf(" NATIVE C STRESS — %lld tact cycles (libdhqhk)\n", n);
    printf("========================================================================\n");
    fflush(stdout);

    double t0 = now_sec();
    long long lockdowns = 0;
    long long impulses = 0;
    double max_res = 0.0;
    int errors = 0;

    for (long long i = 1; i <= n; ++i) {
        if (i % 25000LL == 0) {
            /* impulse */
            for (int k = 0; k < OQ_DHC_DIMENSION; ++k)
                core.state_psi[k] = ((double)((i * 1103515245ULL + k * 12345ULL) % 10000) / 10000.0 - 0.5) * 10.0;
            impulses++;
        }
        if (i % 50000LL == 0) {
            /* force a hard residual spike path: large values then cycle */
            for (int k = 0; k < OQ_DHC_DIMENSION; ++k)
                core.state_psi[k] = 1e3;
        }

        int rc = qhk_execute_tact_cycle(&core);
        if (rc == QHK_ERR_LOCKED) {
            lockdowns++;
            qhk_reset_kernel(&core);
            load_sine(&core);
            continue;
        }
        if (rc != QHK_OK) {
            errors++;
        }

        if (i % 1000LL == 0) {
            double r = qhk_get_residual(&core);
            if (r > max_res) max_res = r;
        }

        if (report_every > 0 && i % report_every == 0) {
            double elapsed = now_sec() - t0;
            double rate = (double)i / (elapsed > 0 ? elapsed : 1e-12);
            double pct = 100.0 * (double)i / (double)n;
            double eta = (double)(n - i) / (rate > 0 ? rate : 1e-12);
            printf("  … %lld/%lld  %.4f%%  rate=%.0f cycles/s  ETA=%.2fh  max_res=%.4f  "
                   "lockdowns=%lld impulses=%lld\n",
                   i, n, pct, rate, eta / 3600.0, max_res, lockdowns, impulses);
            fflush(stdout);
            FILE *sf = fopen("/home/workdir/artifacts/stress_800m_native_status.txt", "w");
            if (sf) {
                fprintf(sf,
                        "percent=%.6f\ncycles=%lld\ntotal=%lld\nrate=%.2f\n"
                        "eta_sec=%.1f\nmax_residual=%.6f\nlockdowns=%lld\n"
                        "impulses=%lld\nelapsed_sec=%.1f\nbackend=libdhqhk_c\n",
                        pct, i, n, rate, eta, max_res, lockdowns, impulses, elapsed);
                fclose(sf);
            }
        }
    }

    double elapsed = now_sec() - t0;
    double rate = (double)n / (elapsed > 0 ? elapsed : 1e-12);
    if (strcmp(core.swat_status, "CONNECTED") != 0) {
        qhk_reset_kernel(&core);
        load_sine(&core);
        qhk_execute_tact_cycle(&core);
    }
    double final_res = qhk_get_residual(&core);

    printf("------------------------------------------------------------------------\n");
    printf("  cycles            : %lld\n", n);
    printf("  wall_sec          : %.4f\n", elapsed);
    printf("  cycles_per_sec    : %.1f\n", rate);
    printf("  max_residual      : %.6f\n", max_res);
    printf("  lockdown_events   : %lld\n", lockdowns);
    printf("  impulses          : %lld\n", impulses);
    printf("  errors            : %d\n", errors);
    printf("  final_swat        : %s\n", core.swat_status);
    printf("  final_residual    : %.6e\n", final_res);
    printf("========================================================================\n");
    int ok = (errors == 0 && strcmp(core.swat_status, "CONNECTED") == 0);
    printf("RESULT: %s\n", ok ? "PASS" : "FAIL");
    return ok ? 0 : 1;
}
