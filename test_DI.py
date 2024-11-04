from PythonDI import *
import pytest
from pydantic import BaseModel

def test_register():
    di = DIContainer()
    di.register(HelloResponse)

def test_locate():
    di = DIContainer()
    di.register(HelloResponse)

    response = di.locate(HelloResponse, [])
    assert response is not None # HelloResponse located
    assert response.body == "" # body populated with default value for str
    assert response.goodbye is not None # GoodbyeResponse not registered. default value used
    assert response.goodbye.test is None # TestResponse not located because GoodbyeResponse was default. test never populated

def test_locate_unregistered_none():
    di = DIContainer(UnregisteredAction.NONE)
    di.register(HelloResponse)

    response = di.locate(HelloResponse, [])
    assert response is not None # HelloResponse located
    assert response.body is None # str not registered. value is None
    assert response.goodbye is None # GoodbyeResponse not registered. value is None

def test_locate_unregistered_exception():
    di = DIContainer(UnregisteredAction.EXCEPTION)
    di.register(HelloResponse)

    with pytest.raises(UnregisteredType) as ex:
        _ = di.locate(HelloResponse, [])

    assert ex.value.args[0] == f"{str} not registered with DIContainer."

def test_locate_unregistered_register():
    di = DIContainer(UnregisteredAction.REGISTER)
    di.register(HelloResponse)

    _ = di.locate(HelloResponse, [])

    response = di.locate(HelloResponse, [])
    assert response is not None # HelloResponse located
    assert response.body == "" # body populated with default value for str
    assert response.goodbye is not None # GoodbyeResponse located
    assert response.goodbye.test is not None # TestResponse located
    assert response.goodbye.test.test == 0 # TestResponse.test populated with default value for int
    assert response.goodbye.test.body == "" # TestResponse.body populated with default value for str

def test_locate_dependencies():
    di = DIContainer()
    di.register(OtherResponse)
    di.register(GoodbyeResponse)
    di.register(HelloResponse)

    response = di.locate(HelloResponse, [])
    assert response is not None # HelloResponse located
    assert response.body == "" # body populated with default value for str
    assert response.goodbye is not None # GoodbyeResponse located
    assert response.goodbye.test is not None # TestResponse located
    assert response.goodbye.test.test == 0 # TestResponse.test populated with default value for int
    assert response.goodbye.test.body == "" # TestResponse.body populated with default value for str

def test_locate_pydantic_dependencies():
    di = DIContainer()
    di.register(PydanticOtherResponse)
    di.register(PydanticGoodbyeResponse)
    di.register(PydanticHelloResponse)

    response = di.locate(PydanticHelloResponse, [])
    assert response is not None # HelloResponse located
    assert response.body == "" # body populated with default value for str
    assert response.goodbye is not None # GoodbyeResponse located
    assert response.goodbye.test is not None # TestResponse located
    assert response.goodbye.test.test == 0 # TestResponse.test populated with default value for int
    assert response.goodbye.test.body == "" # TestResponse.body populated with default value for str

def test_locate_dependencies_mixed():
    di = DIContainer()
    di.register(OtherResponse)
    di.register(GoodbyeResponse)
    di.register(HelloResponse)
    di.register(PydanticOtherResponse)
    di.register(PydanticGoodbyeResponse)
    di.register(PydanticHelloResponse)
    di.register(MixedResponse)

    response: MixedResponse = di.locate(MixedResponse, [])
    assert response is not None # HelloResponse located
    assert response.hello is not None
    assert response.hello.body == "" # body populated with default value for str
    assert response.hello.goodbye is not None # GoodbyeResponse located
    assert response.hello.goodbye.test is not None # TestResponse located
    assert response.hello.goodbye.test.test == 0 # TestResponse.test populated with default value for int
    assert response.hello.goodbye.test.body == "" # TestResponse.body populated with default value for str
    
    assert response.py_hello is not None
    assert response.py_hello is not None
    assert response.py_hello.body == "" # body populated with default value for str
    assert response.py_hello.goodbye is not None # GoodbyeResponse located
    assert response.py_hello.goodbye.test is not None # TestResponse located
    assert response.py_hello.goodbye.test.test == 0 # TestResponse.test populated with default value for int
    assert response.py_hello.goodbye.test.body == "" # TestResponse.body populated with default value for str

def test_locate_with_param():
    di = DIContainer()
    di.register(HelloResponse)

    response = di.locate(HelloResponse, ["Hello"])
    assert response is not None # HelloResponse located
    assert response.body == "Hello" # body param applies

def test_locate_with_param_pydantic():
    di = DIContainer()
    di.register(PydanticHelloResponse)

    response = di.locate(PydanticHelloResponse, ["Hello"])
    assert response is not None # HelloResponse located
    assert response.body == "Hello" # body param applies

def test_register_instance():
    di = DIContainer()
    di.register_instance(B, B())

def test_register_instance_none():
    di = DIContainer()
    di.register_instance(B)

def test_locate_instance():
    di = DIContainer()
    b1 = B()

    di.register_instance(B, b1)
    b2 = di.locate(B)
    assert b1 == b2

def test_locate_instance_none():
    di = DIContainer()

    di.register_instance(B)
    b1 = di.locate(B)
    b2 = di.locate(B)
    assert b1 == b2

def test_locate_all():
    di = DIContainer()
    di.register(A)
    di.register(B)
    di.register(C)
    d = D()
    di.register_instance(D, d)

    # locate_all test
    all_A = di.locate_all(A)
    assert len(all_A) == 4 # Includes A, B, C, and D
    assert d in all_A

    all_B = di.locate_all(B)
    assert len(all_B) == 2 # Includes B and C
    assert d not in all_B

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

class MixedResponse:
    def __init__(self, hello: HelloResponse = None, py_hello: PydanticHelloResponse = None):
        self.hello = hello
        self.py_hello = py_hello
        
class A: pass

class B(A): pass

class C(B): pass

class D(A): pass