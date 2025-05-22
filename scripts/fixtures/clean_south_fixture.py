#!/usr/bin/env python

# This small script removes from fixtures
# every entries that would have been added by South :
# - 'applied' fields
# - 'south.*' models

import json
import sys

filepath = sys.argv[1]

with open(filepath) as f:
    data = json.load(f)
    res = []
    for obj in data:
        if obj['model'].startswith('south.'):
            # Skipping South model entry
            continue
        if 'applied' in obj['fields']:
            del obj['fields']['applied']
        res.append(obj)
    print(json.dumps(res, indent=4))
