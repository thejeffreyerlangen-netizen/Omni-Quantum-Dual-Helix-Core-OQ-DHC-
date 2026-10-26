/**
 * libdhqhk.c – Omni Quantum Dual Helix Core SDK (software reference model)
 * Version 1.1.0
 *
 * Implements the same semantics as the Python hardened kernel:
 *  - 4×12 helix torsion
 *  - baseline-protected GIP evaluation
 *  - SWAT fail-closed
 *  - residual + soft reset
 *
 * This is a pure-C host-side model suitable for simulation, HIL and
 * early bring-up of the Development Board. It does not talk to real silicon.
 */

#include "libdhqhk.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* Internal kernel state (not exposed in public header) */
typedef struct {
    double prev_torsion;
    int    baseline_set;
    double omega_crit;
    double lege_tol;
    unsigned long block_seq;
} qhk_internal_t;

static qhk_internal_t g_internal;

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

static void set_status(char *dst, const char *src)
{
    strncpy(dst, src, 31);
    dst[31] = '\0';
}

static double compute_residual(const qhk_core_t *core)
{
    if (!core || core->dimension < 2)
        return 0.0;

    double sum = 0.0;
    int n = core->dimension;
    /* central differences approximation of mean |gradient| */
    sum += fabs(core->state_psi[1] - core->state_psi[0]);
    for (int i = 1; i < n - 1; i++) {
        double g = 0.5 * (core->state_psi[i + 1] - core->state_psi[i - 1]);
        sum += fabs(g);
    }
    sum += fabs(core->state_psi[n - 1] - core->state_psi[n - 2]);
    return sum / (double)n;
}

static double calculate_torsion(const qhk_core_t *core)
{
    /* Map onto 4×12 lattice (pad / truncate to 48) */
    double lattice[48];
    memset(lattice, 0, sizeof(lattice));
    int n = core->dimension < 48 ? core->dimension : 48;
    for (int i = 0; i < n; i++)
        lattice[i] = core->state_psi[i];

    double torsion_sum = 0.0;
    for (int layer = 0; layer < 3; layer++) {
        for (int col = 0; col < 12; col++) {
            int idx_a = layer * 12 + col;
            int idx_b = (layer + 1) * 12 + ((col + 11) % 12); /* roll -1 */
            torsion_sum += fabs(lattice[idx_a] - lattice[idx_b]);
        }
    }
    return torsion_sum / 48.0;
}

/* Extremely lightweight JSON number array extractor for "state" or "psi".
 * Not a full parser – sufficient for the Intent-PDU format used by the project.
 */
static int extract_state_from_json(const char *json, double *out, int max_n)
{
    if (!json || !out)
        return -1;

    const char *p = strstr(json, "\"state\"");
    if (!p)
        p = strstr(json, "\"psi\"");
    if (!p)
        p = strstr(json, "\"initial_state\"");
    if (!p)
        return 0; /* no state field – not an error */

    p = strchr(p, '[');
    if (!p)
        return -1;
    p++;

    int count = 0;
    while (*p && count < max_n) {
        while (*p && (isspace((unsigned char)*p) || *p == ','))
            p++;
        if (*p == ']')
            break;
        char *end;
        double v = strtod(p, &end);
        if (end == p)
            break;
        out[count++] = v;
        p = end;
    }
    return count;
}

static int extract_dimension_from_json(const char *json)
{
    if (!json)
        return -1;
    const char *p = strstr(json, "\"dimension\"");
    if (!p)
        return -1;
    p = strchr(p, ':');
    if (!p)
        return -1;
    p++;
    while (*p && isspace((unsigned char)*p))
        p++;
    return (int)strtol(p, NULL, 10);
}

/* ------------------------------------------------------------------ */
/* Public API                                                         */
/* ------------------------------------------------------------------ */

