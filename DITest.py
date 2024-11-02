from PythonDI import DIContainer 

def main():
    di = DIContainer()
    di.register_instance(DIContainer, di)
    di.register(TestResponse)
    di.register(GoodbyeResponse)
    di.register(HelloResponse)

    di.register_instance(D, D())
    di.register(A)
    di.register(B)
    di.register(C)

    all_A = di.locate_all(A)
    assert(len(all_A) == 4) # Includes A, B, C, and D

    all_B = di.locate_all(B)
    assert(len(all_B) == 2) # Includes B and C

    response = di.locate(HelloResponse, ["Hello"])
    assert(response is not None) # HelloResponse located
    assert(response.body == "Hello") # body param applies
    assert(response.goodbye is not None) # GoodbyeResponse located
    assert(response.goodbye.test is not None) # TestResponse located
    assert(response.goodbye.test.test == 0) # TestResponse.test populated with default value for int
    assert(response.goodbye.test.body == "") # TestResponse.body populated with default value for str

    print("All tests pass!")

class TestResponse:
    def __init__(self, test: int, body: str = ""):
        self.test = test
        self.body = body

class GoodbyeResponse:
    def __init__(self, test: TestResponse):
        self.test = test

class HelloResponse:
    def __init__(self, body: str, goodbye: GoodbyeResponse):
        self.body = body
        self.goodbye = goodbye

class A: pass

class B(A): pass

class C(B): pass

class D(A): pass

if __name__ == "__main__":
    main()