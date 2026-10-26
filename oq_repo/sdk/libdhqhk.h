#ifndef LIBDHQHK_H

#include <stdint.h>
#define LIBDHQHK_H

#ifdef __cplusplus
extern "C" {
#endif

#define OQ_DHC_DIMENSION   48
#define OQ_DHC_PHASES      12
#define OQ_DHC_LAYERS       4
#define OQ_DHC_BGA_PINS   144

/* Status strings (null-terminated, max 31 chars + NUL) */
typedef struct {
    double state_psi[OQ_DHC_DIMENSION];
    char   swat_status[32];   /* "CONNECTED" | "PHYSICALLY_DISCONNECTED" */
    char   system_status[32]; /* "VERIFIED_STABLE" | "LOCKDOWN_ABSORBING_STATE" */
    char   wallet_lock[32];   /* "SECURE" | "ISOLATED_AND_LOCKED" */
    int    dimension;
    int    cycle_count;
} qhk_core_t;

/* Return codes */
#define QHK_OK                 0
#define QHK_ERR_NULL          -1
#define QHK_ERR_DIMENSION     -2
#define QHK_ERR_LOCKED        -3
#define QHK_ERR_INVALID_PDU   -4

/**
 * Initialise kernel to clean state (CONNECTED / SECURE / VERIFIED_STABLE).
 * state_psi is zeroed. Returns QHK_OK on success.
 */
int qhk_initialize_kernel(qhk_core_t* core);

/**
 * Inject an Intent-PDU (JSON string). The engine extracts dimension / state
 * vector if present. Returns QHK_OK or QHK_ERR_*.
 */
int qhk_inject_intent_pdu(qhk_core_t* core, const char* json_pdu);

/**
 * Execute one hard 100-ms tact cycle (Layer-8 GIP evaluation + diffusion).
 * If SWAT is already PHYSICALLY_DISCONNECTED the call is a no-op and
 * returns QHK_ERR_LOCKED.
 */
int qhk_execute_tact_cycle(qhk_core_t* core);

/**
 * Soft-reset operational state (does not clear forensic ledger on host side).
 */
int qhk_reset_kernel(qhk_core_t* core);

/**
 * Query current residual (mean abs gradient). Returns negative on error.
 */
double qhk_get_residual(const qhk_core_t* core);

/* CMOS / sensor boundary (Layer-1 host API; digitized samples) */
typedef struct {
    uint32_t res_h;
    uint32_t res_v;
    double   fps;
    double   v_min;
    double   v_max;
    uint32_t sample_count;
    const double* samples; /* length sample_count; may be NULL */
} qhk_sensor_frame_t;

/**
 * Map sensor sample window into state_psi (downsample) and optionally
 * run one tact. Returns QHK_ERR_LOCKED if SWAT disconnected.
 */
int qhk_ingest_sensor_frame(qhk_core_t* core, const qhk_sensor_frame_t* frame, int execute_cycle);

typedef struct {
    double   determinant;
    double   residual;
    double   torsion_proxy;
    double   base_frequency_hz;
    double   psi_energy;
    uint32_t cycle;
    char     swat_status[32];
    char     system_status[32];
    char     frame_seal[17];
} qhk_field_params_t;

/** Fill field/GTR telemetry from current core state. */
int qhk_get_field_params(const qhk_core_t* core, qhk_field_params_t* out);



#ifdef __cplusplus
}
#endif

#endif /* LIBDHQHK_H */
