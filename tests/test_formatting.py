# Import pytest
import pytest

# Import global modules
import collections
import dataclasses
import pathlib
import sys
import typing

# Import module to test
from formatting import \
    fmt_bool, fmt_int, fmt_str, fmt_list, fmt_set, fmt_tuple, fmt_value, fmt_dataclass, \
    val2txt, txt2val, str2list, \
    process_container, get_ga_types, get_dc_type_hints, \
    define_dataclass, read_txt, write_txt, write_txt_class, write_txt_row

def test_get_ga_types():
    assert get_ga_types(typing.List[str]) == (list, (str,))
    T = typing.TypeVar('T', str, int)
    assert get_ga_types(typing.List[T]) == (list, (T,))

def test_get_dc_type_hints():
    @dataclasses.dataclass
    class DtClass:
        x: str = '1'
        y: set = dataclasses.field(default_factory={2, 3})
        z: int = 3

    @dataclasses.dataclass
    class DtSubClass(DtClass):
        a: typing.List[int] = dataclasses.field(default_factory=[1, 2, 3, 4])
        b: typing.Set[str] = dataclasses.field(default_factory={'a', 'b', 'c'})
        c: typing.Tuple[int] = dataclasses.field(default_factory=(1, 2, 3))
        d: typing.Dict[str, list] = dataclasses.field(
            default_factory={'positions': ['QB', 'RB'], 'teams': ['DET', 'GB', 'CHI']}
        )
        e: typing.List[None] = dataclasses.field(default_factory=[None])

    assert get_dc_type_hints(DtClass) == {
        'x': str, 'y': set, 'z': int
    }
    assert get_dc_type_hints(DtSubClass) == {
        'x': str, 'y': set, 'z': int,
        'a': typing.List[int],
        'b': typing.Set[str],
        'c': typing.Tuple[int],
        'd': typing.Dict[str, list],
        'e': list
    }

def test_fmt_bool():
    assert fmt_bool(True, bool) == True
    assert fmt_bool(True, int) == 1
    assert fmt_bool(False, int) == 0
    assert fmt_bool(True, str) == 'True'
    assert fmt_bool(True, list) == [True]
    assert fmt_bool(True, set) == {True}
    assert fmt_bool(True, tuple) == (True,)
    assert fmt_bool(True, typing.List[str]) == ['True']
    assert fmt_bool(False, typing.Set[int]) == {0}
    assert fmt_bool(True, typing.Tuple[list]) == ([True],)
    with pytest.raises(ValueError):
        fmt_bool(True, float)
    with pytest.raises(ValueError):
        fmt_bool(True, dict)

def test_fmt_int():
    assert fmt_int(37, int) == 37
    assert fmt_int(37, bool) == True
    assert fmt_int(-37, bool) == True
    assert fmt_int(0, bool) == False
    assert fmt_int(1, bool) == True
    assert fmt_int(37, str) == '37'
    assert fmt_int(37, float) == 37.0
    assert fmt_int(37, list) == [37]
    assert fmt_int(37, set) == {37}
    assert fmt_int(37, tuple) == (37,)
    assert fmt_int(37, typing.List[str]) == ['37']
    assert fmt_int(37, typing.Set[bool]) == {True}
    assert fmt_int(37, typing.Tuple[list]) == ([37],)
    with pytest.raises(ValueError):
        fmt_int(37, dict)