int qhk_initialize_kernel(qhk_core_t *core)
{
    if (!core)
        return QHK_ERR_NULL;

    memset(core, 0, sizeof(*core));
    core->dimension = OQ_DHC_DIMENSION;
    set_status(core->swat_status, "CONNECTED");
    set_status(core->system_status, "VERIFIED_STABLE");
    set_status(core->wallet_lock, "SECURE");
    core->cycle_count = 0;

    memset(&g_internal, 0, sizeof(g_internal));
    g_internal.omega_crit = 2.5;
    g_internal.lege_tol   = 1.0e-6;
    g_internal.baseline_set = 0;
    g_internal.prev_torsion = 0.0;
    g_internal.block_seq = 0;

    return QHK_OK;
}

int qhk_reset_kernel(qhk_core_t *core)
{
    if (!core)
        return QHK_ERR_NULL;

    /* Preserve dimension, zero state, restore operational flags.
     * Forensic ledger (if kept on host) is intentionally not cleared. */
    int dim = core->dimension;
    memset(core->state_psi, 0, sizeof(core->state_psi));
    core->dimension = dim > 0 ? dim : OQ_DHC_DIMENSION;
    set_status(core->swat_status, "CONNECTED");
    set_status(core->system_status, "VERIFIED_STABLE");
    set_status(core->wallet_lock, "SECURE");
    core->cycle_count = 0;

    g_internal.prev_torsion = 0.0;
    g_internal.baseline_set = 0;
    /* block_seq intentionally continues */

    return QHK_OK;
}

int qhk_inject_intent_pdu(qhk_core_t *core, const char *json_pdu)
{
    if (!core)
        return QHK_ERR_NULL;
    if (!json_pdu)
        return QHK_ERR_INVALID_PDU;

    if (strcmp(core->swat_status, "PHYSICALLY_DISCONNECTED") == 0)
        return QHK_ERR_LOCKED;

    int dim = extract_dimension_from_json(json_pdu);
    if (dim >= 4 && dim <= OQ_DHC_DIMENSION)
        core->dimension = dim;

    double tmp[OQ_DHC_DIMENSION];
    int n = extract_state_from_json(json_pdu, tmp, OQ_DHC_DIMENSION);
    if (n < 0)
        return QHK_ERR_INVALID_PDU;

    if (n > 0) {
        memset(core->state_psi, 0, sizeof(core->state_psi));
        int copy = n < core->dimension ? n : core->dimension;
        for (int i = 0; i < copy; i++)
            core->state_psi[i] = tmp[i];
        /* New state → re-baseline on next cycle */
        g_internal.baseline_set = 0;
    }

    return QHK_OK;
}

int qhk_execute_tact_cycle(qhk_core_t *core)
{
    if (!core)
        return QHK_ERR_NULL;

    if (strcmp(core->swat_status, "PHYSICALLY_DISCONNECTED") == 0)
        return QHK_ERR_LOCKED;

    int n = core->dimension;
    if (n < 4 || n > OQ_DHC_DIMENSION)
        return QHK_ERR_DIMENSION;

    /* Discrete Laplace diffusion (matches Python 0.08 coefficient) */
    double lap[OQ_DHC_DIMENSION];
    for (int i = 0; i < n; i++) {
        double left  = core->state_psi[(i - 1 + n) % n];
        double right = core->state_psi[(i + 1) % n];
        lap[i] = left - 2.0 * core->state_psi[i] + right;
    }
    for (int i = 0; i < n; i++)
        core->state_psi[i] += 0.08 * lap[i];

    /* GIP / torsion evaluation */
    double current_torsion = calculate_torsion(core);
    double d_torsion_dt = 0.0;
    const double dt = 0.01;

    if (!g_internal.baseline_set) {
        g_internal.prev_torsion = current_torsion;
        g_internal.baseline_set = 1;
        d_torsion_dt = 0.0;
    } else {
        d_torsion_dt = (current_torsion - g_internal.prev_torsion) / dt;
        g_internal.prev_torsion = current_torsion;
    }

    double e_res = fabs(d_torsion_dt) - g_internal.omega_crit;
    double residual = compute_residual(core);

    if (e_res > 0.0) {
        /* Soft phase absorption */
        double phase = current_torsion * 3.141592653589793 * 0.15;
        for (int i = 0; i < n; i++) {
            /* real part of complex multiply by exp(i*phase) ≈ cos(phase) */
            core->state_psi[i] *= cos(phase);
        }
        residual = compute_residual(core);

        if (residual > g_internal.lege_tol * 50.0) {
            set_status(core->swat_status, "PHYSICALLY_DISCONNECTED");
            set_status(core->system_status, "LOCKDOWN_ABSORBING_STATE");
            set_status(core->wallet_lock, "ISOLATED_AND_LOCKED");
        }
    }

    g_internal.block_seq++;
    core->cycle_count++;
    return QHK_OK;
}

