# Design notes

Working notes for funbit rev 0.1. Requirements and the decision table are in
[`spec.md`](spec.md). This file records **status, open issues and how-tos**
that do not belong in the spec.

## Status (2026-10-17)

| Area | State |
| --- | --- |
| Zener source (`funbit.zen`, `modules/`) | Complete. `pcb build` passes; the one warning (`VBAT_lcd_vdd`) is expected, see below. |
| Envelope detector | Simulated in ngspice and re-run on 2026-10-17: attack 20.7 ms, release 153.9 ms, music on at 27.6 mV rms / off at 16.5 mV rms, front end 1.90 µA. |
| Schematic (`eda/eda.kicad_sch`) | Grouped into one titled block per module on an A2 sheet. Netlist checked identical to the generated original (86 parts, 46 nets). |
| Placement | All parts placed, 44 × 72 mm, 2 layers. |
| Routing | **Incomplete by request.** Only the analog front end and the LCD bus into J4 are routed (57 segments, 2 vias). GND pours not yet defined. |
| Fab outputs | BOM (`fab/funbit-bom.csv`) and schematic PDF. No Gerbers yet. |

## Block overview

| Block | Module | What it does |
| --- | --- | --- |
| POWER | `power.zen` | CR2032 (BT1, back) → Q1 reverse-polarity P-FET → VBAT. 3 × 47 µF bulk (+1 DNP). No regulator. |
| AUDIO PASSTHROUGH | `audio_passthrough.zen` | J1 in → 0 Ω links (R3/R4, where the dropped volume pot was) → J2 out. Common ground. Captive-cable pads, DNP bleeds. |
| AUDIO SENSE | `audio_sense.zen` | 100 kΩ taps sum L+R into U1A, an inverting precision half-wave rectifier. C3/R6/R10 set attack/release. U1B is the music-present comparator with hysteresis. Option B direct-ADC parts are DNP. |
| MCU | `mcu.zen` | STM32U083KCU6, decoupling per DS, LSE crystal, BOOT0 pull-down, NRST cap. |
| DISPLAY | `display.zen` | J4 FPC for the Sharp LS013B7DH03. EXTMODE strap (R18 fitted / R19 DNP), CS pull-down. |
| HMI | `hmi.zen` | 3 front buttons + pinhole reset (back). |
| DEBUG | `debug.zen` | Cortex 10-pin SWD header J3 (back) + probe pads. |
| MECHANICAL | `funbit.zen` | 2 × M2 holes, 5 fiducials. |

## Known issues and things to check

1. **LCD vs cell voltage.** The Sharp panel is specified 2.7–3.3 V, while the
   cell runs 2.0–3.2 V. This is handled in firmware (blank below 2.7 V), and
   `pcb build` reports it as the warning `VBAT_lcd_vdd`. The warning is
   expected. Do not "fix" it by narrowing the VBAT range.
2. **ERC: 3 × "power pin not driven".** KiCad's ERC wants a `PWR_FLAG` on
   VBAT and GND. The generated schematic has none. This is cosmetic: it does
   not change the netlist or the board. The other ERC warnings ("symbol
   library not configured", "footprint link") appear because the symbols are
   embedded and the stdlib footprint cache (`.pcb/`) only exists after
   `pcb build`.
3. **Datasheet citation (fixed).** `modules/mcu.zen` cited "DS14548" for the
   Stop 2 figure. The STM32U083KC datasheet is **DS14463** (Rev 2, Mar 2024),
   and its Table 40 gives 750 nA at 3.0 V. The comment now says DS14463.
4. **Large-signal compression.** At 1 V rms input the envelope reaches
   1141 mV (3.0 V cell) / 1034 mV (2.7 V cell) above VMID, versus about
   1.75 V expected from the small-signal gain. That is fine for a "how loud
   is it" signal, but firmware should not assume linearity above about
   0.5 V rms.
5. **47 µF bulk caps out of US stock** at export time (see `quote.md`).
6. **README battery mismatch (fixed).** The old README said "LiPo battery",
   but the design is a single CR2032 with no charger. The README now says
   CR2032.
7. Open mechanical questions (from the spec): button plunger positions,
   strap-hole size, exact LCD window. Whether to fit the input bleed resistors
   R1/R2 depends on how the player is connected in practice.

## Routing to do

- Finish routing on 2 layers. Go to 4 only if forced (spec).
- Define GND pours on both layers, stitched with vias. Keep the pour away
  from the high-impedance audio-sense nodes (`RECT_SUMJ`, `CMP_POS`, the
  2.2 MΩ / 22 MΩ resistors) or guard them, because board leakage matters at
  these impedances.
- Keep the LSE crystal (Y1, back) loop short and guarded. Do not route other
  signals under it.
- J4 is 0.5 mm pitch. Keep the LCD bus as routed.
- Run DRC with `pcb layout funbit.zen --check` (it validates without
  rewriting the layout) or in KiCad.

## Working with this repo

- **Zener is the source of truth for the circuit.** Change `modules/*.zen`,
  then `pcb build` and `pcb layout funbit.zen`. `pcb layout` updates
  `eda/eda.kicad_pcb` (keeping placement and routing) and **does not touch
  `eda/eda.kicad_sch`**.
- The KiCad project must stay in `eda/` next to `vendor/` and `.pcb/`,
  because `eda/fp-lib-table` uses `${KIPRJMOD}/../vendor/...` and
  `${KIPRJMOD}/../.pcb/stdlib/...`.
- `vendor/` is committed so `pcb build --offline` works. `.pcb/` is a cache
  and is ignored.

### Regrouping the schematic after a regeneration

If a new schematic is generated (e.g. after adding a module), the block layout
can be re-applied with the scripts in `tools/kicad-schematic/`:

```sh
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
cp eda/eda.kicad_sch /tmp/orig.kicad_sch
python3 tools/kicad-schematic/unrail.py  /tmp/orig.kicad_sch /tmp/mid.kicad_sch
python3 tools/kicad-schematic/regroup.py /tmp/mid.kicad_sch eda/eda.kicad_sch .
# verify: netlists must match
$K sch export netlist -o /tmp/a.net /tmp/orig.kicad_sch
$K sch export netlist -o /tmp/b.net eda/eda.kicad_sch
python3 tools/kicad-schematic/netcmp.py /tmp/a.net /tmp/b.net
$K sch export pdf -o fab/funbit-schematic.pdf eda/eda.kicad_sch
```

- `unrail.py` breaks the generator's shared VBAT/GND decoupling rails, which
  chain caps from different modules. Each cap pin gets its own VBAT/GND
  power symbol, so the nets are unchanged.
- `regroup.py` moves each symbol together with its wire stubs and labels as
  one unit, into the block of the module named in its `Path` property. Parts
  inside a block follow the declaration order in the `.zen` file (signal
  flow). Block descriptions and the row layout are at the top of the script
  (`DESC`, `LAYOUT`). A new module must be added there.
