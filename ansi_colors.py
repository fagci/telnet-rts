for i in range(16):
    for j in range(16):
        v = str(i * 16 + j)
        print(f'\033[48;5;{v}m {v.ljust(4)}', end='')
    print('\033[0m')
