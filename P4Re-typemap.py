#!/usr/bin/env python
import subprocess

output = subprocess.check_output("p4 typemap -o", shell=True).decode()
for typemap in output.rpartition('TypeMap:')[-1].splitlines():
    if typemap:
        print("%s" % typemap)
        subprocess.call("p4 retype -t %s" % typemap, shell=True)