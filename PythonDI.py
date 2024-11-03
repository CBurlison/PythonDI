import inspect
from enum import Enum

class UnregisteredAction(Enum):
    NONE = 0
    DEFAULT = 1
    EXCEPTION = 2
    REGISTER = 3

class TypeConstructor:
    base_type: type = None
    constructor: dict[str, type] = None
    keys: list[str] = None
    classes: tuple[type, ...] = None
    
    def __init__(self, object_type: type, constructor: dict[str, type]):
        self.base_type = object_type
        self.classes = inspect.getmro(object_type)
        self.constructor = constructor
        self.keys = [key for key in constructor.keys()]

class UnregisteredType(Exception): pass

class DIContainer:
    __type_constructors: dict[type, TypeConstructor] = {}
    __type_instances: dict[type, any] = {}

    def __init__(self, unregistered_action: UnregisteredAction = UnregisteredAction.DEFAULT):
        match unregistered_action.value:
            case UnregisteredAction.DEFAULT.value:
                self.__unregistered_action = self.__unregistered_default
            case UnregisteredAction.NONE.value:
                self.__unregistered_action = self.__unregistered_none
            case UnregisteredAction.EXCEPTION.value:
                self.__unregistered_action = self.__unregistered_exception
            case UnregisteredAction.REGISTER.value:
                self.__unregistered_action = self.__unregistered_register

    # register an object type for future construction
    def register(self, object_type: type):
        constructor: dict[str, any]
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
    def locate(self, object_type: type, params=[]) -> any:
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
    def locate_all(self, object_type: type, params=[]) -> list[any]:
        all: list[any] = []

        for item in self.__type_constructors.values():
            if object_type in item.classes:
                all.append(self.locate(item.base_type, params))

        return all

    # private: construct a new object
    def __inner_locate(self, object_type: type, params=[]) -> any:
        if object_type not in self.__type_constructors:
            return self.__unregistered_action(object_type, params)
               
        args: list[any] = []
        di_constructor = self.__type_constructors[object_type]
        params_len = len(params)

        for i in range(len(di_constructor.constructor)):
            if (i < params_len):
                args.append(params[i])
            else:
                key = di_constructor.keys[i]
                args.append(self.locate(di_constructor.constructor[key]))

        return object_type(*args)
    
    def __unregistered_default(self, object_type: type, params: list[any]):
        return object_type()
    
    def __unregistered_none(self, object_type: type, params: list[any]):
        return None
    
    def __unregistered_exception(self, object_type: type, params: list[any]):
        raise UnregisteredType(f"{object_type} not registered with DIContainer.")
    
    def __unregistered_register(self, object_type: type, params: list[any]):
        self.register(object_type)
        return self.__inner_locate(object_type, params)