def test_fmt_str():
    assert fmt_str('123', str) == '123'
    assert fmt_str('123', list) == ['123']
    assert fmt_str('123', set) == {'123'}
    assert fmt_str('123', tuple) == ('123',)
    assert fmt_str('123', bool) == False
    assert fmt_str('True', bool) == True
    assert fmt_str('False', bool) == False
    assert fmt_str('foo.bar', pathlib.PosixPath) == pathlib.PosixPath('foo.bar')
    assert fmt_str('foo.bar', pathlib.Path) == pathlib.Path('foo.bar')
    assert fmt_str('', str) == ''
    assert fmt_str('', list) == []
    assert fmt_str('', set) == set()
    assert fmt_str('', tuple) == tuple()
    assert fmt_str('123', int) == 123
    assert fmt_str('123.4', float) == 123.4
    with pytest.raises(ValueError):
        fmt_str('123a', int)
    assert fmt_str('37', typing.List[int]) == [37]
    assert fmt_str('37', typing.Set[bool]) == {False}
    assert fmt_str('true', typing.Set[bool]) == {True}
    assert fmt_str('37', typing.Tuple[list]) == (['37'],)

def test_fmt_list():
    assert fmt_list([], list) == []
    assert fmt_list([1], list) == [1]
    assert fmt_list([1, 2, 3], set) == {1, 2, 3}
    assert fmt_list([1, 2, 3], tuple) == (1, 2, 3)
    assert fmt_list([1, 2, 3], str) == '1,2,3'
    assert fmt_list([1, 2, 3, 4], dict) == { 1: 2, 3: 4}
    with pytest.raises(ValueError):
        fmt_list([1, 2, 3], dict)
    assert fmt_list([1, '1', 2, '2'], typing.List[str]) == ['1', '1', '2', '2']
    assert fmt_list([1, '1', 2, '2'], typing.List[int]) == [1, 1, 2, 2]
    assert fmt_list([1, '1', 2, '2'], typing.Dict[int, int]) == {1: 1, 2: 2}
    assert fmt_list([1, '1', 2, '2'], typing.Dict[str, int]) == {'1': 1, '2': 2}
    assert fmt_list([1, '1', 2, '2'], typing.Set[str]) == {'1', '2'}
    assert fmt_list([1, '1', 2, '2'], typing.Tuple[int]) == (1, 1, 2, 2)

def test_fmt_set():
    assert fmt_set(set(), set) == set()
    assert fmt_set(set(), list) == []
    assert fmt_set(set(), tuple) == ()
    assert fmt_set({1, '2'}, tuple) in [(1, '2'), ('2', 1)]
    assert fmt_set({1, '2'}, list) in [[1, '2'], ['2', 1]]
    assert fmt_set({1, '2'}, set) in [{1, '2'}, {'2', 1}]
    assert fmt_set({'a', '2'}, str) == '2,a'
    assert fmt_set({1, '1', 2, '2'}, typing.List[str]) in [['1', '2'], ['2', '1']]
    assert fmt_set({1, '1', 2, '2'}, typing.List[int]) == [1, 2]
    assert fmt_set({1, '1', 2, '2'}, typing.Set[str]) == {'1', '2'}
    assert fmt_set({1, '1', 2, '2'}, typing.Set[int]) == {1, 2}
    assert fmt_set({1, '1', 2, '2'}, typing.Tuple[int]) == (1, 2)

def test_fmt_tuple():
    assert fmt_tuple((), set) == set()
    assert fmt_tuple((), list) == []
    assert fmt_tuple((), tuple) == ()
    assert fmt_tuple((1, '2'), tuple) == (1, '2') # Volatile going from unordered to ordered
    assert fmt_tuple((1, '2'), list) == [1, '2']  # Volatile going from unordered to ordered
    assert fmt_tuple((1, '2'), set) == {1, '2'}
    assert fmt_tuple((1, '2'), str) == '1,2'
    assert fmt_tuple((1, '1', 2, '2'), typing.List[str]) == ['1', '1', '2', '2']
    assert fmt_tuple((1, '1', 2, '2'), typing.List[int]) == [1, 1, 2, 2]
    assert fmt_tuple((1, '1', 2, '2'), typing.Set[str]) == {'1', '2'}
    assert fmt_tuple((1, '1', 2, '2'), typing.Set[int]) == {1, 2}
    assert fmt_tuple((1, '1', 2, '2'), typing.Tuple[int]) == (1, 1, 2, 2)

