#!/usr/bin/env python

import sys

# HW instructions indicate the map/reduce doesn't actually do anything, end-goal is to write as avro format
# Professor comment in Piazza: "Problem 3 does not run any queries - it only converts your plain text input data into Avro output data:"
# so we simply consume the  files that are fed in and print them out
for line in sys.stdin:

    print(line)