#!/usr/bin/env python
from subprocess import Popen, PIPE, STDOUT
import json

p = Popen('python printer.py'.split(), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
if p.stdout is None:
    print("ERROR")
    exit(1)

for line in p.stdout:
    if line.strip():
        obj = json.loads(line.decode())
        print(obj)
    else:
        break
