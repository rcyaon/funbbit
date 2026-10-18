# DMP2045U-7

Diodes Incorporated P-channel enhancement MOSFET, −20 V, −4.3 A, 45 mΩ max at V_GS −4.5 V, SOT-23.
[Datasheet DS40478](https://www.diodes.com/assets/Datasheets/DMP2045U.pdf)

```python
DMP2045U = Module("code.diode.computer/lena/registry/components/Diodes_Incorporated/DMP2045U-7/DMP2045U-7.zen")
DMP2045U(name="Q1", G=en_n, S=vin, D=vout)
```

IO: `G`, `S`, `D` (Net). Pinout is 1 G, 2 S, 3 D.

Notes:
- This is Diodes' recommended replacement for the NRND DMG3415U. The pinout, footprint and API are the same, but the electrical ratings differ:
  - R_DS(on) is higher at low gate drive: 90 mΩ max at −1.8 V, vs 71 mΩ for DMG3415U.
  - Input capacitance Ciss is about 2× higher: 634 pF vs 294 pF.
  - Gate resistance Rg is 20 Ω vs 250 Ω.
- V_GS is limited to ±8 V.
- Footprint: Diodes SOT23 suggested pad layout (pads 0.8 × 0.9 mm, C 2.0 mm, X1 1.35 mm).
- 3D model: generated from the datasheet outline. Its height is 1.20 mm (A1 max plus A2 max), slightly above the 1.15 mm A max.
- No SPICE model is included.
