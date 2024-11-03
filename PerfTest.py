import timeit
from PythonDI import DIContainer

def perf_test_di():
    di = DIContainer()
    di.register(OtherResponse)
    di.register(GoodbyeResponse)
    di.register(HelloResponse)

    for i in range(100_000_000):
        _ = di.locate(HelloResponse, ["Hello"])

def perf_test_manual():
    for i in range(100_000_000):
        _ = HelloResponse(body="Hello", goodbye=GoodbyeResponse(test=OtherResponse(test=0, body="")))

def main():
    print("Running performance tests.")
    print("Now running: DI test")
    di = timeit.timeit(stmt=perf_test_di, number=1)
    print("Now running: Manual test")
    manual = timeit.timeit(stmt=perf_test_manual, number=1)

    print("\nResults\nTest\t\t\tRuntime (sec)")
    print(f"DI test\t\t\t{di:.2f}")
    print(f"Manual test\t\t{manual:.2f}")

class OtherResponse:
    def __init__(self, test: int, body: str):
        self.test = test
        self.body = body

class GoodbyeResponse:
    def __init__(self, test: OtherResponse = None):
        self.test = test

class HelloResponse:
    def __init__(self, body: str, goodbye: GoodbyeResponse):
        self.body = body
        self.goodbye = goodbye

if __name__ == "__main__":
    main()