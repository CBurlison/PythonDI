import timeit
from PythonDI import *
from pydantic import BaseModel

#execution_count = 100_000_000
execution_count = 10_000_000

def perf_test_di():
    di = DIContainer()
    di.register(OtherResponse)
    di.register(GoodbyeResponse)
    di.register(HelloResponse)

    for _ in range(execution_count):
        _ = di.locate(HelloResponse, ["Hello"])

def perf_test_di_pydantic():
    di = DIContainer()
    di.register(PydanticOtherResponse)
    di.register(PydanticGoodbyeResponse)
    di.register(PydanticHelloResponse)

    for _ in range(execution_count):
        _ = di.locate(PydanticHelloResponse, ["Hello"])

def perf_test_manual():
    for _ in range(execution_count):
        _ = HelloResponse(body="Hello", goodbye=GoodbyeResponse(test=OtherResponse(test=0, body="")))

def perf_test_manual_pydantic():
    for _ in range(execution_count):
        _ = PydanticHelloResponse(body="Hello", goodbye=PydanticGoodbyeResponse(test=PydanticOtherResponse(test=0, body="")))

def main():
    print("Running performance tests.")
    print("Now running: DI test")
    di = timeit.timeit(stmt=perf_test_di, number=1)
    print("Now running: Pydantic DI test")
    pydantic_di = timeit.timeit(stmt=perf_test_di_pydantic, number=1)
    print("Now running: Manual test")
    manual = timeit.timeit(stmt=perf_test_manual, number=1)
    print("Now running: Pydantic Manual test")
    pydantic_manual = timeit.timeit(stmt=perf_test_manual_pydantic, number=1)

    print("\nResults\nTest\t\t\tRuntime (sec)")
    print(f"DI test\t\t\t{di:.2f}")
    print(f"Pydantic DI test\t{pydantic_di:.2f}")
    print(f"Manual test\t\t{manual:.2f}")
    print(f"Pydantic Manual test\t{pydantic_manual:.2f}")

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
        
class PydanticOtherResponse(BaseModel):
    test: int = 0
    body: str = ""

class PydanticGoodbyeResponse(BaseModel):
    test: PydanticOtherResponse = None

class PydanticHelloResponse(BaseModel):
    body: str = ""
    goodbye: PydanticGoodbyeResponse = None

if __name__ == "__main__":
    main()