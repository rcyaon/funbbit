#!/usr/bin/env python3
"""Envelope-detector checks for modules/audio_sense.zen (run from this directory).

1. Burst transient (test_audio_sense_envelope.zen, vendor op amp model):
   envelope levels, 63 % attack, 37 % release.
2. Comparator trip points: same netlist with channel B swapped for a
   behavioral comparator (the MCP6041 Rev D macro model is linear-region only),
   tone ramped 0 -> 80 mV rms -> 0 at 100 Hz.
3. Top of range: 1 V rms at VBAT = 3.0 V and 2.7 V.
"""
import os
import re
import subprocess

import numpy as np

os.makedirs("output", exist_ok=True)
subprocess.run(["pcb", "sim", "test_audio_sense_envelope.zen", "-o", "output/envelope.cir"], check=True)
base = open("output/envelope.cir").read()


def ngspice(name, text):
    path = f"output/{name}.cir"
    open(path, "w").write(text)
    log = subprocess.run(["ngspice", "-b", path], capture_output=True, text=True, timeout=900).stdout
    return {m.group(1): float(m.group(2)) for m in re.finditer(r"^(\w+)\s+=\s+([-+0-9.eE]+)", log, re.M)}


def with_control(text, source, control):
    text = re.sub(r"B_SRC SRC GND V = .*", "B_SRC SRC GND V = " + source, text)
    return re.sub(r"\.control.*?\.endc\n", ".control\n" + control + ".endc\n", text, flags=re.S)


# 1. Burst transient.
burst = ngspice("burst", base)
d = np.loadtxt("output/envelope.txt")
t, env = d[:, 0], d[:, 1]
e50 = env[(t > 0.6) & (t < 0.8)].mean()
e300 = env[(t > 1.4) & (t < 1.6)].mean()
rest = env[-1]
attack = t[np.where((t > 0.8) & (env >= e50 + 0.632 * (e300 - e50)))[0][0]] - 0.8
release = t[np.where((t > 1.6) & (env <= rest + 0.368 * (e300 - rest)))[0][0]] - 1.6
print(f"VMID {burst['vmid']:.4f} V | ENV-VMID: 50 mV rms -> {e50*1e3:.1f} mV, 300 mV rms -> {e300*1e3:.1f} mV")
print(f"attack (63 %) {attack*1e3:.1f} ms | release (37 %) {release*1e3:.1f} ms | front-end current {-burst['i_quiescent']*1e6:.2f} uA")

# 2. Comparator trip points with a behavioral channel B.
behavioral = """.SUBCKT CMP_BEH INP INN VDD VSS OUT
B1 n1 VSS V = V(VDD,VSS) / (1 + exp(-(V(INP)-V(INN))*20000))
R1 n1 OUT 1k
C1 OUT VSS 330n
.ENDS CMP_BEH
"""
cmp_net = base.replace("XB INBP INBN VDD VSS OUTB MCP6041", "XB INBP INBN VDD VSS OUTB CMP_BEH")
cmp_net = cmp_net.replace(".SUBCKT MCP6042", behavioral + ".SUBCKT MCP6042", 1)
ramp = "(time < 4 ? 0.11314*time/4 : (time < 5 ? 0.11314 : (time < 9 ? 0.11314*(9-time)/4 : 0))) * sin(2*3.14159265*100*time)"
control = """  tran 25u 10 0 50u
  let env = v(ENV_OUT) - v(AUDIO_VMID)
  meas tran t_on when v(MUSIC_PRESENT)=1.5 rise=1
  meas tran t_off when v(MUSIC_PRESENT)=1.5 fall=1
  meas tran env_on find env when v(MUSIC_PRESENT)=1.5 rise=1
  meas tran env_off find env when v(MUSIC_PRESENT)=1.5 fall=1
  meas tran mp_end find v(MUSIC_PRESENT) at=10
"""
c = ngspice("comparator", with_control(cmp_net, ramp, control))
on_rms = 80 * c["t_on"] / 4
off_rms = 80 * (9 - c["t_off"]) / 4
print(f"MUSIC_PRESENT on at {on_rms:.1f} mV rms (ENV-VMID {c['env_on']*1e3:.1f} mV), "
      f"off at {off_rms:.1f} mV rms (ENV-VMID {c['env_off']*1e3:.1f} mV), silence -> {c['mp_end']:.3f} V")

# 3. Top of range.
for vbat in ("3.0", "2.7"):
    net = base.replace("V_BAT VBAT GND DC 3.0", f"V_BAT VBAT GND DC {vbat}")
    top = ngspice(f"top_{vbat}", with_control(net, "(time < 0.8 ? 1.41421 : 0) * sin(2*3.14159265*100*time)",
                  "  tran 20u 1.0 0 50u\n  let env = v(ENV_OUT) - v(AUDIO_VMID)\n  meas tran env_1v avg env from=0.6 to=0.8\n"))
    print(f"VBAT {vbat} V: 1 V rms -> ENV-VMID {top['env_1v']*1e3:.0f} mV")
