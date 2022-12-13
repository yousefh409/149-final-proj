#!/usr/bin/env python
from time import sleep
from sys import stdout
import json

i = 0

while True:
    if i >= 20:
        print('\n', end='')
    else:
        obj = {"i" : i}
        print(json.dumps(obj))
        stdout.flush()
        i = i + 1
        sleep(0.1)
