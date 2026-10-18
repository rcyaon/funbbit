# Same Sky SJ-3523-SMT-TR

3.5 mm stereo (TRS) headphone jack. It is right-angle SMT, 5.0 mm high and has
**no internal switches**. The tip-switch version is SJ-3524-SMT, which has a
different footprint.

## Usage

```zen
Jack = Module("@registry/components/Same_Sky/SJ-3523-SMT/SJ-3523-SMT.zen")

Jack(
    name = "J2",
    TIP = AUDIO_L,
    RING = AUDIO_R,
    SLEEVE = GND,
)
```

| Pin | Function |
| --- | --- |
| 1 | sleeve |
| 2 | tip |
| 3 | ring |
| 4 | not populated on SJ-3523 (tip switch on SJ-3524). No land |

- **Footprint** (datasheet rev 1.07 p2, "Recommended PCB Layout"):
  - Sleeve and ring lands are 2.8 × 2.2 mm. The tip land is 2.8 × 2.8 mm.
  - Two Ø1.70 mm non-plated holes, 7.0 mm apart on the jack axis, take the
    Ø1.5 mm × 0.8 mm locating bosses.
- The plug enters from the +Y side. The Ø5.0 mm nose sticks out 2.5 mm past
  the body, so align the body front with the board edge or enclosure wall
  as needed.
- Ratings: 12 V DC, 1 A, −25 to +85 °C, 5,000 cycles.
- Datasheet: [SJ-352X-SMT](https://www.sameskydevices.com/product/resource/sj-352x-smt.pdf).

The 3D model is built from datasheet dimensions: body, nose, bore, bosses and
terminal feet. Same Sky's own CAD downloads are behind a login and were not
used.
