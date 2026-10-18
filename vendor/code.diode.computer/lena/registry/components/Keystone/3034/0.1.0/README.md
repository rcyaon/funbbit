# Keystone 3034TR

SMT ultra-low-profile retainer for one 20 mm coin cell (CR2032, CR2025,
2020). It is 4.06 mm high and nickel-plated phosphor bronze. 3034TR is the tape
and reel version and 3034 the same part in bulk; 3034 is listed as an
alternative.

## Usage

```zen
Coin = Module("@registry/components/Keystone/3034/3034.zen")

Coin(
    name = "BT1",
    POS = VBAT,
    NEG = GND,
)
```

- **Positive (`POS`, pad 1):** the retainer, soldered by the two side tabs.
- **Negative (`NEG`, pad 2):** a bare-copper PCB pad under the centre of the
  cell, with a solder-mask opening and **no paste**. Keystone drawing 3034
  rev F specifies at least 3.96 mm (.156 in) square on the tab centreline. This
  footprint uses 4.0 × 4.0 mm. Use ENIG or another corrosion-resistant finish.
- **Tab lands:** Keystone minimums are 1.27 × 5.08 mm on a 23.24 mm outer span.
  These lands are 1.77 × 5.60 mm: same inner edge, 0.5 mm longer outward for
  the toe fillet.
- Keep other exposed copper, vias and test points out from under the cell.
  The cell's positive can overhangs the open (+Y) front of the retainer. The
  courtyard includes the 20 mm cell outline, which assumes the cell is
  centred on the pad axis. Leave room at the front edge to slide the cell in.
- Datasheets: [catalog p11](https://www.keyelco.com/userAssets/file/K75p11.pdf),
  [drawing 3034](https://www.keyelco.com/product-pdf.cfm?p=798).

The 3D model is a simplified sheet-metal shell (top plate with the rear arc,
front chamfers and spring windows, side walls and tabs) at the drawing's
outer dimensions of 23.24 × 16.41 × 4.06 mm. It does not show the cell or the
spring finger shapes.
