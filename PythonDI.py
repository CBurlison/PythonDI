import inspect
from enum import Enum
from pydantic import BaseModel
import typing

class UnregisteredAction(Enum):
    NONE = 0
    DEFAULT = 1
    EXCEPTION = 2
    REGISTER = 3

class TypeConstructor:
    def __init__(self, object_type: type, constructor: dict[str, type]):
        self.base_type: type = object_type

        if issubclass(object_type, BaseModel) and "return" in constructor:
            self.is_pydantic: bool = True
            constructor.pop("return")
        else:
            self.is_pydantic = False

        self.constructor: dict[str, type] = constructor
        self.keys: list[str] = list(constructor.keys())

class UnregisteredType(Exception): 
    pass

class DIContainer:
    def __init__(self, unregistered_action: UnregisteredAction = UnregisteredAction.DEFAULT):
        self.__type_constructors: dict[type, TypeConstructor] = {}
        self.__type_instances: dict[type, typing.Any] = {}

        if unregistered_action == UnregisteredAction.DEFAULT:
            self.__unregistered_action = self.__unregistered_default
        elif unregistered_action == UnregisteredAction.NONE:
            self.__unregistered_action = self.__unregistered_none
        elif unregistered_action == UnregisteredAction.EXCEPTION:
            self.__unregistered_action = self.__unregistered_exception
        elif unregistered_action == UnregisteredAction.REGISTER:
            self.__unregistered_action = self.__unregistered_register

    # register an object type for future construction
    def register(self, object_type: type):
        constructor: dict[str, typing.Any]
        
        try:
            constructor = inspect.getfullargspec(object_type).annotations
        except(TypeError):
            constructor = {}

        self.__type_constructors[object_type] = TypeConstructor(object_type, constructor)
        
    # register an object type instance
    def register_instance(self, object_type: type, instance=None):
        self.register(object_type)
        self.__type_instances[object_type] = instance

    # locate existing instance or construct new object
    def locate(self, object_type: type, params=[]) -> typing.Any:
        # locate registered instance/singleton
        if object_type in self.__type_instances:
            value = self.__type_instances[object_type]

            if value is None:
                value = self.__inner_locate(object_type, params)
                self.__type_instances[object_type] = value

            return value
        # construct dymanic object
        else:
            return self.__inner_locate(object_type, params)

    # locate all objects associated with the given object_type
    def locate_all(self, object_type: type, params=[]) -> list[typing.Any]:
        all: list[typing.Any] = []

        for item in self.__type_constructors.values():
            if issubclass(item.base_type, object_type):
                all.append(self.locate(item.base_type, params))

        return all

    # private: construct a new object
    def __inner_locate(self, object_type: type, params=[]) -> typing.Any:
        if object_type not in self.__type_constructors:
            return self.__unregistered_action(object_type, params)
               
        di_constructor = self.__type_constructors[object_type]
        
        if di_constructor.is_pydantic:
            return self.__construct_base_model(di_constructor, object_type, params)
        
        return self.__construct_type(di_constructor, object_type, params)
    
    def __construct_type(self, di_constructor: TypeConstructor, object_type: type, params=[]):
        args: list[typing.Any] = []
        params_len = len(params)

        for i in range(len(di_constructor.constructor)):
            if (i < params_len):
                args.append(params[i])
            else:
                key = di_constructor.keys[i]
                args.append(self.locate(di_constructor.constructor[key]))

        return object_type(*args)
    
    def __construct_base_model(self, di_constructor: TypeConstructor, object_type: type, params=[]):
        obj = object_type()
        params_len = len(params)

        for i in range(len(di_constructor.constructor)):
            key = di_constructor.keys[i]

            if (i < params_len):
                setattr(obj, key, params[i])
            else:
                setattr(obj, key, self.locate(di_constructor.constructor[key]))

        return obj
    
    def __unregistered_default(self, object_type: type, params: list[typing.Any]):
        return object_type()
    
    def __unregistered_none(self, object_type: type, params: list[typing.Any]):
        return None
    
    def __unregistered_exception(self, object_type: type, params: list[typing.Any]):
        raise UnregisteredType(f"{object_type} not registered with DIContainer.")
    
    def __unregistered_register(self, object_type: type, params: list[typing.Any]):
        self.register(object_type)
        return self.__inner_locate(object_type, params)
