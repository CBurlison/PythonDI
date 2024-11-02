# PythonDI
A simple DI Container script for python

This DI container comes with 4 simple functions to facilitate the Dependency Injection workflow. In order PythonDI to work all registered objects must have __init__ functions with strongly defined types. The only exception to this is if "register_instance" is being used and the instance of that object is included.

## Functions
### register(object_type: type)
"register" registers the object type to the DI Container, allowing it to be located and constructed.

### register_instance(self, object_type: type, instance=None)
"register_instance" registers a single instance of an object to the DI Container. If no instance is included, the first time one is located it will be saved.

### locate(self, object_type: type, params=[]) -> any
"locate" finds an existing instance of the given object type or constructs a new one.

### locate_all(self, object_type: type, params=[]) -> list[any]
"locate_all" finds all existing instance of registered objects associated with the given object type or constructs a new ones.

Examples of all functions can be found in DITest.py