def test_fmt_value():
    # String
    assert fmt_value('123', str) == '123'
    assert fmt_value('123', list) == ['123']
    assert fmt_value('123', set) == {'123'}
    assert fmt_value('123', tuple) == ('123',)
    assert fmt_value('123', bool) == False
    assert fmt_value('True', bool) == True
    assert fmt_value('False', bool) == False
    assert fmt_value('foo.bar', pathlib.PosixPath) == pathlib.PosixPath('foo.bar')
    assert fmt_value('foo.bar', pathlib.Path) == pathlib.Path('foo.bar')
    assert fmt_value('', str) == ''
    assert fmt_value('', list) == []
    assert fmt_value('', set) == set()
    assert fmt_value('', tuple) == tuple()
    with pytest.raises(ValueError):
        fmt_value('123a', int)
    # List
    assert fmt_value([], list) == []
    assert fmt_value([1], list) == [1]
    assert fmt_value([1, 2, 3], set) == {1, 2, 3}
    assert fmt_value([1, 2, 3], tuple) == (1, 2, 3)
    assert fmt_value([1, 2, 3], str) == '1,2,3'
    assert fmt_value([1, 2, 3, 4], dict) == { 1: 2, 3: 4}
    with pytest.raises(ValueError):
        fmt_value([1, 2, 3], dict)
    # Boolean
    assert fmt_value(True, bool) == True
    assert fmt_value(True, int) == 1
    assert fmt_value(True, str) == 'True'
    assert fmt_value(True, list) == [True]
    assert fmt_value(True, set) == {True}
    assert fmt_value(True, tuple) == (True,)
    with pytest.raises(ValueError):
        fmt_value(True, float)
    with pytest.raises(ValueError):
        fmt_value(True, dict)
    # Integer
    assert fmt_value(37, int) == 37
    assert fmt_value(37, bool) == True
    assert fmt_value(0, bool) == False
    assert fmt_value(1, bool) == True
    assert fmt_value(37, str) == '37'
    assert fmt_value(37, float) == 37.0
    assert fmt_value(37, list) == [37]
    assert fmt_value(37, set) == {37}
    assert fmt_value(37, tuple) == (37,)
    with pytest.raises(ValueError):
        fmt_value(37, dict)
    # Set
    assert fmt_value({1, '2'}, tuple) in [('2', 1), (1, '2')]
    assert fmt_value({1, '2'}, list) in [['2', 1], [1, '2']]
    assert fmt_value({1, '2'}, set) == {1, '2'}
    assert fmt_value({1, '2'}, str) == '1,2'

def test_fmt_dataclass():
    # Set up
    @dataclasses.dataclass
    class Test:
        b: bool
        f: float
        n: int
        s: str
        t: tuple
        li: list
        si: typing.Set[int]

    # Verify result of txt2val, all list-like things have been cast as a list
    dc_val = [True, 2, 4, 'foo.bar', ['foo', 'bar'], ['foo', 'bar'], ['1', '2']]
    dc = Test(*dc_val)
    assert dc.b == True
    assert dc.f == 2
    assert dc.n == 4
    assert dc.s == 'foo.bar'
    assert dc.t == ['foo', 'bar']
    assert dc.li == ['foo', 'bar']
    assert dc.si == ['1', '2']

    dcf = fmt_dataclass(dc)
    assert dcf.b == True
    assert dcf.f == 2.0
    assert dcf.n == 4
    assert dcf.s == 'foo.bar'
    assert dcf.t == ('foo', 'bar')
    assert dcf.li == ['foo', 'bar']
    assert dcf.si == {1, 2}

##
## Routines to convert a value from one type to text and vice versa
##

def test_str2list():
    assert str2list('12') == ['12']
    assert str2list('1,2') == ['1,2']
    assert str2list([]) == []
    assert str2list(['1', '2']) == ['1', '2']
    with pytest.raises(ValueError):
        str2list(1)

