# PythonDI
A simple DI Container script for python

This DI container comes with 4 simple functions to facilitate the Dependency Injection workflow. In order PythonDI to work all registered objects must have __init__ functions with strongly defined types. The only exception to this is if "register_instance" is being used and the instance of that object is included.

### DIContainer(default_if_unregistered: bool = True)
when default_if_unregistered is True, __init__ values that are not registered will be initialized with their default values of type(). When false they will be set to None.

## Functions
### register(object_type: type)
"register" registers the object type to the DI Container, allowing it to be located and constructed.

### register_instance(self, object_type: type, instance=None)
"register_instance" registers a single instance of an object to the DI Container. If no instance is included, the first time one is located it will be saved.

### locate(self, object_type: type, params=[]) -> any
"locate" finds an existing instance of the given object type or constructs a new one.

### locate_all(self, object_type: type, params=[]) -> list[any]
"locate_all" finds all existing instance of registered objects associated with the given object type or constructs a new ones.

Examples of all functions can be found in test_DI.py

```python
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
    
def test_locate_with_param():
    di = DIContainer()
    di.register(HelloResponse)

    response = di.locate(HelloResponse, ["Hello"])
    assert response is not None # HelloResponse located
    assert response.body == "Hello" # body param applies

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

# test classes
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

class A: pass

class B(A): pass

class C(B): pass

class D(A): pass
```
