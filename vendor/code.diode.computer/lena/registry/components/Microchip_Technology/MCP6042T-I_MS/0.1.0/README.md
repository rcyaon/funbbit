# MCP6042T-I/MS

Microchip dual 600 nA/channel, 14 kHz rail-to-rail I/O CMOS op amp, MSOP-8, 1.4 V to 6.0 V.
[Datasheet DS20001669E](https://ww1.microchip.com/downloads/en/DeviceDoc/20001669e.pdf)

```python
load("@stdlib/interfaces.zen", "Opamp")
MCP6042 = Module("code.diode.computer/lena/registry/components/Microchip_Technology/MCP6042T-I_MS/MCP6042T-I_MS.zen")

MCP6042(name="U1", VDD=vdd, VSS=gnd,
        A=Opamp(IN_P=sense, IN_N=buf, OUT=buf),
        B=Opamp(IN_P=ref, IN_N=fb, OUT=out))
```

IO: `VDD` (Power, 1.4–6.0 V), `VSS` (Ground), `A`/`B` (`Opamp`: `IN_P`, `IN_N`, `OUT`).

Integration notes:
- Add a 0.01–0.1 µF bypass capacitor within 2 mm of VDD (pin 8) (datasheet §4.6).
- Capacitive loads need an output isolation resistor (§4.2, Fig. 4-4).
- Input bias is pA-level; guard high-impedance inputs against board leakage (§4.7).
- Footprint: Microchip land pattern C04-2111A (C 4.40, X1 0.45, Y1 1.45 mm); 3D model generated from C04-111C.
- SPICE: Microchip MCP6041 macro model Rev D (license header retained), wrapped as `MCP6042` with nodes in pin order. Verified in ngspice via `pcb sim`: follower and gain-of-2 DC points correct, about 1.2 µA total quiescent current at 3 V.
