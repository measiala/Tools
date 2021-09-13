# Import pytest
import pytest

# Import global modules
import dataclasses
import pathlib
import typing

# Import module to test
from ..formatting import \
    fmt_bool, fmt_float, fmt_int, fmt_none, fmt_str, \
    fmt_dict, fmt_list, fmt_set, fmt_tuple, \
    fmt_value, fmt_dataclass, val2txt, txt2val, str2list, \
    process_container, get_ga_types, get_dc_type_hints, populate_list, \
    define_dataclass, read_txt, write_txt, write_txt_class, write_txt_row


def test_get_ga_types():
    assert get_ga_types(typing.List[str]) == (list, (str,))
    T = typing.TypeVar('T', str, int)
    assert get_ga_types(typing.List[T]) == (list, (T,))
    with pytest.raises(TypeError):
        get_ga_types(list)


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
    assert fmt_bool(True, bool) is True
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


def test_fmt_float():
    assert fmt_float(1.5, float) == 1.5
    assert fmt_float(1.5, str) == '1.5'
    assert fmt_float(1.5, list) == [1.5]
    assert fmt_float(1.5, set) == {1.5}
    assert fmt_float(1.5, tuple) == (1.5,)
    assert fmt_float(1.5, typing.List[float]) == [1.5]
    assert fmt_float(1.5, typing.Set[float]) == {1.5}
    assert fmt_float(1.5, typing.Tuple[float]) == (1.5,)
    assert fmt_float(1.5, typing.List[str]) == ['1.5']
    assert fmt_float(1.5, typing.Set[str]) == {'1.5'}
    assert fmt_float(1.5, typing.Tuple[str]) == ('1.5',)
    with pytest.raises(ValueError):
        fmt_float(1.5, int)


def test_fmt_int():
    assert fmt_int(37, int) == 37
    assert fmt_int(37, bool) is True
    assert fmt_int(-37, bool) is True
    assert fmt_int(0, bool) is False
    assert fmt_int(1, bool) is True
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


def test_fmt_none():
    assert fmt_none(None, None) is None
    with pytest.raises(ValueError):
        fmt_none(None, bool)
    with pytest.raises(ValueError):
        fmt_none(None, int)
    with pytest.raises(ValueError):
        fmt_none(None, float)
    assert fmt_none(None, str) == ''
    assert fmt_none(None, list) == []
    assert fmt_none(None, set) == set()
    assert fmt_none(None, tuple) == tuple()
    assert fmt_none(None, dict) == {}
    assert fmt_none(None, typing.List[str]) == []
    assert fmt_none(None, typing.Set[str]) == set()
    assert fmt_none(None, typing.Tuple[str]) == tuple()


def test_fmt_str():
    assert fmt_str('123', str) == '123'
    assert fmt_str('123', list) == ['123']
    assert fmt_str('123', set) == {'123'}
    assert fmt_str('123', tuple) == ('123',)
    assert fmt_str('123', bool) is False
    assert fmt_str('True', bool) is True
    assert fmt_str('False', bool) is False
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
    assert fmt_str('', typing.List[str]) == []
    assert fmt_str('', typing.Set[str]) == set()
    assert fmt_str('', typing.Tuple[str]) == tuple()
    assert fmt_str('37', typing.List[int]) == [37]
    assert fmt_str('37', typing.Set[bool]) == {False}
    assert fmt_str('true', typing.Set[bool]) == {True}
    assert fmt_str('37', typing.Tuple[list]) == (['37'],)
    assert fmt_str('', typing.List[int]) == []
    assert fmt_str('', typing.Set[int]) == set()
    assert fmt_str('', typing.Tuple[int]) == tuple()


def test_fmt_dict():
    assert fmt_dict({}, dict) == {}
    assert fmt_dict({1: '1'}, dict) == {1: '1'}
    assert fmt_dict({1: '1'}, str) == '1,1'
    assert fmt_dict({1: '1'}, list) == [1, '1']
    assert fmt_dict({1: '1'}, typing.List[int]) == [1, 1]
    assert fmt_dict({1: '1'}, typing.Dict[int, str]) == {1: '1'}
    with pytest.raises(ValueError):
        fmt_dict({1: '1'}, bool)