def test_val2txt():
    assert val2txt(1) == '1'
    assert val2txt(1.5) == '1.5'
    assert val2txt(1.50) == '1.5'
    assert val2txt(True) == 'True'
    assert val2txt({1}) == '1'
    assert val2txt({1,2}) == '1,2'
    assert val2txt([1]) == '1'
    assert val2txt([1,2]) == '1,2'
    assert val2txt((1,)) == '1'
    assert val2txt((1,2)) == '1,2'
    assert val2txt({'1': 's'}) == '1,s'
    assert val2txt([[1,2],3]) == '1,2,3'
    assert val2txt([1,'s',True]) == '1,s,True'

def test_txt2val():
    assert txt2val('1') == 1
    assert txt2val('1.0') == 1
    assert txt2val('1.5') == 1.5
    assert txt2val('1.50') == 1.50
    assert txt2val('True') == True
    assert txt2val('False') == False
    assert txt2val('true') == True
    assert txt2val('1,2') == [1,2]
    assert txt2val('a,1') == ['a', 1]
    assert txt2val('1,s,True') == [1, 's', True]

def test_process_container():
    # Set up
    @dataclasses.dataclass
    class TestDC:
        x: int
        y: set

    # Container is list of parameters for one dataclass
    assert process_container([1, {1,2}], TestDC) == [TestDC(x=1, y={1,2})]
    # Container is a list of list of parameters to define a list of dataclasses
    assert process_container([[1, {1,2}], [2, {3,4}]], TestDC) == [TestDC(x=1, y={1,2}), TestDC(2, {3,4})]
    # Container is dataclass
    assert process_container(TestDC(1, {1,2}), TestDC) == [TestDC(x=1, y={1,2})]
    # Container is a list of dataclasses
    assert process_container([TestDC(1, {1,2}), TestDC(2, {3,4})], TestDC) == [TestDC(x=1, y={1,2}), TestDC(2, {3,4})]

##
## Helpers to read and write dataclasses to lists and vice versa
##

def test_define_dataclass():
    class TestClass:
        def __init__(self, name, groups, platforms, other = None):
            self.name = name
            self.groups = groups
            self.platforms = platforms
            self.other = other

    @dataclasses.dataclass
    class DtClass:
        groups: list
        name: str
        platforms: list

    user_inst = TestClass('lead', ['group', 'group1', 'group2'], ['PS-PROD'])

    assert define_dataclass(user_inst, DtClass) == DtClass(['group','group1','group2'], 'lead', ['PS-PROD'])

def test_read_txt():
    t_str = '1,2|s,t|True'
    t_list = t_str.split('|')
    assert read_txt(t_list) == [[1, 2], ['s', 't'], True]

def test_write_txt():
    # Set up
    tup = collections.namedtuple('Test', 'w x y z')
    tt = tup(w=1, x={1,2}, y=('s', 't'), z=True)

    assert write_txt(tt) == ['1', '1,2', 's,t', 'True']

    ############## Add dataclass test values #########################

def test_write_txt_class():
    # Set up
    ############## Add dataclass test values #########################
    tup = collections.namedtuple('Test', 'w x y z')
    stup = collections.namedtuple('Test', 'z y w x')
    tt = tup(w=1, x={1,2}, y=('s', 't'), z=True)
    stt = stup(w=1, x={1,2}, y=('s', 't'), z=True)

    assert list(tt) == [1, {1,2}, ('s','t'), True]
    assert list(stt) == [True, ('s','t'), 1, {1,2}]

    assert write_txt(tt) == ['1', '1,2', 's,t', 'True']
    assert write_txt(stt) == ['True', 's,t', '1', '1,2']

    assert write_txt_class(stt, tt) == ['1', '1,2', 's,t', 'True']

def test_write_txt_row():
    ## assert write_txt_row()
    pass