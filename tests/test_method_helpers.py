# Import pytest
import pytest

# Import global modules
import pathlib
import dataclasses
import typing

# Import items to test
from ..method_helpers import \
    base_add_item, base_read_file, base_read_xls, base_read_xlsx, base_write_file

# Root directory
root = pathlib.Path.cwd()
print(root.name)

@dataclasses.dataclass
class Type1Class:
    var1: str
    var2: str

@dataclasses.dataclass
class Type2Class:
    field1: str
    field2: str

@dataclasses.dataclass
class Type3Class:
    field1: str

@dataclasses.dataclass
class UmbrellaClass:
    name: str
    t1dict: dict = dataclasses.field(init=False, default_factory=dict)
    t2dict: dict = dataclasses.field(init=False, default_factory=dict)
    t3dict: dict = dataclasses.field(init=False, default_factory=dict)

    def add_t1(self, t1_inst):
        self.t1dict[t1_inst.var1] = t1_inst

    def add_t2(self, t2_inst):
        self.t2dict[t2_inst.field1] = t2_inst

    def add_t3(self, t3_inst):
        self.t3dict[t3_inst.field1] = t3_inst

# All of these tests are inherently tested by the various classes that call them
# but we should add in separate test files and unit tests

def test_base_read_xls():
    uc = UmbrellaClass('Test XLS')
    assert base_read_xls(
        root / 'tests' / 'test_xls.xls',
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

    # Create various errors
    uc1 = UmbrellaClass('Error Instance')

    # Incorrect number of list items
    with pytest.raises(ValueError):
        base_read_xls(
            root / 'tests' / 'test_xls.xls',
            [
                ['1epyT', uc.add_t1]
            ]
        )
    
    # Sheet name not found
    with pytest.raises(ValueError):
        base_read_xls(
            root / 'tests' / 'test_xls.xls',
            [
                ['1epyT', uc.add_t1, Type1Class]
            ]
        )

    # Record type mismatch in number of records
    with pytest.raises(TypeError):
        base_read_xls(
            root / 'tests' / 'test_xls.xls',
            [
                ['Type1', uc.add_t3, Type3Class]
            ]
        )

    # Record type mismatch in number of records
    with pytest.raises(ValueError):
        base_read_xls(
            root / 'tests' / 'test_xls.xls',
            [
                ['Type1', uc.add_t3, Type1Class]
            ]
        )


def test_base_read_xlsx():
    uc = UmbrellaClass('Test XLSX')
    assert base_read_xlsx(
        root / 'tests' / 'test_xlsx.xlsx',
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
        root / 'tests' / 'test_xlsx.xlsx',
        [
            ['Type1', uc.add_t1, Type1Class],
            ['Type2', uc.add_t2, Type2Class]
        ]
    ) == (9, [5, 4])

    # Write out one record with no record type prefix to .._1
    assert base_write_file(
        root / 'tests' / 'test_asc_1.txt',
        [
            [None, uc.t1dict, Type1Class]
        ]
    ) == 5

    # Verify contents of .._1
    with open(root / 'tests' / 'test_asc_1.txt', 'r') as infile:
        f = infile.read()
    assert f == \
        'Value1.1|Value2.1\n' \
        + 'Value1.2|Value2.2\n' \
        + 'Value1.3|Value2.3\n' \
        + 'Value1.4|Value2.4\n' \
        + 'Value1.5|Value2.5\n'
    
    # Trigger ValueError if rt_lists is incomplete
    with pytest.raises(ValueError):
        assert base_write_file(
            root / 'tests' / 'test_asc_2.txt',
            [
                ['Type1', uc.t1dict, Type1Class],
                ['Type2', uc.t2dict]
            ]
        )

    # Standard final write to .._2
    assert base_write_file(
        root / 'tests' / 'test_asc_2.txt',
        [
            ['Type1', uc.t1dict, Type1Class],
            ['Type2', uc.t2dict, Type2Class]
        ]
    ) == 9

    # Verify contents of .._2
    with open(root / 'tests' / 'test_asc_2.txt', 'r') as infile:
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
    # Read in base line
    uc0 = UmbrellaClass('Test XLSX')
    assert base_read_xlsx(
        root / 'tests' / 'test_xlsx.xlsx',
        [
            ['Type1', uc0.add_t1, Type1Class],
            ['Type2', uc0.add_t2, Type2Class]
        ]
    ) == (9, [5, 4])

    # Read in standard 2 class from .._2
    uc1 = UmbrellaClass('Test XLSX')
    assert base_read_file(
        root / 'tests' / 'test_asc_2.txt',
        [
            ['Type1', uc1.add_t1, Type1Class],
            ['Type2', uc1.add_t2, Type2Class]
        ]
    ) == 9
    assert uc0 == uc1

    # Read in just t1 class from .._1
    uc2 = UmbrellaClass('Test XLSX')
    assert base_read_file(
        root / 'tests' / 'test_asc_1.txt',
        [
            [None, uc2.add_t1, Type1Class]
        ]
    ) == 5
    assert uc0.t1dict == uc2.t1dict

    # Trigger Value Error
    uc3 = UmbrellaClass('Test XLSX')
    with pytest.raises(ValueError):
        base_read_file(
            root / 'tests' / 'test_asc_1.txt',
            [
                [uc2.add_t1, Type1Class]
            ]
        )

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