def test_fmt_list():
    assert fmt_list([], list) == []
    assert fmt_list([1], list) == [1]
    assert fmt_list([1, 2, 3], set) == {1, 2, 3}
    assert fmt_list([1, 2, 3], tuple) == (1, 2, 3)
    assert fmt_list([], str) == ''
    assert fmt_list([1, 2, 3], str) == '1,2,3'
    assert fmt_list([1, 2, 3, 4], dict) == {1: 2, 3: 4}
    with pytest.raises(ValueError):
        fmt_list([1, 2, 3], dict)
    assert fmt_list([1, '1', 2, '2'], typing.List[str]) == ['1', '1', '2', '2']
    assert fmt_list([1, '1', 2, '2'], typing.List[int]) == [1, 1, 2, 2]
    assert fmt_list([1, '1', 2, '2'], typing.Dict[int, int]) == {1: 1, 2: 2}
    assert fmt_list([1, '1', 2, '2'], typing.Dict[str, int]) == {'1': 1, '2': 2}
    assert fmt_list([1, '1', 2, '2'], typing.Set[str]) == {'1', '2'}
    assert fmt_list([1, '1', 2, '2'], typing.Tuple[int]) == (1, 1, 2, 2)
    assert fmt_list([], typing.Set[str]) == set()


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
    with pytest.raises(ValueError):
        fmt_set({1, 2}, bool)


def test_fmt_tuple():
    assert fmt_tuple((), set) == set()
    assert fmt_tuple((), list) == []
    assert fmt_tuple((), tuple) == ()
    assert fmt_tuple((1, '2'), tuple) == (1, '2')   # Volatile going from unordered to ordered
    assert fmt_tuple((1, '2'), list) == [1, '2']    # Volatile going from unordered to ordered
    assert fmt_tuple((1, '2'), set) == {1, '2'}
    assert fmt_tuple((1, '2'), str) == '1,2'
    assert fmt_tuple((1, '1', 2, '2'), typing.List[str]) == ['1', '1', '2', '2']
    assert fmt_tuple((1, '1', 2, '2'), typing.List[int]) == [1, 1, 2, 2]
    assert fmt_tuple((1, '1', 2, '2'), typing.Set[str]) == {'1', '2'}
    assert fmt_tuple((1, '1', 2, '2'), typing.Set[int]) == {1, 2}
    assert fmt_tuple((1, '1', 2, '2'), typing.Tuple[int]) == (1, 1, 2, 2)
    with pytest.raises(ValueError):
        fmt_tuple((1, 2), bool)


def test_fmt_value():
    # String
    assert fmt_value('123', str) == '123'
    assert fmt_value('123', list) == ['123']
    assert fmt_value('123', set) == {'123'}
    assert fmt_value('123', tuple) == ('123',)
    assert fmt_value('123', bool) is False
    assert fmt_value('True', bool) is True
    assert fmt_value('False', bool) is False
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
    assert fmt_value([1, 2, 3, 4], dict) == {1: 2, 3: 4}
    with pytest.raises(ValueError):
        fmt_value([1, 2, 3], dict)
    # Boolean
    assert fmt_value(True, bool) is True
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
    assert fmt_value(37, bool) is True
    assert fmt_value(0, bool) is False
    assert fmt_value(1, bool) is True
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
    with pytest.raises(ValueError):
        fmt_value(pathlib.Path('./'), str)


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
    assert dc.b is True
    assert dc.f == 2
    assert dc.n == 4
    assert dc.s == 'foo.bar'
    assert dc.t == ['foo', 'bar']
    assert dc.li == ['foo', 'bar']
    assert dc.si == ['1', '2']

    dcf = fmt_dataclass(dc)
    assert dcf.b is True
    assert dcf.f == 2.0
    assert dcf.n == 4
    assert dcf.s == 'foo.bar'
    assert dcf.t == ('foo', 'bar')
    assert dcf.li == ['foo', 'bar']
    assert dcf.si == {1, 2}

    class FailTest:
        def __init__(self, b, f):
            self.b = b
            self.f = f
    ft = FailTest('1', '2')
    with pytest.raises(TypeError):
        fmt_dataclass(ft)

    dc.b = {1, 2}
    with pytest.raises(ValueError):
        fmt_dataclass(dc)

