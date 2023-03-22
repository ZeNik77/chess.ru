a = int(input())
f = [1]
for i in range(1, 10 ** 5):
    print(f[i-1] * i)
    f.append(f[i-1] * i)
print(f[4])

