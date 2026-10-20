# Fabrication outputs

Exported from code.diode.computer/lena/b/funbit (main @ 0969e25 + J3 footprint v0.1.1 and silkscreen cleanup). `pcb publish funbit.zen --check` passes build, sync and DRC.

- `funbit-gerbers-drill.zip`: Gerber X2 + Excellon drill, ready to upload
- `funbit-pos-{top,bottom,both}.csv`: pick-and-place (mm, DNP excluded)
- `funbit-ipc2581.xml`: IPC-2581 rev C
- `funbit-bom.csv`: BOM with distributor PNs; last line is the hand-fitted LCD
- `funbit-assembly-{top,bottom}.pdf`, `funbit-layers.pdf`, `funbit-schematic.pdf`

```
BOARD / FAB NOTES
  44 x 72 mm, 2 layers, FR-4 1.6 mm, 1 oz copper, ENIG, black solder mask,
  white silkscreen. Signals 0.2 mm, VBAT 0.3 mm, 0.16 mm min clearance,
  vias 0.45/0.2 mm tented. Back layer is a continuous GND pour.
  Jack barrels (J1, J2) overhang the bottom edge by about 1.7 mm by design:
  leave clearance there in any panel rail or V-score.

ASSEMBLY NOTES
  - Two-sided SMT. Top: 39 placements (incl. 3 fiducials). Bottom: 16
    (incl. 2 fiducials): BT1 cell holder, J3, Q1, SW3 reset, Y1 + C12/C13,
    C1, C18, C20-C22, R20, R22. Suggested order: top first, bottom second
    (BT1 is the heaviest bottom part and has no locating pegs).
  - BT1's centre pad is the cell's negative contact: keep it paste-free
    (the footprint has no paste opening).
  - Not placed by SMT: the Sharp LS013B7DH03 LCD (insert its FPC into J4 after
    assembly, display side up; bend the FPC only 0.8-6.0 mm from the glass,
    min 0.45 mm radius), the CR2032 cell, and the optional captive-cable wires
    on TP1-TP3.
  - DNP: C23, R1, R2, R13, R14, R15, R19, R21, C4, C5.
    R18 (fitted) and R19 (DNP) are alternative LCD EXTMODE straps: never fit
    both, it shorts VBAT to GND.
  - Sourcing: STM32U083KCU6 is out of stock at DigiKey right now; Mouser has
    stock (511-STM32U083KCU6). The 47 uF 1210 bulk caps have no US stock;
    LCSC stocks them, or use any 47 uF 10 V X7R 1210.

KNOWN ISSUE IN THE 3D FILES
  The library 3D models of the headphone jacks (J1, J2) and the coin-cell
  holder (BT1) are rotated 180 degrees, so the renders and STEP show the jack
  openings facing into the board. The copper is correct: the jacks can only be
  soldered with their openings at the bottom edge, and the CR2032 slides in
  from the top (strap) end of the board.
```
