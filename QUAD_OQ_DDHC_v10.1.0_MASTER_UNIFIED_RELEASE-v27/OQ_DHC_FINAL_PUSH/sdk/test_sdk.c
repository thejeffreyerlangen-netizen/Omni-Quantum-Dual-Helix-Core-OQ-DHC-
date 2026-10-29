/**
 * Minimal host-side test for libdhqhk (software model).
 * Build:  gcc -O2 -o test_sdk test_sdk.c libdhqhk.c -lm
 */
#include "libdhqhk.h"
#include <stdio.h>
#include <math.h>
#include <string.h>

static void print_status(const qhk_core_t *c)
{
    printf("  SWAT=%s  SYS=%s  WALLET=%s  residual=%.4e  cycle=%d\n",
           c->swat_status, c->system_status, c->wallet_lock,
           qhk_get_residual(c), c->cycle_count);
}

int main(void)
{
    qhk_core_t core;
    int rc;

    printf("=== OQ-DHC SDK C Test ===\n");

    rc = qhk_initialize_kernel(&core);
    if (rc != QHK_OK) {
        fprintf(stderr, "init failed: %d\n", rc);
        return 1;
    }
    printf("[1] After init:\n");
    print_status(&core);

    /* Load a smooth sine */
    for (int i = 0; i < OQ_DHC_DIMENSION; i++)
        core.state_psi[i] = sin(2.0 * 3.141592653589793 * i / 48.0);

    printf("[2] After sine load + 5 cycles:\n");
    for (int k = 0; k < 5; k++)
        qhk_execute_tact_cycle(&core);
    print_status(&core);

    if (strcmp(core.swat_status, "CONNECTED") != 0) {
        fprintf(stderr, "FAIL: expected CONNECTED after smooth evolution\n");
        return 1;
    }

    /* Massive injection */
    for (int i = 0; i < OQ_DHC_DIMENSION; i++)
        core.state_psi[i] += 200.0 * ((i % 3) - 1);
    printf("[3] After attack injection:\n");
    qhk_execute_tact_cycle(&core);
    qhk_execute_tact_cycle(&core); /* may need second cycle */
    print_status(&core);

    if (strcmp(core.swat_status, "PHYSICALLY_DISCONNECTED") != 0) {
        fprintf(stderr, "FAIL: expected PHYSICALLY_DISCONNECTED after attack\n");
        return 1;
    }

    /* Locked call must return error */
    rc = qhk_execute_tact_cycle(&core);
    if (rc != QHK_ERR_LOCKED) {
        fprintf(stderr, "FAIL: expected QHK_ERR_LOCKED\n");
        return 1;
    }
    printf("[4] Locked call correctly returned QHK_ERR_LOCKED\n");

    /* Reset */
    qhk_reset_kernel(&core);
    for (int i = 0; i < OQ_DHC_DIMENSION; i++)
        core.state_psi[i] = 0.3 * sin(2.0 * 3.141592653589793 * i / 48.0);
    qhk_execute_tact_cycle(&core);
    printf("[5] After reset + cycle:\n");
    print_status(&core);

    if (strcmp(core.swat_status, "CONNECTED") != 0) {
        fprintf(stderr, "FAIL: expected CONNECTED after reset\n");
        return 1;
    }

    printf("\n*** ALL C SDK TESTS PASSED ***\n");
    return 0;
}
