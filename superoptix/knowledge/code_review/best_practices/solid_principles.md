# SOLID Principles

## Overview
SOLID is an acronym for five design principles that make software more maintainable and flexible.

## S - Single Responsibility Principle (SRP)

**"A class should have only one reason to change"**

### ❌ Multiple Responsibilities
```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def save_to_database(self):
        # Database logic
        db.insert('users', self.__dict__)
    
    def send_welcome_email(self):
        # Email logic
        send_email(self.email, "Welcome!")
    
    def generate_report(self):
        # Reporting logic
        return f"User Report: {self.name}"
```

### ✅ Single Responsibility
```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    def save(self, user):
        db.insert('users', user.__dict__)

class EmailService:
    def send_welcome(self, user):
        send_email(user.email, "Welcome!")

class ReportGenerator:
    def generate_user_report(self, user):
        return f"User Report: {user.name}"
```

## O - Open/Closed Principle (OCP)

**"Open for extension, closed for modification"**

### ❌ Modifying Existing Code
```python
def calculate_area(shape):
    if shape.type == 'circle':
        return 3.14 * shape.radius ** 2
    elif shape.type == 'rectangle':
        return shape.width * shape.height
    # Need to modify this function for each new shape!
```

### ✅ Extension Through Inheritance
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

# Add new shapes without modifying existing code!
```

## L - Liskov Substitution Principle (LSP)

**"Subtypes must be substitutable for their base types"**

### ❌ Violating LSP
```python
class Bird:
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")  # Breaks contract!
```

### ✅ Proper Abstraction
```python
class Bird:
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        return self.fly()
    
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def move(self):
        return self.swim()
    
    def swim(self):
        return "Swimming"
```

## I - Interface Segregation Principle (ISP)

**"Clients shouldn't depend on interfaces they don't use"**

### ❌ Fat Interface
```python
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass
    
    @abstractmethod
    def eat(self):
        pass

class Robot(Worker):
    def work(self):
        return "Working"
    
    def eat(self):
        raise Exception("Robots don't eat!")  # Forced to implement unused method
```

### ✅ Segregated Interfaces
```python
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Human(Workable, Eatable):
    def work(self):
        return "Working"
    
    def eat(self):
        return "Eating"

class Robot(Workable):  # Only implements what it needs
    def work(self):
        return "Working"
```

## D - Dependency Inversion Principle (DIP)

**"Depend on abstractions, not concretions"**

### ❌ High-Level Depends on Low-Level
```python
class MySQLDatabase:
    def save(self, data):
        # MySQL-specific code
        pass

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Tightly coupled!
    
    def create_user(self, user):
        self.db.save(user)
```

### ✅ Depend on Abstraction
```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def save(self, data):
        pass

class MySQLDatabase(Database):
    def save(self, data):
        # MySQL-specific code
        pass

class PostgresDatabase(Database):
    def save(self, data):
        # Postgres-specific code
        pass

class UserService:
    def __init__(self, database: Database):
        self.db = database  # Depends on abstraction!
    
    def create_user(self, user):
        self.db.save(user)

# Easy to swap databases
service = UserService(MySQLDatabase())
# or
service = UserService(PostgresDatabase())
```

## Benefits of SOLID

1. **Maintainability** - Easier to modify code
2. **Testability** - Easier to write unit tests
3. **Flexibility** - Easy to extend with new features
4. **Reusability** - Components can be reused
5. **Understanding** - Clearer code organization