#
# Routines to convert a value from one type to text and vice versa
#


def test_str2list():
    assert str2list('12') == ['12']
    assert str2list('1,2') == ['1,2']
    assert str2list([]) == []
    assert str2list(['1', '2']) == ['1', '2']
    with pytest.raises(ValueError):
        str2list(1)


def test_val2txt():
    assert val2txt(None) == ''
    assert val2txt(1) == '1'
    assert val2txt(1.5) == '1.5'
    assert val2txt(1.50) == '1.5'
    assert val2txt(True) == 'True'
    assert val2txt({1}) == '1'
    assert val2txt({1, 2}) == '1,2'
    assert val2txt([1]) == '1'
    assert val2txt([1, 2]) == '1,2'
    assert val2txt((1,)) == '1'
    assert val2txt((1, 2)) == '1,2'
    assert val2txt({'1': 's'}) == '1,s'
    assert val2txt([[1, 2], 3]) == '1,2,3'
    assert val2txt([1, 's', True]) == '1,s,True'
    assert val2txt(pathlib.PosixPath('./foo/bar.foo')) == 'foo/bar.foo'
    with pytest.raises(ValueError):
        val2txt(ValueError)


def test_txt2val():
    assert txt2val(None) is None
    assert txt2val(1) == 1
    assert txt2val('None') is None
    assert txt2val('1') == 1
    assert txt2val('1.0') == 1
    assert txt2val('1.5') == 1.5
    assert txt2val('1.50') == 1.50
    assert txt2val('0b110') == 6
    assert txt2val('0b110x') == '0b110x'
    assert txt2val('0b110') == 6
    assert txt2val('0o770') == 7*64 + 7*8
    assert txt2val('0o770x') == '0o770x'
    assert txt2val('0x110') == 1*256 + 1*16
    assert txt2val('0x110x') == '0x110x'
    assert txt2val('True') is True
    assert txt2val('False') is False
    assert txt2val('true') is True
    assert txt2val('1,2') == [1, 2]
    assert txt2val('a,1') == ['a', 1]
    assert txt2val('1,s,True') == [1, 's', True]


def test_process_container():
    # Set up
    @dataclasses.dataclass
    class TestDC:
        x: int
        y: set

    class FailTest:
        def __init__(self, b, f):
            self.b = b
            self.f = f

    # str or list[str]
    assert process_container('12', str) == ['12']
    with pytest.raises(ValueError):
        process_container('12', list)
    assert process_container(['12'], str) == ['12']
    assert process_container(['1', '2'], str) == ['1', '2']
    with pytest.raises(ValueError):
        process_container(['1', 2], str)
    with pytest.raises(ValueError):
        process_container({'1', '2'}, str)
    # Container is list of parameters for one dataclass
    assert process_container([1, {1, 2}], TestDC) == [TestDC(x=1, y={1, 2})]
    # Container is a list of list of parameters to define a list of dataclasses
    assert process_container([[1, {1, 2}], [2, {3, 4}]], TestDC) == [TestDC(x=1, y={1, 2}), TestDC(2, {3, 4})]
    # Container is dataclass
    assert process_container(TestDC(1, {1, 2}), TestDC) == [TestDC(x=1, y={1, 2})]
    # Container is a list of dataclasses
    assert process_container([TestDC(1, {1, 2}), TestDC(2, {3, 4})], TestDC) \
        == [TestDC(x=1, y={1, 2}), TestDC(2, {3, 4})]
    with pytest.raises(ValueError):
        process_container([TestDC(1, {1, 2}), [1, {1, 2}]], TestDC)
    with pytest.raises(TypeError):
        process_container([TestDC(1, {1, 2}), [1, {1, 2}]], FailTest)

