import sys

lines = open(sys.argv[1]).readlines()

ids = set()
for l in lines:
    line = l.strip()
    parts = line.split(" ")
    v = parts[4].split("\t")
    ids.add(v[1])

print(len(ids))
print(ids)

