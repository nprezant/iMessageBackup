def create1k():
    s = ""
    for i in range(1024):
        s += '*'
    return s

def create1m():
    s = ""
    x = create1k()
    for i in range(1024):
        s += x
    return s

def create1g():
    s = ""
    x = create1m()
    for i in range(1024):
        s += x
    return s

def string_size_test():
    print("begin")
    s = ""
    x = create1g()
    for i in range(1024):
        s += x
        print(str(i) + "g ok")
        print(str(len(s)) + ' bytes')

if __name__ == '__main__':
    string_size_test()
