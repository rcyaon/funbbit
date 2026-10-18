# STM32U083KCU6

STMicroelectronics STM32U083KC ultra-low-power Arm Cortex-M0+ MCU: 56 MHz,
256 KB flash, 40 KB SRAM, UFQFPN32 5 x 5 mm, 0.5 mm pitch, 3.6 x 3.6 mm
exposed pad (ST package A0B8), -40 to +85 °C.

Primitive package: the component only. Decoupling, LSE crystal, reset
capacitor, BOOT0 strap, and debug header belong to the integrating design.

Datasheet: [DS14463 Rev 2](https://www.st.com/resource/en/datasheet/stm32u083kc.pdf).

## Usage

```zen
Mcu = Module("@registry/components/STMicroelectronics/STM32U083KCU6/STM32U083KCU6.zen")

Mcu(
    name = "MCU",
    VDD = VDD_3V3,
    VDDA = VDDA_3V3,
    GND = GND,
    NRST = NRST,
    BOOT0 = BOOT0,
    PA13 = SWDIO,
    PA14 = SWCLK,
)
```

## Integration notes

- VDD pins 1/17: 100 nF each + one 4.7 µF (Fig. 13); 1.71–3.6 V. VDDUSB is
  internally VDD on this package, so USB (PA11/PA12) needs VDD ≥ 3.0 V.
- VDDA/VREF+ pin 5: 100 nF + 1 µF. VSS pins 16/32 and the EP share `GND`
  (ST recommends soldering the EP to ground).
- PF3-BOOT0 (31) selects boot at reset; PA13/PA14 are SWDIO/SWCLK.
- Fig. 3 labels pin 17 "VDDUSB"; Table 12 says VDD, which is used.

## Pin map (UFQFPN32, Table 12)

| Pin | Name | Pin | Name | Pin | Name | Pin | Name |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | VDD | 9 | PA3 | 17 | VDD | 25 | PA15 |
| 2 | PC14-OSC32_IN | 10 | PA4 | 18 | PA8 | 26 | PB3 |
| 3 | PC15-OSC32_OUT | 11 | PA5 | 19 | PA9 | 27 | PB4 |
| 4 | PF2-NRST | 12 | PA6 | 20 | PA10 | 28 | PB5 |
| 5 | VDDA/VREF+ | 13 | PA7 | 21 | PA11 [PA9] | 29 | PB6 |
| 6 | PA0 | 14 | PB0 | 22 | PA12 [PA10] | 30 | PB7 |
| 7 | PA1 | 15 | PB1 | 23 | PA13 | 31 | PF3-BOOT0 |
| 8 | PA2 | 16 | VSS | 24 | PA14 | 32 | VSS |
| EP (33) | Exposed pad → GND | | | | | | |

## Footprint

`ST_UFQFPN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm`, generated from ST's land pattern
(Fig. 35): 0.25 × 0.65 mm lands at 0.5 mm pitch, 4.85 mm center span (5.50 mm
outer), 3.6 × 3.6 mm EP, EP paste 3 × 3 windows. STEP model generated from
Table 89 nominals and embedded (5.0 × 5.0 × 0.60 mm).

## Sourcing

- Primary: `STM32U083KCU6` (tray).
- Alternative: `STM32U073KCU6` — same UFQFPN32 pinout/package; lacks the AES
  accelerator (firmware-only difference).
