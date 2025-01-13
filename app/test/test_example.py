import pytest


def test_instance():
    assert isinstance("this is a string instance", str)
    assert not isinstance(123, str)

def test_type():
    assert type("this is a string" is str)
    assert type(123 is int)

def test_bool():
    validated = True
    assert validated is True

def test_value():
    assert 7 > 5
    assert 3 < 10

def test_list():
    num_list = [1,2,3,4,5,6,7]
    bool_list = [False, False]
    assert 7 in num_list
    assert 8 not in num_list
    assert all(num_list)
    assert not any(bool_list)

class Student:
    def __init__(self, first_name: str, last_name: str, major: str, year: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.year = year

@pytest.fixture
def default_student():
    return Student("John", "Doe", "Mathematics", 1999)

def test_init_student(default_student):
    assert default_student.first_name == "John", "First name must be John"
    assert default_student.last_name == "Doe", "Last name must be Doe"
    assert default_student.major == "Mathematics", "Major must be Mathematics"
    assert default_student.year == 1999, "Year must be 1999"