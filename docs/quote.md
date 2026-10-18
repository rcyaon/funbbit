# Quote: 3 assembled boards

Status: **parts cost is computed from `fab/funbit-bom.csv`; PCB fabrication and
assembly are not yet quoted.** Those two lines need a real quote from the
board house (the request spec is below), because they depend on vendor,
lead time and the assembly options they accept.

Prices are the US unit prices in the BOM (DigiKey/Mouser single-unit, USD,
as exported). They do not include shipping, tax, tariffs, minimum-order
quantities or attrition spares.

## 1. Parts

| Designators | Qty / board | Part | Unit | Per board | Stock (US / global) |
| --- | --- | --- | --- | --- | --- |
| U2 | 1 | STM32U083KCU6 | 4.06 | 4.06 | 3,427 / **59** |
| U1 | 1 | MCP6042T-I/MS | 1.04 | 1.04 | 23,176 / 461 |
| J3 | 1 | Samtec FTSH-105-01-L-DV-K-A-P-TR | 2.27 | 2.27 | 3,715 / **30** |
| C20 C21 C22 | 3 | Murata GRM32ER71A476KE15L 47 µF 1210 | 0.93 | 2.79 | **0** / 44,310 |
| SW1–SW4 | 4 | C&K KMR221NG LFS | 0.67 | 2.68 | 80,743 / 7,241 |
| J1 J2 | 2 | Same Sky SJ-3523-SMT-TR | 0.88 | 1.76 | 80,575 / — |
| C1 C2 C9 C14–C17 | 7 | 100 nF X7R 0603 | 0.16 | 1.12 | ample |
| D1 D2 | 2 | Vishay BAT54WS-HE3_A-08 | 0.49 | 0.98 | 13,250 / 8,845 |
| C7 C8 C10 C11 C18 | 5 | 1 µF X7R 0603 | 0.19 | 0.95 | ample |
| J4 | 1 | Panasonic AYF531035 FPC | 0.88 | 0.88 | 9,942 / 4,896 |
| Y1 | 1 | Abracon ABS07-32.768KHZ-7-T | 0.86 | 0.86 | ample |
| BT1 | 1 | Keystone 3034TR | 0.49 | 0.49 | 86,680 / 106 |
| Q1 | 1 | Diodes DMP2045U-7 | 0.44 | 0.44 | ample |
| C19, C3, C6, C12 C13 | 5 | other MLCCs | — | 0.84 | ample |
| R3–R12, R16–R18, R20, R22 | 15 | 0603 resistors | ~0.10 | 1.42 | ample |
| **SMT parts subtotal** | **50 placements** | | | **22.58** | |
| — (hand-fit) | 1 | Sharp LS013B7DH03 LCD | 12.39 | 12.39 | 33,509 / — |
| **Parts per board** | | | | **34.97** | |
| **Parts for 3 boards** | | | | **104.90** | |

DNP footprints (C4, C5, C23, R1, R2, R13–R15, R19, R21) are not bought. They
would add $1.89 per board if fitted.

The CR2032 cell is not in the BOM. Add one per board.

## 2. PCB fabrication and assembly (request spec)

Send this with `fab/` outputs (Gerbers, drill, pick-and-place and BOM from
`eda/eda.kicad_pcb`) once routing is finished:

| Item | Value |
| --- | --- |
| Quantity | 3 assembled (fab minimum is usually 5 bare boards) |
| Size | 44 × 72 mm, radiused corners |
| Stack-up | 2 layers, FR-4, 1.6 mm, 1 oz copper |
| Finish | **ENIG** (needed for the coin-cell negative pad and 0.5 mm pitch) |
| Mask / silk | any colour; silkscreen graphic area on front (clear shell) |
| Holes | 2 × M2 non-plated, 3 × 2.0 mm THT pads (captive-cable option, unpopulated) |
| Assembly | **Two-sided SMT.** Top: about 35 placements incl. QFN-32 0.5 mm, MSOP-8, FPC 0.5 mm. Bottom: 15 placements (BT1 coin holder, SW reset, Q1, Y1, J3 SWD header, C20–C22 1210, 0603s). |
| Fine pitch | UFQFPN32 0.5 mm pitch with exposed pad; FPC 0.5 mm |
| Fiducials | 3 top, 2 bottom |
| Not assembled | Sharp LCD (hand-fit into J4), CR2032, DNP parts |
| Parts sourcing | turnkey, or consigned for U2 / J3 / C20–C22 (see risks) |

| Line | Amount |
| --- | --- |
| Parts (3 boards, from §1) | $104.90 |
| PCB fabrication | _to be quoted_ |
| SMT assembly, setup and stencils (two sides) | _to be quoted_ |
| Shipping / tax / tariffs | _to be quoted_ |
| **Total** | _pending fab quote_ |

To cut cost: moving the bottom-side parts to the top (the holder and reset
switch must stay on the back) would make assembly one-sided, which is often
the biggest single saving at this quantity.

## 3. Sourcing risks

- **C20–C22 (47 µF 1210, GRM32ER71A476KE15L):** 0 US stock at export time.
  Global stock is 44k. A different 47 µF 10 V X7R 1210 is an acceptable
  substitute **if** its DC-bias derating keeps the bulk ≥ 100 µF at 3 V.
- **U2 (STM32U083KCU6):** fine at DigiKey (3.4k), very low at LCSC (59). The
  STM32U073KCU6 is a pin-compatible fallback (no AES, firmware-only difference).
- **J3 (Samtec FTSH-105):** low global stock (30). Any 2×5 1.27 mm SMD
  Cortex debug header with the same footprint works. It is only needed for
  development and could be DNP on production units (use the test pads).
- **BT1 (Keystone 3034):** low global stock (106), plenty in the US.
- Single-source parts: U1 (MCP6042), J4 (Panasonic AYF531035, Sharp's
  recommended mate), the LCD (Sharp).
