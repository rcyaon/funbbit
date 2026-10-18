# KMR2x1NGLFS — C&K / Littelfuse KMR2 SMT Tactile Switch (NG, silver)

SPST normally-open momentary tactile switch, 4.2 x 2.2 mm body (4.6 mm over
the leads), 1.9 mm high, SMT gullwing, IP40. 32 VDC / 50 mA max. Covers
KMR211/221/231/241NGLFS (1.2 N / 2 N / 3 N / 4 N actuation force), selected
by `actuation_force`.

## Usage

Active-low button to GND:

```zen
KMR2 = Module("code.diode.computer/lena/registry/components/Littelfuse/KMR2x1NGLFS/KMR2x1NGLFS.zen")

GND = Net("GND")
BTN_N = Net("BTN_N")

KMR2(name="SW_USER", P1=BTN_N, P2=GND)
KMR2(name="SW_BOOT", actuation_force="2N", P1=Net("BOOT_N"), P2=GND)
```

`P1`/`P2` each map to an internally bonded terminal pair (pads 1+4 and
2+3), so all four pads are connected automatically.

## Notes

- Footprint is the datasheet recommended NG land pattern (5.0/3.2 mm
  spans, 0.9 x 1.0 mm pads).
- 3D model is KiCad's `SW_Push_1P1T-SH_NO_CK_KMR2xxG` STEP, embedded with no
  offset. It has the four corner leads only (no ground tab), so it suits the NG
  part, and matches the datasheet 4.6 mm lead span, 1.9 mm actuator height and
  oval actuator. It is 2.8 mm across vs the datasheet's 2.2 mm — 0.3 mm oversize
  per side, conservative for clearance but not a mechanical master.
- G (ground-pin), gold-contact (LFG), and ULC variants are not covered;
  they differ in footprint or electrical ratings.
