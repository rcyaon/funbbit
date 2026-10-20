# funbit Design Specification

## Purpose

Modern recreation of the Sony PET-F7 "Funbbit" (1998): an inline headphone
accessory that sits between a portable player and headphones, taps the audio
without disturbing it, and animates a virtual pet on a small reflective LCD.
The pet dances while music plays and gets fat when it does not. The owner
writes the firmware; this board must hand off cleanly to that work.

## Requirements

### Build and assembly
- 2-layer, 1.6 mm FR-4, 1 oz, ENIG (needed for the coin-cell negative pad and
  the 0.5 mm pitch parts). Go to 4 layers only if routing forces it.
- Board outline <= 44 x 72 mm, radiused corners, two M2 mounting holes,
  strap-hole keep-out at the top, a clean silkscreen graphic area (clear shell).
- All SMD. Passives 0603 or larger. QFN allowed, no BGA/WLCSP.
- Prefer Diode library parts; flag single-source or low-stock parts.
- Quote for 3 assembled boards.

### Audio
- Passthrough fully passive: headphones work with a dead cell or the MCU in reset.
- Stereo in and out on 3.5 mm TRS SMD jacks. The input also has wire pads with a
  strain-relief slot for a captive cable (not fitted by default).
- Common ground, no ground lift.
- Volume: dual-gang log pot (1-2 kOhm) if an SMD thumbwheel part exists in the
  library, otherwise 0 Ohm links.
- Sense tap must not load the audio: >= 100 kOhm from each channel into a
  summing node, AC-coupled, biased to mid-rail.

### Power
- One CR2032. No boost; no LDO unless justified. 2.0-3.2 V operation.
- < 300 uA average while music plays, < 10 uA asleep.
- >= 100 uF bulk capacitance. SMD cell holder on the back.

### Display
- Sharp reflective memory-in-pixel LCD, 1.1-1.3 in, rated for 3 V. FPC
  connector on the front. EXTCOMIN driven from an MCU timer output.

### HMI and debug
- Front tactile buttons Select, Dance A, Dance B on EXTI pins with internal
  pull-ups and distinct EXTI line numbers.
- Pinhole reset switch on the back, 100 nF on NRST.
- 10-pin 1.27 mm Cortex debug header. Test pads for SWDIO, SWCLK, NRST,
  UART TX, GND, and two spare GPIOs.

### MCU
- Low-power Cortex-M0+/M4 running from the cell; SPI with DMA; 12-bit ADC;
  on-chip comparator; >= 8 KB RAM. Mainstream open toolchain and an
  off-the-shelf dev board.

## Design decisions

| Topic | Decision | Reason |
| --- | --- | --- |
| MCU | STM32U083KCU6 (UFQFPN32; U073KCU6 is a no-AES alternate) | Stop 2 750 nA typ, LPTIM1-3 keep running in Stop 2, so LPTIM2 on PA8 makes the 60 Hz EXTCOMIN without CPU wakeups. 40 KB SRAM / 256 KB flash. Dev board NUCLEO-U083RC. STM32L4 32-pin parts only offer LPTIM1_OUT on SWCLK, and their Stop 1 (4.4 uA) breaks the sleep budget. |
| LCD | Sharp LS013B7DH03, 1.28 in, 128x128 | VDD 2.7/3.0/3.3 V (spec LD-26X06A, Table 6-1). DigiKey stock 33k. |
| LCD below 2.7 V | Firmware blanks the panel below 2.7 V | No 3 V Sharp MIP panel is specified down to 2.0 V. A CR2032 delivers little capacity below 2.7 V at these loads. |
| FPC connector | Panasonic AYF531035 (Sharp's recommendation) | Top and bottom contacts. LCD lies display-up above it, so contact N = LCD pin 11-N. |
| Volume | Dropped; R_LINK_L/R are 0 Ohm | No SMD dual-gang thumbwheel pot exists in the Diode library (only THT/panel parts in the catalog). |
| Sensing | Option A: analog envelope detector | Lets the MCU sleep in Stop 2 until a hardware comparator sees music. Option B (direct 8 kHz ADC) is fitted as DNP footprints. |
| Op amp | MCP6042 (600 nA/ch, RRIO, 14 kHz) | TLV8802 is not rail-to-rail on the input (VCM <= V+ - 0.9 V) and slews at 1.4 V/ms. |
| Envelope | Inverting precision half-wave rectifier, gain 1.24 (mono). R_ATT 2.7k, R_FB 62k, C_ENV 2.2 uF. | Release path is R_ATT + R_FB into the virtual ground, so AUDIO_VMID carries no current. Measured in ngspice (Microchip macro model): 20.7 ms attack, 154 ms release. |
| Music detect | Op amp channel B comparator, threshold ladder on AUDIO_VMID | Trips at 32 mV envelope (28 mV rms tone), releases at 20 mV, at VBAT 3.0 V. |
| Reverse cell | DMP2045U-7 P-FET high side | Cell holders accept a reversed CR2032. The FET drop is < 1 mV at board currents. A Schottky would cost about 0.3 V of headroom. |
| Bulk | 3 x 47 uF X7R 1210 (+1 DNP) | 141 uF nominal, about 100-115 uF effective at 3 V after X7R DC-bias loss. |
| LSE | ABS07 32.768 kHz, 7 pF, 2 x 8.2 pF | The house 12.5 pF / 90 kOhm crystal has gm_crit 2.8 uA/V, above the STM32U0's 2.7 uA/V high-drive limit. |
| Buttons | C&K KMR221NG LFS (2 N) | In the registry. 2 N resists pocket presses. |
| Debug | Samtec FTSH-105-01-L-DV-K-A-P-TR | Standard Cortex 10-pin header; it fits. |
| Back-side placement | Reset switch on the back right edge beside the SWD header; CR2032 slides in from the top (strap) end; bulk caps sit behind the retainer's closed back | Puts the switch on the same right-edge NRST run as the 100 nF cap, the test pad and the header pin, instead of a second branch of about 25 mm across the board's routing corridors. Keystone drawing 3034 rev F puts the open face 7.77 mm from the tab line, which faces the clear top region here. |
| Fiducials | 3 on the front (two top corners, one bottom left), 2 on the back (diagonal corners) | Front set is non-collinear and spans the fine-pitch QFN and the 0.3 mm FPC connector. |
| Routing | Signals on the top layer; the back is a continuous GND pour with short hops only. 0.2 mm signals, 0.3 mm VBAT and cell feed, 0.45/0.2 mm tented vias, 3 GND vias at each jack sleeve | Keeps one unbroken return plane under the analog block, the crystal and the headphone sleeve-to-sleeve path. Under the CR2032 there is only the GND pour, the negative contact and the cell's own feed vias at the retainer tabs; no other signals. |

## Open Questions

- Shell mechanics: button plunger positions, strap-hole size, and the exact LCD
  window. The layout assumes plungers directly over the switches and a
  strap post at top centre. The back shell needs a cell door at the top end
  (the cell slides toward the bottom of the board) and a reset pinhole at the
  back right edge, behind the front test-pad grid.
- Whether to fit the DNP input bleed resistors (R_BLEED_L/R) depends on how the
  player is connected in practice.
