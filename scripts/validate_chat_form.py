#!/usr/bin/env python3
import sys, yaml, pathlib

if len(sys.argv) != 3:
    print("usage: validate_chat_form.py <expected_top_key> <input_yaml_path>", file=sys.stderr)
    sys.exit(2)

top_key, path = sys.argv[1], pathlib.Path(sys.argv[2])
data = yaml.safe_load(path.read_text(encoding="utf-8"))

if not isinstance(data, dict) or list(data.keys()) != [top_key]:
    print(f"ERROR: top-level key must be exactly '{top_key}'", file=sys.stderr)
    sys.exit(1)

print("OK")
