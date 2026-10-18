# Firmware handoff

Everything firmware needs to bring up the funbit board. The hardware source of
truth is `modules/*.zen`. If this document and the Zener source disagree, the
source wins. Please fix this file when that happens.

- MCU: **STM32U083KCU6** (Cortex-M0+, 56 MHz max, 256 KB flash, 40 KB SRAM,
  UFQFPN32). Drop-in alternate: STM32U073KCU6 (no AES).
- Dev board for early work: **NUCLEO-U083RC** (same die, more pins).
- Toolchain: STM32CubeU0 HAL/LL, or plain CMSIS with arm-none-eabi-gcc. Any
  SWD probe (ST-LINK V3, J-Link, CMSIS-DAP).
- Supply: the MCU, LCD and op amp all run **directly from the CR2032**
  (VBAT, 2.0–3.2 V across cell life). There is no regulator, so VDD changes as
  the cell discharges, and ADC readings must be ratiometric (see §5).

## 1. Pin map

| Pin | Net | Direction | Peripheral / AF | Notes |
| --- | --- | --- | --- | --- |
| PA0 | `MUSIC_PRESENT` | in | EXTI0, **WKUP1** | High while music plays. Push-pull from op amp, no pull needed. Wakes Stop 2 / Standby / Shutdown. |
| PA1 | `ENV_OUT` | analog | ADC1_IN5, COMP1_INP3 | Audio envelope, after 48 Hz anti-alias RC. |
| PA2 | `UART_TX` | out | USART2_TX (AF7), LPUART1_TX | Debug log. Pad `TP_UART_TX`. |
| PA3 | `UART_RX` | in | USART2_RX (AF7), LPUART1_RX | Pad `TP_UART_RX`. Enable pull-up (pad floats). |
| PA4 | `LCD_DISP` | out | GPIO | LCD on (high) / all-white (low). Image memory is kept. |
| PA5 | `LCD_SCLK` | out | SPI1_SCK (AF5) | ≤ 1.1 MHz (use 1 MHz). |
| PA6 | `LCD_CS` | out | GPIO | **Active high** (Sharp SCS). 1 MΩ pull-down on board. |
| PA7 | `LCD_MOSI` | out | SPI1_MOSI (AF5) | |
| PA8 | `LCD_EXTCOMIN` | out | **LPTIM2_CH1 (AF14)**, TIM1_CH1 (AF1) | 54–65 Hz VCOM clock. Pad `TP_LCD_EXTCOMIN`. |
| PA9 | `SPARE_1` | — | USART1_TX / I2C1_SCL / TIM1_CH2 | Pad `TP_SPARE_1`. Analog or pulled when unused. |
| PA10 | `SPARE_2` | — | USART1_RX / I2C1_SDA / TIM1_CH3 | Pad `TP_SPARE_2`. |
| PA13 | `SWDIO` | — | SWD | Header J3 pin 2, pad `TP_SWDIO`. |
| PA14 | `SWCLK` | — | SWD | Header J3 pin 4, pad `TP_SWCLK`. |
| PB0 | `AUDIO_RAW` | analog | ADC1_IN17 | **Option B only** (parts DNP by default, so the pin floats). Set it to analog. |
| PB1 | `AUDIO_VMID` | analog | ADC1_IN18, COMP1_INM2 | Mid-rail bias, about 0.4956 × VBAT. |
| PB4 | `BTN_SELECT` | in | EXTI4 | Active low. **Enable internal pull-up.** |
| PB5 | `BTN_DANCE_A` | in | EXTI5 | Active low. **Enable internal pull-up.** |
| PB6 | `BTN_DANCE_B` | in | EXTI6 | Active low. **Enable internal pull-up.** |
| PC14 / PC15 | `OSC32_IN` / `OSC32_OUT` | — | LSE | 32.768 kHz, ABS07, CL = 7 pF. |
| PF2 | `NRST` | — | reset | 100 nF to GND. Pinhole switch on the back. |
| PF3 | `BOOT0` | — | BOOT0 | 10 kΩ pull-down → boots from flash. Pull high via `TP_BOOT0` for the ROM bootloader. |
| PA11, PA12, PA15, PB3, PB7 | NC | — | — | **Set to analog mode** (lowest leakage). |

The buttons use EXTI lines 4, 5 and 6, which are distinct. On the STM32U0,
EXTI4..15 share one interrupt vector (`EXTI4_15_IRQn`), so a single handler
reads the pending flags.

## 2. Boot, debug and logging

