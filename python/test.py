class A:
    def __init__(self):
        self.b = B()

    def run(self):
        c = self.b.c
        c = 1

        self.b.c = c

        return self


class B:
    def __init__(self):
        self.c = 0

a = A()
a = a.run()
print(a)