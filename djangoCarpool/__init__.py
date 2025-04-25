class MyType(type):
    def __new__(cls, name, bases, attrs):
        # Add a custom attribute to the class
        attrs['custom_attribute'] = 'This is a custom attribute'
        # print(f"Creating class {name} with custom attribute")
        return super().__new__(cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        print(f"Creating instance of {cls.__name__}")
        instance = cls.__new__(cls, *args, **kwargs)
        return instance


class Base(metaclass=MyType):
    def __init__(self):
        self.name = 'Base'

    def greet(self):
        print(f"Hello from {self.name}")


class Derived(Base):
    def __init__(self):
        super().__init__()
        self.name = 'Derived'

    def __new__(cls, *args, **kwargs):
        print("Derived instance called")
        return super().__new__(cls)


obj = Derived()
print(obj.__str__())