- **SWD**: 10-pin 1.27 mm Cortex header J3 (Samtec FTSH-105). Pin 1 = VTref,
  which only **senses** VBAT. The probe does not power the board. Without a
  cell, feed **3.0 V into `TP_VBAT`** (never above 3.3 V, the LCD's maximum).
- There is **no SWO** (Cortex-M0+). Log over USART2 on `TP_UART_TX`
  (suggest 115200 8N1). LPUART1 on the same pins can run from LSE in Stop
  mode if you need to log while sleeping (9600 baud max from LSE).
- Debug in Stop mode: set `DBGMCU_CR.DBG_STOP` during development so SWD
  stays attached. **Clear it for current measurements**, because it keeps
  clocks on and the sleep current reads far too high.
- ROM bootloader: short `TP_BOOT0` to VBAT and press reset. Check ST AN2606
  for the STM32U0 bootloader's USART pins before relying on `TP_UART_TX/RX`.
  SWD is the primary programming path.

## 3. Display: Sharp LS013B7DH03 (128 × 128, 1 bit)

Hardware strapping (in `modules/display.zen`):

- `EXTMODE` is tied **high** (R18 0 Ω fitted, R19 DNP). VCOM inversion
  follows the **EXTCOMIN pin**, and the M1/VCOM bit in SPI commands is
  ignored.
- `DISP` has 100 nF to GND. `SCS` has a 1 MΩ pull-down so the panel is
  deselected while the MCU is in reset.

### SPI

- SPI1, master, mode 0 (CPOL 0, CPHA 0), **LSB first**, 8-bit frames,
  SCLK ≤ 1.1 MHz (use 1 MHz). TX only. A DMA channel can feed it.
- CS is **active high** and is driven by GPIO, not hardware NSS. Raise it
  before the first clock and lower it after the last, with a few µs of setup
  and hold (see the Sharp spec LD-26X06A timing table).
- With LSB-first framing, the command bytes are: write lines `0x01`,
  clear all `0x04`, and a no-op/maintain frame `0x00`. This is the same
  convention as Adafruit's `Adafruit_SharpMem` driver, which is a useful
  reference.
- Multi-line write: `0x01`, then for each line: line address (1..128),
  16 data bytes, one `0x00` trailer. Finish the frame with one extra `0x00`.
  Pixel bit 1 = white (reflective), 0 = black.
- Full frame = 128 × 18 + 2 bytes = 2306 bytes ≈ **18.5 ms at 1 MHz**. Only
  send changed lines. The pet sprite usually touches a small number of rows.

### VCOM / EXTCOMIN

- Keep **54–65 Hz** on PA8 all the time the panel shows an image (DC on the
  liquid crystal damages it). Use **LPTIM2** clocked from **LSE**, PWM on
  CH1 (AF14), e.g. 32768 / 512 = 64 Hz, 50 % duty. LPTIM2 keeps running in
  Stop 2, so EXTCOMIN needs no CPU wakeups.
- TIM1_CH1 (AF1) on the same pin is a fallback, but TIM1 stops in Stop mode.

### Power sequence (from the Sharp spec)

1. Power up: VDD is already present (there is no LCD power switch). Send
   "clear all", start EXTCOMIN, then set DISP high.
2. Power down / blanking: DISP low, stop EXTCOMIN (output low), and keep the
   panel quiet.
3. **Undervoltage:** the panel is specified for VDD 2.7–3.3 V, but the cell
   runs down to 2.0 V. **Firmware must blank the panel (step 2) whenever VBAT
   < 2.7 V** and re-init above about 2.75 V (add hysteresis). `pcb build` flags
   this as the `VBAT_lcd_vdd` warning, and that warning is expected.

## 4. Buttons and reset

- `BTN_SELECT` / `BTN_DANCE_A` / `BTN_DANCE_B`: KMR221NG (2 N) to GND,
  internal pull-up, **falling edge** EXTI. They can wake Stop 2. Debounce in
  software (≈ 20 ms, using an LPTIM or RTC tick).
- While a button is held, its pull-up draws about VBAT / 40 kΩ ≈ 75 µA. Do
  not wait for a long press while sitting in run mode. Sleep and re-sample.
- Pinhole reset (SW_RESET, on the back) pulls NRST low directly.

## 5. Audio sensing

The analog front end (`modules/audio_sense.zen`) runs from VBAT, always on, and
draws about **1.9 µA** (op amp + bias ladder, ngspice). Firmware does not have
to turn it on or off.

### Signals

| Net | Meaning |
| --- | --- |
| `AUDIO_VMID` (PB1) | Bias, 0.4956 × VBAT (2.2 MΩ / 39 kΩ / 2.2 MΩ ladder). |
| `ENV_OUT` (PA1) | Envelope, **referenced to VMID**: `env = V(ENV_OUT) − V(VMID)`. Rises with music, rests at ≈ 0. |
| `MUSIC_PRESENT` (PA0) | Comparator output: high when env > threshold. |

Measured in ngspice at VBAT = 3.0 V (`testbench/`, run on 2026-10-17):

| Input (mono, 100 Hz) | env = ENV_OUT − VMID |
| --- | --- |
| 50 mV rms | 63 mV |
| 300 mV rms | 389 mV |
| 1 V rms | 1141 mV (1034 mV at VBAT = 2.7 V; starts to compress) |

- `MUSIC_PRESENT` rises at ≈ 28 mV rms input (env ≈ 32 mV) and falls at
  ≈ 17 mV rms (env ≈ 20 mV). Attack (63 %) about 21 ms, release (37 %) about
  154 ms.
- The threshold scales with VBAT (it is a tap on the bias ladder), so the
  sensitivity in mV rms drops slightly as the cell runs down.

### Suggested use

1. **Asleep (no music):** Stop 2, with EXTI0 rising edge on `MUSIC_PRESENT`
   as a wake source. The pet is "getting fat" here, and the RTC can count the
   hours of silence.
2. **Music playing:** wake on `MUSIC_PRESENT`. Sample `ENV_OUT` and
   `AUDIO_VMID` with ADC1 at **≤ 100 Hz**, because the RC anti-alias corner is
   48 Hz. Use the env value for dance intensity and beat detection (peaks in
   env at 40–200 ms spacing). Go back to Stop 2 between samples (LPTIM1 or
   RTC wakeup).
3. When `MUSIC_PRESENT` falls and stays low for a few seconds, return to the
   asleep state.

### Converting ADC readings

There is no reference voltage on the board: VREF+ = VDDA = VBAT. Read
**VREFINT** (with its factory calibration value `VREFINT_CAL`) to get VBAT:

```
VBAT  = 3.0 V * VREFINT_CAL / VREFINT_DATA        (check the cal VDD in the DS)
env_V = (ENV_OUT_code - VMID_code) * VBAT / 4095
```

Because VMID and ENV_OUT are both ratiometric to VBAT, the difference of the
two codes is clean. Only the conversion to volts needs VREFINT. Use the
longest sampling time on ENV_OUT and VMID. Both are high-impedance sources:
C_AA (100 nF) supplies the charge on ENV_OUT, and VMID has 1 µF.

### Optional alternatives

- **COMP1** can compare `ENV_OUT` (INP3) against `AUDIO_VMID` (INM2) to get a
  software-adjustable music detector (with a DAC/VREFINT scaler as offset),
  if the hardware threshold is not right.
- **Option B (DNP):** fitting R13–R15, C4 and C5 feeds raw audio (AC
  coupled, biased at VMID, 1.5 nF anti-alias) to PB0 for direct ~8 kHz ADC
  sampling and FFT/beat tracking. It costs much more run time. `sense_mode`
  in `audio_sense.zen` controls the population.

## 6. Clocks and low power

- **LSE**: ABS07 32.768 kHz, CL 7 pF, 8.2 pF load caps. gm_crit ≈ 0.8 µA/V,
  so use **LSEDRV = medium-high**. This feeds RTC, LPTIM2 (EXTCOMIN) and
  optionally LPUART1.
- **System clock**: MSI at 4 MHz (Range 1/2) is plenty for 1 MHz SPI and
  sprite blits. Use voltage range 2 at low clocks for lower run current.
- **Stop 2** is the normal sleep mode: 750 nA typ at 3.0 V without RTC,
  0.94 µA with LSE + RTC when `EN_ULP = 1` and `LPCAL = 1` (DS14463 Table 40).
  Set both bits. LPTIM1..3, RTC, LPUART1 and EXTI keep running. Wake-up to
  Run from flash is about 13 µs on HSI16 (Table 45).
- **Brown-out:** enable BOR (BOR1 2.00 V typ falling, DS14463 Table 24) in
  ultra-low-power mode (`ENULP`, about 55 nA instead of 1.1 µA). Below 2.7 V, blank the
  LCD (§3). Below about 2.2 V, consider a "low battery" sleep that wakes
  only on buttons.
- Unused GPIOs: analog mode. Do not enable pulls on `AUDIO_RAW`, `ENV_OUT`
  or `AUDIO_VMID`.
- See [`power-budget.md`](power-budget.md) for the current targets
  (< 10 µA asleep, < 300 µA average with music).

## 7. Bring-up checklist

1. Before fitting the cell, check VBAT–GND resistance (it should not be a
   short) and that Q1 blocks a reversed cell.
2. Power from 3.0 V on `TP_VBAT` with a current limit around 20 mA. Connect
   SWD and read the IDCODE.
3. Blink something on `TP_SPARE_1`, and send a UART "hello" on `TP_UART_TX`.
4. Start LSE and LPTIM2. Scope `TP_LCD_EXTCOMIN` for 54–65 Hz.
5. Plug in the LCD. Send "clear all", set DISP high, then draw a test pattern.
6. Play a 100 Hz tone into J1. Scope `TP_ENV_OUT`, `TP_AUDIO_VMID` and
   `TP_MUSIC_PRESENT`, and compare them with the table in §5.
7. Check that the passthrough still works with the cell removed (it is a
   passive path).
8. Measure the sleep current with the debugger disconnected and
   `DBG_STOP` cleared.
