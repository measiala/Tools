# Import pytest
import pytest

# Import global modules
import pathlib
import dataclasses
import typing

# Import items to test
from method_helpers import \
    base_add_item, base_read_file, base_read_xls, base_read_xlsx, base_write_file

@dataclasses.dataclass
class Type1Class:
    var1: str
    var2: str

@dataclasses.dataclass
class Type2Class:
    field1: str
    field2: str

@dataclasses.dataclass
class UmbrellaClass:
    name: str
    t1dict: dict = dataclasses.field(init=False, default_factory=dict)
    t2dict: dict = dataclasses.field(init=False, default_factory=dict)

    def add_t1(self, t1_inst):
        self.t1dict[t1_inst.var1] = t1_inst

    def add_t2(self, t2_inst):
        self.t2dict[t2_inst.field1] = t2_inst

# All of these tests are inherently tested by the various classes that call them
# but we should add in separate test files and unit tests

def test_base_read_file():
    pass

def test_base_write_file():
    pass

def test_base_read_xls():
    uc = UmbrellaClass('Test XLS')
    assert base_read_xls(
        './tests/test_xls.xls',
        [
            ['Type1', uc.add_t1, Type1Class],
            ['Type2', uc.add_t2, Type2Class]
        ]
    ) == (9, [5, 4])
    assert uc.t1dict == {
        'Value1.1': Type1Class(var1='Value1.1', var2='Value2.1'), 
        'Value1.2': Type1Class(var1='Value1.2', var2='Value2.2'),
        'Value1.3': Type1Class(var1='Value1.3', var2='Value2.3'),
        'Value1.4': Type1Class(var1='Value1.4', var2='Value2.4'),
        'Value1.5': Type1Class(var1='Value1.5', var2='Value2.5')
    }
    assert uc.t2dict == {
        'Value1.1': Type2Class(field1='Value1.1', field2='Value2.1'), 
        'Value1.2': Type2Class(field1='Value1.2', field2='Value2.2'),
        'Value1.3': Type2Class(field1='Value1.3', field2='Value2.3'),
        'Value1.4': Type2Class(field1='Value1.4', field2='Value2.4')
    }

def test_base_read_xlsx():
    uc = UmbrellaClass('Test XLSX')
    assert base_read_xlsx(
        './tests/test_xlsx.xlsx',
        [
            ['Type1', uc.add_t1, Type1Class],
            ['Type2', uc.add_t2, Type2Class]
        ]
    ) == (9, [5, 4])
    assert uc.t1dict == {
        'Value1.1': Type1Class(var1='Value1.1', var2='Value2.1'), 
        'Value1.2': Type1Class(var1='Value1.2', var2='Value2.2'),
        'Value1.3': Type1Class(var1='Value1.3', var2='Value2.3'),
        'Value1.4': Type1Class(var1='Value1.4', var2='Value2.4'),
        'Value1.5': Type1Class(var1='Value1.5', var2='Value2.5')
    }
    assert uc.t2dict == {
        'Value1.1': Type2Class(field1='Value1.1', field2='Value2.1'), 
        'Value1.2': Type2Class(field1='Value1.2', field2='Value2.2'),
        'Value1.3': Type2Class(field1='Value1.3', field2='Value2.3'),
        'Value1.4': Type2Class(field1='Value1.4', field2='Value2.4')
    }

def test_base_write_file():
    uc = UmbrellaClass('Test XLSX')
    assert base_read_xlsx(
        './tests/test_xlsx.xlsx',
        [
            ['Type1', uc.add_t1, Type1Class],
            ['Type2', uc.add_t2, Type2Class]
        ]
    ) == (9, [5, 4])
    assert base_write_file(
        './tests/test_asc.txt',
        [
            ['Type1', uc.t1dict, Type1Class],
            ['Type2', uc.t2dict, Type2Class]
        ]
    )
    with open('./tests/test_asc.txt', 'r') as infile:
        f = infile.read()
    assert f == \
        'Type1|Value1.1|Value2.1\n' \
        + 'Type1|Value1.2|Value2.2\n' \
        + 'Type1|Value1.3|Value2.3\n' \
        + 'Type1|Value1.4|Value2.4\n' \
        + 'Type1|Value1.5|Value2.5\n' \
        + 'Type2|Value1.1|Value2.1\n' \
        + 'Type2|Value1.2|Value2.2\n' \
        + 'Type2|Value1.3|Value2.3\n' \
        + 'Type2|Value1.4|Value2.4\n'

def test_base_read_file():
    uc0 = UmbrellaClass('Test XLSX')
    assert base_read_xlsx(
        './tests/test_xlsx.xlsx',
        [
            ['Type1', uc0.add_t1, Type1Class],
            ['Type2', uc0.add_t2, Type2Class]
        ]
    ) == (9, [5, 4])
    uc1 = UmbrellaClass('Test XLSX')
    assert base_read_file(
        './tests/test_asc.txt',
        [
            ['Type1', uc1.add_t1, Type1Class],
            ['Type2', uc1.add_t2, Type2Class]
        ]
    ) == 9
    assert uc0 == uc1

def test_base_add_item():
    @dataclasses.dataclass
    class TestDC:
        x: int
        y: str
        z: tuple

    @dataclasses.dataclass
    class DestDC(TestDC):
        w: list = dataclasses.field(default_factory=list)

    @dataclasses.dataclass
    class City:
        name: str = 'Test City'
        dc_dict: dict = dataclasses.field(init=False, default_factory=dict)

    a = City()
    # Add first time item as list of variables, returns one key
    assert base_add_item(
        [1, 1, 1], TestDC, DestDC, 'x', a.dc_dict
    ) == [1]
    assert a.dc_dict[1] == DestDC(1, '1', (1,), [])
    # Try add second time, not added, list of added keys is empty
    assert base_add_item(
        [1, 1, 1], TestDC, DestDC, 'x', a.dc_dict
    ) == []
    assert a.dc_dict[1] == DestDC(1, '1', (1,), [])
    # Now add second item as a single object, returns one key
    assert base_add_item(
        TestDC(2, 2, 2), TestDC, DestDC, 'x', a.dc_dict
    ) == [2]
    assert a.dc_dict[2] == DestDC(2, '2', (2,), [])
    # Now add second item as a single object, returns one key
    assert base_add_item(
        [[3, 3, 3], [4, 4.0, '4.0']], TestDC, DestDC, 'x', a.dc_dict
    ) == [3, 4]
    assert a.dc_dict[3] == DestDC(3, '3', (3,), [])
    assert a.dc_dict[4] == DestDC(4, '4.0', ('4.0',), [])
    # Now add second item as a single object, returns one key
    assert base_add_item(
        [TestDC(5, 5, 5), TestDC('6', '6', '6')], TestDC, DestDC, 'x', a.dc_dict
    ) == [5, 6]
    assert a.dc_dict[5] == DestDC(5, '5', (5,), [])
    assert a.dc_dict[6] == DestDC(6, '6', ('6',), [])