#
# Helpers to read and write dataclasses to lists and vice versa
#


def test_populate_list():
    class TestClass:
        def __init__(self, name, groups, platforms, other=None):
            self.name = name
            self.groups = groups
            self.platforms = platforms
            self.other = other

    @dataclasses.dataclass
    class DtClass:
        groups: list
        name: str
        platforms: list

    @dataclasses.dataclass
    class DtClass2:
        groups: list
        name: str
        platforms: list
        name2: str

    assert populate_list(
                TestClass('nemo', ['g1', 'g2'], ['p1', 'p2'], 'thing'), DtClass
            ) == [['g1', 'g2'], 'nemo', ['p1', 'p2']]
    assert populate_list(
                TestClass('nemo', ['g1', 'g2'], ['p1', 'p2'], 'thing'), DtClass2
            ) == [['g1', 'g2'], 'nemo', ['p1', 'p2'], '']


def test_define_dataclass():
    class TestClass:
        def __init__(self, name, groups, platforms, other=None):
            self.name = name
            self.groups = groups
            self.platforms = platforms
            self.other = other

    @dataclasses.dataclass
    class DtClass:
        groups: list
        name: str
        platforms: list

    assert define_dataclass(
                TestClass('nemo', ['g1', 'g2'], ['p1', 'p2'], 'thing'), DtClass
            ) == DtClass(
                groups=['g1', 'g2'], name='nemo', platforms=['p1', 'p2']
            )
    with pytest.raises(TypeError):
        define_dataclass(
                TestClass('nemo', ['g1', 'g2'], ['p1', 'p2'], 'thing'), TestClass
            )


def test_read_txt():
    t_str = '1,2|s,t|True'
    t_list = t_str.split('|')
    assert read_txt(t_list) == [[1, 2], ['s', 't'], True]


def test_write_txt_class():
    # Set up
    class TestClass:
        def __init__(self, name, groups, platforms, other=None):
            self.name = name
            self.groups = groups
            self.platforms = platforms
            self.other = other

    @dataclasses.dataclass
    class DtClass:
        groups: list
        name: str
        platforms: list
    assert write_txt_class(
                TestClass('nemo', ['g1', 'g2'], ['p1', 'p2'], 'thing'), DtClass
            ) == ['g1,g2', 'nemo', 'p1,p2']
    with pytest.raises(TypeError):
        write_txt_class(
                TestClass('nemo', ['g1', 'g2'], ['p1', 'p2'], 'thing'), TestClass
            )


def test_write_txt():
    # Set up
    class TestClass:
        def __init__(self, name, groups, platforms, other=None):
            self.name = name
            self.groups = groups
            self.platforms = platforms
            self.other = other

    @dataclasses.dataclass
    class DtClass:
        groups: list
        name: str
        platforms: list
    assert write_txt(
        DtClass(groups=['g1', 'g2'], name='nemo', platforms=['p1', 'p2'])
    ) == ['g1,g2', 'nemo', 'p1,p2']


def test_write_txt_row():
    # assert write_txt_row()
    class TestClass:
        def __init__(self, name, groups, platforms, other=None):
            self.name = name
            self.groups = groups
            self.platforms = platforms
            self.other = other

    @dataclasses.dataclass
    class DtClass:
        groups: list
        name: str
        platforms: list
    assert write_txt_class(
                TestClass('nemo', ['g1', 'g2'], ['p1', 'p2'], 'thing'), DtClass
            ) == ['g1,g2', 'nemo', 'p1,p2']

    assert write_txt_row(
                TestClass('nemo', ['g1', 'g2'], ['p1', 'p2'], 'thing'), DtClass
            ) == ['g1,g2', 'nemo', 'p1,p2']
    assert write_txt_row(
        DtClass(groups=['g1', 'g2'], name='nemo', platforms=['p1', 'p2'])
    ) == ['g1,g2', 'nemo', 'p1,p2']
