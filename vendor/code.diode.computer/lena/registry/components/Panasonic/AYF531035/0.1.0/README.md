# Panasonic AYF531035

10-contact, 0.5 mm pitch FPC/FFC connector from Panasonic's Y5B series. It is
right-angle SMT, 1.00 mm high and back lock. Contacts sit on both the top and
bottom of the slot, so it mates with an FPC/FFC whose exposed conductors face
**either up or down**. Use FPC/FFC 0.30 ± 0.03 mm thick and 5.50 mm wide.

AYF531035 is a Y5B part without FPC holding contacts. The Y5BW 10-pin part is
AYF531065T. This package has the 10 contacts plus the two soldering terminals
(`MP`).

## Usage

```zen
Fpc = Module("@registry/components/Panasonic/AYF531035/AYF531035.zen")

Fpc(
    name = "J1",
    P1 = GND,
    P2 = SDA,
    P3 = SCL,
    # ... P4..P10
    MP = GND,
)
```

- **Numbering:** Panasonic does not number the contacts. Here, contact 1 is
  at the left (x = −2.25 mm) in the top view with the FPC entering from the
  top edge, at the silkscreen triangle.
- **Cable orientation:** turning the FPC over reverses the order (contact N
  meets conductor 11−N). Decide which way the conductors face, then check the
  pin-1 sense against the cable drawing.
- **MP** is the pair of soldering terminals. They are for mechanical retention
  only and are not rated as conductors.
- **Land pattern** (catalog p7): contact lands are 0.30 × 0.80 mm, terminal
  lands 0.40 × 0.80 mm with 3.30 mm overall depth, and terminal centres sit
  1.00 mm outboard of contacts 1 and 10. The stencil follows the
  catalog's metal-mask pattern for a 120 µm stencil: 0.25 × 0.55 mm on each
  contact, flush with the FPC-side edge, and 100 % on the terminals.
- Keep the FPC entry side (the top edge of the footprint) at the board edge
  or clear of tall parts, and leave about 0.5 mm behind the body for the
  lever to swing (3.70 mm open).
- Ratings: 0.5 A per contact, 50 V, −55 to +85 °C, 20 mating cycles.
- Datasheet: [Y5B/Y5BW catalog](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/9053/Y5B-W.pdf).

The 3D model was built from catalog dimensions with the lever closed:
7.00 × 3.20 × 1.00 mm, with contact tails and soldering terminals.
