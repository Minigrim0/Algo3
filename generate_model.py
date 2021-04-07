import sys

if len(sys.argv) < 3:
    print("usage : python3 ")


filepath, p = sys.argv[1:]
with open(filepath) as f:
    a = f.readline()
    i, j, k = a.split()
    print(i, j, k)
