import json
import sys

# Usage:
# python dyn_out_to_json.py proc_count file_write_count registry_write_count network_attempts out.json
proc_count = int(sys.argv[1])
file_write_count = int(sys.argv[2])
registry_write_count = int(sys.argv[3])
network_attempts = int(sys.argv[4])
out_path = sys.argv[5]

data = {
    "proc_count": proc_count,
    "file_write_count": file_write_count,
    "registry_write_count": registry_write_count,
    "network_attempts": network_attempts
}

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("[OK] wrote", out_path)