# Power budget

Targets from the spec: **< 10 µA asleep**, **< 300 µA average while music
plays**, from one CR2032. Everything runs straight from VBAT (no regulator).
All figures are at VBAT = 3.0 V, 25 °C, typical, unless noted.

**Result:** about **6.9 µA asleep** (typ) and about **66 µA** while playing
with the suggested firmware plan (about 200 µA in a heavy-redraw worst case).
Both targets are met at typical values. The sleep target depends on the LCD:
at the LCD's *maximum* static power, sleep is about 20 µA. **Measure this on
the first boards.**

## Sources

| Ref | Document |
| --- | --- |
| [ST] | STM32U083xC datasheet **DS14463 Rev 2** (Mar 2024) |
| [Sharp] | LS013B7DH03 spec **LD-26X06A** |
| [Sim] | `testbench/run_envelope_checks.py` (ngspice, Microchip MCP6041 macro model), run 2026-10-17 |

## 1. Asleep: pet on screen, waiting for music

MCU in Stop 2. The LCD keeps showing its image (memory-in-pixel), LPTIM2 makes
EXTCOMIN from the LSE, and the comparator watches for music.

| Load | Current | Source |
| --- | --- | --- |
| MCU Stop 2, LSE + RTC on, EN_ULP = 1, LPCAL = 1 | 0.94 µA | [ST] Table 40 (3.0 V row) |
| LPTIM2 clocked from LSE (1.13 µA/MHz × 32.768 kHz) | 0.04 µA | [ST] Table 44 |
| BOR in ultra-low-power mode (ENULP = 1) | 0.06 µA | [ST] Table 24 note (1.1 µA without ULP) |
| LCD static, no data update: 12 µW typ | 4.0 µA | [Sharp] Table 6-4, condition 1 |
| Audio front end: MCP6042 (both channels) + bias ladder + hysteresis | 1.90 µA | [Sim] |
| EXTCOMIN pin toggling into LCD input, CS pull-down (CS low) | ≈ 0 | |
| **Total (typ)** | **6.9 µA** | target < 10 µA ✔ |
| Total with LCD static at its 50 µW max | 19.6 µA | ✘ over target |

Notes:

- Without EN_ULP and with BOR at normal power, the MCU adds about 1.4 µA
  (1.25 µA Stop 2 with RTC + 1.1 µA BOR instead of 0.94 + 0.06). That is
  still under target, but set `EN_ULP`.
- Stop 1 (3.3 µA) would also fit, but Stop 2 is the plan because LPTIM2
  keeps running in it.
- **Unknowns, measure on hardware:** leakage of the 3 × 47 µF X7R bulk caps
  (the spec-sheet minimum insulation resistance of large MLCCs can allow
  µA-level leakage, though typical parts are far lower), board leakage around
  the 2.2 MΩ / 22 MΩ nodes, and the actual LCD static power.
- A held button adds about 75 µA (internal pull-up, about 40 kΩ). Firmware
  should not stay awake while waiting on a long press.

## 2. Music playing

Assumed firmware plan (see `firmware-handoff.md` §5):

- ADC samples `ENV_OUT` + `AUDIO_VMID` at **100 Hz**. Each wake is about
  100 µs of Run at 16 MHz range 2 (1.15 mA), including the 13.4 µs Stop 2
  wake-up ([ST] Table 45).
- Animation at **10 fps**, about **32 changed lines per frame** (the pet sprite):
  2 ms of drawing at MSI 4 MHz Run (0.365 mA), then SPI DMA at 1 MHz
  (32 × 18 + 2 bytes = 4.6 ms) in Sleep at 4 MHz (0.19 mA).
  [ST] Tables 27, 36.
- LCD data-update power: [Sharp] gives only 50 µW typ for a full update at
  1 Hz (vs 12 µW static). Here it is **extrapolated** linearly: 38 µW per
  full-screen update per second, scaled by the fraction of lines written.
  This is an estimate, not a datasheet figure.

| Load | Current |
| --- | --- |
| Asleep baseline (§1) | 6.9 µA |
| 100 Hz ADC wakes (100 Hz × 100 µs × 1.15 mA) | 11.5 µA |
| Drawing + SPI, 10 fps × 32 lines | 16.1 µA |
| LCD data updates, 10 fps × ¼ screen (extrapolated) | 31.7 µA |
| ADC analog, VREFINT buffer (µs-long conversions) | < 1 µA |
| **Total (typ)** | **≈ 66 µA** — target < 300 µA ✔ |

Worst case: **full-screen redraw every frame at 10 fps** (18.4 ms SPI per frame,
5 ms of drawing), which adds about 53 µA of MCU and about 127 µA of LCD
(extrapolated). Total **≈ 200 µA**, still under 300 µA. Limit full redraws to
scene changes.

Things that would break the budget: running the CPU continuously (16 MHz Run
is 1.15 mA), Option B direct 8 kHz sampling with the CPU awake, or leaving
`DBG_STOP` set.

## 3. Peaks and the cell

- The highest peak is about 1.4 mA (Run at 16 MHz range 1) plus LCD COM
  switching. A CR2032 has 10–100 Ω internal resistance over its life, so it
  droops up to about 0.15 V at end of life. The 3 × 47 µF bulk (about
  100–115 µF effective) carries short pulses: a 1.4 mA, 5 ms burst droops
  about 0.07 V from the caps alone.
- The LCD needs ≥ 2.7 V, so firmware blanks it below 2.7 V (see
  `firmware-handoff.md` §3). The MCU's BOR1 resets at 2.00 V typ falling
  ([ST] Table 24).

## 4. Battery life estimate

Assumes about **200 mAh usable** from a CR2032 at these light loads. Check
the chosen cell's datasheet. Usable capacity above the LCD's 2.7 V cutoff is
lower than the rated capacity, which is usually specified to 2.0 V.

| Use | Average / day | Life |
| --- | --- | --- |
| 1 h music/day, rest asleep | ≈ 226 µAh | ≈ 2.4 years |
| 3 h music/day, rest asleep | ≈ 344 µAh | ≈ 1.6 years |

Self-discharge (about 1 %/year) and the LCD cutoff will shorten these.
Treat them as an upper bound until the board is measured.
