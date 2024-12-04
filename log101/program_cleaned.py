(t, s, x) = map(int, input().split())
if (x - t) % s == 0 or (x - t) % s == 1:
    print('YES')
else:
    print('NO')