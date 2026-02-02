import json
import sys

consolidated_json = sys.argv[1]

with open(consolidated_json, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if line.strip():
            entry = json.loads(line)
            print(json.dumps(entry, indent=2))
            break  # just show the first line
