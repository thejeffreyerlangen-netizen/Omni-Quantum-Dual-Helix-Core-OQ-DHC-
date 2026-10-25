/**
 * OQ-DHC LiteX CSR driver (host / soft-CPU side)
 * Matches oq_dhc_bridge_module.py CSR layout.
 */
#ifndef OQ_DHC_DRIVER_H
#define OQ_DHC_DRIVER_H

#include <stdint.h>

#ifdef CSR_OQ_DHC_BASE
#define OQ_DHC_BASE CSR_OQ_DHC_BASE
#else
#define OQ_DHC_BASE 0x00000000u
#endif

#define OQ_DHC_CONTROL_ADDR    (OQ_DHC_BASE + 0x00)
#define OQ_DHC_CONTROL_EXECUTE (1u << 0)
#define OQ_DHC_CONTROL_RESET   (1u << 1)

#define OQ_DHC_STATUS_ADDR     (OQ_DHC_BASE + 0x04)
#define OQ_DHC_STATUS_SWAT_SHIFT 0
#define OQ_DHC_STATUS_SYS_SHIFT  2
#define OQ_DHC_STATUS_WAL_SHIFT  4
#define OQ_DHC_STATUS_MASK       0x3

#define OQ_DHC_SWAT_CONNECTED               0
#define OQ_DHC_SWAT_PHYSICALLY_DISCONNECTED 1
#define OQ_DHC_SYS_VERIFIED_STABLE          0
#define OQ_DHC_SYS_LOCKDOWN                 1
#define OQ_DHC_WAL_SECURE                   0
#define OQ_DHC_WAL_ISOLATED                 1

#define OQ_DHC_RESIDUAL_ADDR   (OQ_DHC_BASE + 0x08)
#define OQ_DHC_CYCLE_ADDR      (OQ_DHC_BASE + 0x0C)
#define OQ_DHC_PSI_ADDR_ADDR   (OQ_DHC_BASE + 0x10)
#define OQ_DHC_PSI_DATA_ADDR   (OQ_DHC_BASE + 0x14)
#define OQ_DHC_PSI_WE_ADDR     (OQ_DHC_BASE + 0x18)

static inline void oq_dhc_write(uint32_t addr, uint32_t val)
{
    *(volatile uint32_t *)addr = val;
}

static inline uint32_t oq_dhc_read(uint32_t addr)
{
    return *(volatile uint32_t *)addr;
}

static inline void oq_dhc_execute(void)
{
    oq_dhc_write(OQ_DHC_CONTROL_ADDR, OQ_DHC_CONTROL_EXECUTE);
}

static inline void oq_dhc_reset(void)
{
    oq_dhc_write(OQ_DHC_CONTROL_ADDR, OQ_DHC_CONTROL_RESET);
}

static inline void oq_dhc_write_psi(uint8_t idx, int16_t value)
{
    oq_dhc_write(OQ_DHC_PSI_ADDR_ADDR, idx);
    oq_dhc_write(OQ_DHC_PSI_DATA_ADDR, (uint16_t)value);
    oq_dhc_write(OQ_DHC_PSI_WE_ADDR, 1);
}

static inline uint32_t oq_dhc_status(void)
{
    return oq_dhc_read(OQ_DHC_STATUS_ADDR);
}

static inline int oq_dhc_swat_disconnected(void)
{
    return ((oq_dhc_status() >> OQ_DHC_STATUS_SWAT_SHIFT) & OQ_DHC_STATUS_MASK)
           == OQ_DHC_SWAT_PHYSICALLY_DISCONNECTED;
}

#endif /* OQ_DHC_DRIVER_H */