double qhk_get_residual(const qhk_core_t *core)
{
    if (!core)
        return -1.0;
    return compute_residual(core);
}


int qhk_ingest_sensor_frame(qhk_core_t* core, const qhk_sensor_frame_t* frame, int execute_cycle)
{
    if (!core || !frame)
        return QHK_ERR_NULL;
    if (strcmp(core->swat_status, "PHYSICALLY_DISCONNECTED") == 0)
        return QHK_ERR_LOCKED;

    int n = core->dimension > 0 ? core->dimension : OQ_DHC_DIMENSION;
    if (n > OQ_DHC_DIMENSION)
        n = OQ_DHC_DIMENSION;

    if (frame->samples && frame->sample_count > 0) {
        for (int i = 0; i < n; i++) {
            unsigned idx = (unsigned)((double)i * (frame->sample_count - 1) / (double)(n > 1 ? n - 1 : 1));
            if (idx >= frame->sample_count)
                idx = frame->sample_count - 1;
            core->state_psi[i] = frame->samples[idx];
        }
    }

    /* peak check against 3.0 V digital SWAT proxy */
    if (frame->samples && frame->sample_count > 0) {
        for (uint32_t k = 0; k < frame->sample_count; k++) {
            if (frame->samples[k] > 3.0) {
                set_status(core->swat_status, "PHYSICALLY_DISCONNECTED");
                set_status(core->system_status, "LOCKDOWN_ABSORBING_STATE");
                set_status(core->wallet_lock, "ISOLATED_AND_LOCKED");
                return QHK_ERR_LOCKED;
            }
        }
    }

    if (execute_cycle)
        return qhk_execute_tact_cycle(core);
    return QHK_OK;
}


int qhk_get_field_params(const qhk_core_t* core, qhk_field_params_t* out)
{
    if (!core || !out)
        return QHK_ERR_NULL;
    memset(out, 0, sizeof(*out));
    double residual = compute_residual(core);
    double energy = 0.0;
    int n = core->dimension > 0 ? core->dimension : OQ_DHC_DIMENSION;
    if (n > OQ_DHC_DIMENSION) n = OQ_DHC_DIMENSION;
    for (int i = 0; i < n; i++)
        energy += core->state_psi[i] * core->state_psi[i];
    double phase = residual * 0.01;
    double det = cos(phase) * cos(phase) + sin(phase) * sin(phase);
    out->determinant = det;
    out->residual = residual;
    out->torsion_proxy = 0.0;
    out->base_frequency_hz = 98.112;
    out->psi_energy = energy;
    out->cycle = (uint32_t)core->cycle_count;
    strncpy(out->swat_status, core->swat_status, 31);
    strncpy(out->system_status, core->system_status, 31);
    /* simple seal */
    unsigned long h = 1469598103ul;
    const char *s = core->swat_status;
    while (*s) { h ^= (unsigned char)(*s++); h *= 16777619ul; }
    h ^= (unsigned long)core->cycle_count;
    snprintf(out->frame_seal, sizeof(out->frame_seal), "%08lx%08lx", h, (unsigned long)(energy * 1000.0));
    return QHK_OK;
}
