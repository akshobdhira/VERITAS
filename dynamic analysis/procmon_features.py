import pandas as pd
import sys

file_path = sys.argv[1]

df = pd.read_csv(file_path)

proc_count = df["Process Name"].nunique()
file_write_count = df[df["Operation"] == "WriteFile"].shape[0]
registry_write_count = df[df["Operation"].str.contains("RegSetValue", na=False)].shape[0]
network_attempts = df[df["Operation"].str.contains("TCP|UDP", na=False)].shape[0]

print("proc_count:", proc_count)
print("file_write_count:", file_write_count)
print("registry_write_count:", registry_write_count)
print("network_attempts:", network_attempts)