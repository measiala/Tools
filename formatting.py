"""
    Module Title:      formatting

    Author:             Mark Asiala
    Date:               2021/08/26
    Purpose:            This is a collection of functions to aid in formatting
                        values from one format to another
"""

# Import global modules
import dataclasses
import itertools
import pathlib
import sys
import typing

# Alternative to typing.get_field_types that is more robust for subclasses
# and also selective uses detailed versus generic type hints


def get_ga_types(ga_type: typing.Type) -> typing.Tuple[typing.Any, typing.Tuple[typing.Any, ...]]:
    """ Return base origin and arguments type of Generic type in a version-independent method

    :param ga_type: Generic type defined using typing
    :type ga_type: typing.Generic
    """
    if sys.version_info >= (3, 8, 0):
        # python 3.8+: functions were added in 3.8
        _origin = typing.get_origin(ga_type)
        _args = typing.get_args(ga_type)
        if (_origin, _args) == (None, ()):
            raise TypeError('Position parameter for get_ga_types must be a Generic class')
    elif sys.version_info >= (3, 7, 0):
        try:
            _origin = ga_type.__origin__
            _args = ga_type.__args__
        except AttributeError as exc:
            raise TypeError('Position parameter for get_ga_types must be a Generic class') from exc
    else:
        raise NotImplementedError('Support is not provided for python version < v3.7')
    return _origin, _args


def get_dc_type_hints(dc: object) -> typing.Dict[str, typing.Any]:
    """ Create alternative to typing.get_field_types to see if fix problems

    :param dc: dataclass with type hinting from which we will extract the type hints into a dictionary
    :type dc: dataclass
    """
    type_dict = {}
    try:
        fields = dataclasses.fields(dc)
    except (TypeError, AttributeError) as exc:
        raise TypeError('Input to get_dc_type_hints must be a dataclass') from exc
    for x in fields:
        try:
            _origin, _args = get_ga_types(x.type)
        except TypeError:
            # get_ga_types will return TypeError if not a generic class
            type_dict[x.name] = x.type
            continue

        # Path where type is a generic alias
        _args_in = True

        for _a in _args:
            # Only process typing.GenericAlias[bool/int/str/list/set/tuple]
            if _a not in [bool, int, str, list, set, tuple]:
                _args_in = False
                break
        if _origin in [list, dict, set, tuple] and _args_in:
            type_dict[x.name] = x.type              # Try basic GenericAlias approach
        else:
            type_dict[x.name] = _origin             # This removes the types of the args
        continue
    return type_dict


# Format single element values, form is : fmt_<dynamic_type>(value, <dest_type>)

def fmt_bool(value: bool, fmt: type) -> typing.Any:
    """ Convert known boolean value to fmt

    :param value:  boolean value to be reformatted
    :type value:  boolean

    :param fmt:  destination format: bool | int | str | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    # Do nothing
    if fmt == bool:
        return value
    # First simple conversions
    if fmt == int:
        return int(value)
    if fmt == str:
        return str(value)
    # list[bool]
    if fmt == list:
        return [value]
    # set[bool]
    if fmt == set:
        return {value}
    # tuple[bool]
    if fmt == tuple:
        return tuple([value])
    # typing.[List | Set | Tuple][elem_fmt]
    try:
        base_fmt, _args = get_ga_types(fmt)
    except TypeError:
        # Move on to next step
        pass
    else:
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            return fmt_list([fmt_bool(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))


def fmt_float(value: float, fmt: type) -> typing.Any:
    # Do nothing
    if fmt == float:
        return value
    # Basic conversions
    if fmt == str:
        return str(value)
    if fmt == list:
        return [value]
    if fmt == set:
        return {value}
    if fmt == tuple:
        return (value,)
    # typing.[List | Set | Tuple][elem_fmt]
    try:
        base_fmt, _args = get_ga_types(fmt)
    except TypeError:
        # Skip to next test or raise error at end
        pass
    else:
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type

        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            return fmt_list([fmt_float(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))


def fmt_int(value: int, fmt: type) -> typing.Any:
    """ Convert known integer value to fmt

    :param value:  integer value to be reformatted
    :type value:  integer

    :param fmt:  destination format: bool | float | int | str | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    # First simple conversions
    if fmt == int:
        return value
    if fmt == bool:
        return not value == 0
    if fmt == str:
        return str(value)
    if fmt == float:
        return float(value)
    # list[int]
    if fmt == list:
        return [value]
    # set[int]
    if fmt == set:
        return {value}
    # tuple[int]
    if fmt == tuple:
        return tuple([value])
    # typing.[List | Set | Tuple][elem_fmt]
    try:
        base_fmt, _args = get_ga_types(fmt)
    except TypeError:
        # Skip to next test if present
        pass
    else:
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            #print(base_fmt, elem_fmt, fmt_int(value, elem_fmt))
            return fmt_list([fmt_int(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))


def fmt_none(value: None, fmt: type) -> typing.Any:
    """ Convert known None value to fmt

    :param value:  None value to be reformatted
    :type value:  None

    :param fmt:  destination format: str | None | dict | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    # Simple conversions
    if fmt is None:
        return value
    if fmt == str:
        return ''
    if fmt == dict:
        return {}
    if fmt == list:
        return []
    if fmt == set:
        return set()
    if fmt == tuple:
        return tuple()
    # typing.[List | Set | Tuple][elem_fmt]
    try:
        base_fmt, _args = get_ga_types(fmt)
    except TypeError:
        # skip to next test
        pass
    else:
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        if base_fmt in [list, set, tuple]:
            return fmt_none(value, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))


def fmt_str(value: str, fmt: type) -> typing.Any:
    """ Convert known string value to fmt

    :param value:  string value to be reformatted
    :type value:  string

    :param fmt:  destination format: bool | float | int | pathlib.(Posix)Path | str | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    # Do nothing case
    if fmt == str:
        return value
    # Special cases if string is blank and want to return empty dict, list, etc.
    if value == '':
        return fmt_none(None, fmt)
    # Basic structures
    if fmt == bool:
        return value.title() == 'True'
    if fmt in [int, float]:
        try:
            new_value = float(value)
        except ValueError:
            # If ValueError then skip else block and it will pass to final return
            pass
        else:
            if fmt == int:
                # Note we only are reformatting here not transforming
                if int(new_value) == new_value:
                    return int(new_value)
            if fmt == float:
                return new_value
    if fmt == pathlib.PosixPath:
        return pathlib.PosixPath(value)
    if fmt == pathlib.Path:
        return pathlib.Path(value)
    # List[str]
    if fmt == list:
        return [value]
    # Set[str]
    if fmt == set:
        return {value}
    # Tuple[str]
    if fmt == tuple:
        return tuple([value])
    # typing.[List | Set | Tuple][elem_fmt]
    try:
        base_fmt, _args = get_ga_types(fmt)
    except TypeError:
        # skip to next test
        pass
    else:
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            if value:
                return fmt_list([fmt_str(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (value, str(fmt)))


def fmt_dict(value: dict, fmt: type) -> typing.Any:
    """ Convert known dict value to fmt

    :param value:  dict value to be reformatted
    :type value:  dict of arbitrary elements

    :param fmt:  destination format: str | dict[] | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    # Do nothing
    if fmt == dict:
        return value
    # Conversion to comma-delimited string
    if fmt == str:
        # Return str(list) but without the square brackets
        return ','.join(fmt_dict(value, typing.List[str]))
    if fmt == list:
        new_list = []
        for x in value.keys():
            new_list.append(x)
            new_list.append(value[x])
        return new_list
    # typing.[List | Dict]
    try:
        base_fmt, _args = get_ga_types(fmt)
    except TypeError:
        # skip to next test
        pass
    else:
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        if base_fmt in [list, dict]:
            key_fmt = _args[0]
            if base_fmt == list:
                value_fmt = key_fmt
            else:
                value_fmt = _args[1]
            new_dict = {}
            for x, y in zip(value.keys(), value.values()):
                new_key = fmt_value(x, key_fmt)
                new_value = fmt_value(y, value_fmt)
                if new_key not in new_dict:
                    new_dict[new_key] = new_value
            return fmt_dict(new_dict, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (value, str(fmt)))


def fmt_list(value: list, fmt: type) -> typing.Any:
    """ Convert known list value to fmt

    :param value:  list value to be reformatted
    :type value:  list of arbitrary elements

    :param fmt:  destination format: str | dict[] | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    # Do nothing
    if fmt == list:
        return value
    # Conversion to comma-delimited string
    if fmt == str:
        # Return str(list) but without the square brackets
        return ','.join([fmt_value(x, str) for x in value])
    # Basic conversions
    if fmt == set:
        return set(value)
    if fmt == tuple:
        return tuple(value)
    # Dict, if length is even then define using adjacent pairs in order
    if fmt == dict and len(value) % 2 == 0:
        return {value[k]: value[k+1] for k in range(0, len(value), 2)}
    # Generic types
    try:
        base_fmt, _args = get_ga_types(fmt)
    except TypeError:
        # skip to next test
        pass
    else:
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        if base_fmt in [dict, list, set, tuple]:
            if len(value):
                # Format the elements then repass into function to set base_fmt
                if base_fmt == dict:
                    # Note if odd elements, will capture error on second fmt_list call
                    new_list = []
                    for elem_value, elem_fmt in zip(value, itertools.cycle(_args)):
                        new_list.append(fmt_value(elem_value, elem_fmt))
                else:
                    elem_fmt = _args[0]
                    new_list = [fmt_value(x, elem_fmt) for x in value]
                return fmt_list(new_list, base_fmt)
            # Handle empty list so no elements to format
            return fmt_list(value, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))


def fmt_set(value, fmt) -> typing.Any:
    """ Convert known set value to fmt

    :param value:  set value to be reformatted
    :type value:  set of arbitrary elements

    :param fmt:  destination format: str | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    # Do nothing
    if fmt == set:
        return value
    # Conversion to comma-delimited string
    if fmt == str:
        # Return str(list) but without the square brackets
        new_value = {fmt_value(x, str) for x in value}
        return ','.join(sorted(new_value))
    # Basic conversions
    if fmt == list:
        return list(value)
    if fmt == tuple:
        return tuple(value)
    # Generic types
    try:
        base_fmt, _args = get_ga_types(fmt)
    except TypeError:
        # skip to next test
        pass
    else:
        # Order is to convert all elements of set to format, then convert the set
        # base_fmt is standard generic format of type
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            new_set = {fmt_value(x, elem_fmt) for x in value}
            return fmt_set(new_set, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))


def fmt_tuple(value: tuple, fmt: type) -> typing.Any:
    """ Convert known tuple value to fmt

    :param value:  tuple value to be reformatted
    :type value:  tuple of arbitrary elements

    :param fmt:  destination format: str | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    """ Convert known tuple to fmt """
    # Do nothing
    if fmt == tuple:
        return value
    # Conversion to comma-delimited string
    if fmt == str:
        # Return str(list) but without the square brackets
        return ','.join([fmt_value(x, str) for x in value])
    # Basic conversions
    if fmt == list:
        return list(value)
    if fmt == set:
        return set(value)
    # typing Generic Types
    try:
        base_fmt, _args = get_ga_types(fmt)
    except TypeError:
        # skip to next test
        pass
    else:
        # base_fmt is standard generic format of type
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            new_tuple = tuple([fmt_value(x, elem_fmt) for x in value])
            return fmt_tuple(new_tuple, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))


def fmt_value(value: typing.Any, fmt: type) -> typing.Any:
    """ Convert value of inferred type to fmt

    :param value:  list value to be reformatted
    :type value:  list of arbitrary elements

    :param fmt:  destination format: str | dict[] | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    # Note that we are purposely using type rather than isinstance to distingish bool
    # from int as well as subscripted generic types cannot use isinstance.
    if type(value) == fmt:
        return value
    if value is None:
        return fmt_none(value, fmt)
    if isinstance(value, bool):
        return fmt_bool(value, fmt)
    if isinstance(value, dict):
        return fmt_dict(value, fmt)
    if isinstance(value, float):
        return fmt_float(value, fmt)
    if isinstance(value, int):
        return fmt_int(value, fmt)
    if isinstance(value, list):
        return fmt_list(value, fmt)
    if isinstance(value, set):
        return fmt_set(value, fmt)
    if isinstance(value, str):
        return fmt_str(value, fmt)
    if isinstance(value, tuple):
        return fmt_tuple(value, fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))


def fmt_dataclass(dc: object) -> object:
    """ Format the variable values in dataclass according to its defined type hints

    :param dc: dataclass with type hints defined but with unformatted values
    :type dc: dataclass
    """
    try:
        dc_dict = dataclasses.asdict(dc)
        dc_types = get_dc_type_hints(dc)
    except TypeError as exc:
        raise TypeError('Must supply a type hinted dataclass as input') from exc

    rdc_dict = {}
    for x in dc_dict:
        try:
            rdc_dict[x] = fmt_value(dc_dict[x], dc_types[x])
        except ValueError as exc:
            raise ValueError(
                'Cannot handle putting field %s = %s into format %s'
                % (str(x), str(dc_dict[x]), str(dc_types[x]))
            ) from exc

    rdc = getattr(dc, '__class__')
    return rdc(**rdc_dict)


# Routines to convert a value from one type to text and vice versa. These can serve as
# examples of specialized applications of the formatting above.


def str2list(name: typing.Union[str, list]) -> list:
    """ If name is string then return list else if already a list then simply return name

    :param name:  standardizes input of string or list to be a list
    :type name:  string | list
    """
    if not isinstance(name, (str, list)):
        raise ValueError("Expecting name %s to be a string or a list", name)
    return fmt_value(name, list)


def val2txt(v: typing.Any) -> str:
    """ Creates a string version of all acceptable inputs, helpful if writing to an ASCII file

    :param v:  input value to be converted to a string
    :type v:  bool | dict | float | int | list | tuple | pathlib.Path | pathlib.PurePath | pathlib.PosixPath
    """
    if isinstance(v, str):
        return v
    if isinstance(v, (pathlib.Path, pathlib.PurePath, pathlib.PosixPath)):
        return str(v)
    if isinstance(v, set):
        return fmt_list(sorted(v), str)
    if isinstance(v, (bool, dict, float, int, list, tuple)) or v is None:
        return fmt_value(v, str)
    raise ValueError('Following value cannot be converted to text', v)


def txt2val(v: str) -> typing.Any:
    """ Convert text value provided to guessed python type

    :param v:  value of unknown type read in from a string input
    :type v:  string
    """
    # If the string contains a boolean keyword then treat as boolean
    if not isinstance(v, str):
        return v
    if v == 'None':
        return None
    if v.title() in ['True', 'False']:
        return v.title() == 'True'
    # If the string contains a comma treat as list
    if ',' in v:
        nv = v.split(',')
        return [txt2val(x.strip()) for x in nv]
    # Otherwise check if it is a number
    # First address integers of base 2, 8, or 16
    if len(v) > 2:
        if v[:2] == '0b':
            try:
                nv = int(v, 2)
            except (TypeError, ValueError):
                return v
            else:
                return nv
        elif v[:2] == '0o':
            try:
                nv = int(v, 8)
            except (TypeError, ValueError):
                return v
            else:
                return nv
        elif v[:2] == '0x':
            try:
                nv = int(v, 16)
            except (TypeError, ValueError):
                return v
            else:
                return nv
    # From this address numbers base 10 or other
    try:
        fv = float(v)
    except (TypeError, ValueError):
        # An error is raised if not a number so return text string
        return v
    # Test numeric value if it is an integer so we return, e.g., 1 and not 1.0
    if int(fv) == fv:
        return int(fv)
    return fv


def process_container(container: typing.Union[str, list, object], dc: type = str) -> list:
    """ Process container to format into list of dataclasses

    :param container:  this is a generic container to be standardized to list[dataclass].
        If it is a list then it is assumed that only the first element has its intended
        format and that the number of elements equals the number of variables in the dataclass.
    :type container:  str | list | dataclass | list[dataclass]

    :param dc:  this is either a value of string or a type-hinted dataclass used to standardize
        the container to List[dc]
    :type dc: type (either str or dataclass)
    """
    if dc == str:
        if isinstance(container, str):
            return [container]
        if isinstance(container, list):
            if not all(isinstance(x, str) for x in container):
                raise ValueError(
                    'If container is a list and dc=str, '
                    + 'then must have a string or list of strings'
                )
            return container
        raise ValueError(
            'If container is a list and dc=str, '
            + 'then must have a string or list of strings'
        )
    if isinstance(container, list):
        # List[objects]
        if all(isinstance(x, dc) for x in container):
            return container
        try:
            dc_fmt = get_dc_type_hints(dc)
        except TypeError as exc:
            raise TypeError('If type is not specified as string then dc must be a dataclass') from exc
        n_fields = len(dc_fmt.keys())
        #print('here:', container)
        fmt_0 = dc_fmt[dataclasses.fields(dc)[0].name]
        #print('  there:', fmt_0)
        # List[Values]
        if len(container) == n_fields:
            # Require that if a list of values is supplied, at least first element needs to
            # be the correct type (often this may be a string), it provides some guard to
            # distinguish between a list of lists or a list of values.
            if isinstance(container[0], fmt_0):
                return [dc(*container)]
            # If fail, still possible that it is List[List[values]]
        # List[List[values]]
        if all(isinstance(x, list) for x in container):
            if all(len(x) == n_fields and isinstance(x[0], fmt_0) for x in container):
                return [dc(*x) for x in container]
        raise ValueError(
            'If container is a list, '
            + 'it must contain only dataclasses or lists and not both'
        )
    if isinstance(container, dc):
        return [container]
    raise ValueError('process container reached end of decision tree with no action')


#
# Helpers to read and write dataclasses to lists and vice versa
#


def populate_list(c: object, dc: typing.Union[type, object]) -> list:
    """ Populate list of values for fields in dataclass dc that come from generic class c

    :param c:  class containing some or all of variables in dc
    :type c:  generic class object

    :param dc:  dataclass type containing the desired variables to be filled
    :type dc:  dataclass
    """
    if dataclasses.is_dataclass(dc):
        fields_dict = get_dc_type_hints(dc)
        if not isinstance(dc, type):
            dc = type(dc)
    else:
        raise TypeError('Second parameter must be a dataclass or an instance of a dataclass')
    # Now create list of extracted fields from c that exist in dc
    ret_list = []
    c_attrs = dir(c)
    for field in fields_dict:
        if field in c_attrs:
            ret_list.append(getattr(c, field))
        else:
            ret_list.append('')
    # Return instance of type dc
    return ret_list


def define_dataclass(c: object, dc: type) -> object:
    """ Output dataclass instance where values come from generic class c
        corresponding to attributes listed in dc

    :param c:  class containing some or all of variables in dc
    :type c:  generic class object

    :param dc:  dataclass definition containing the desired variables to be filled
    :type dc:  dataclass
    """
    try:
        dc_list = populate_list(c, dc)
    except TypeError as exc:
        raise TypeError(
            'Incorrect type of parameters: types should be class object, dataclass respectively'
        ) from exc
    return dc(*dc_list)


# Handy function to perform intial formatting of CSV read


def read_txt(input_list: list) -> list:
    """ Attempt to autoconvert values in input_list and return a new list containing guessed formatted values

    :param input_list:  unformatted list of strings
    :type input_list:  list[str]
    """
    return [txt2val(x) for x in input_list]


# Set of functions to prep data from dataclass for output to text only CSV write


def write_txt_class(c: object, dc: typing.Union[type, object]) -> typing.List[str]:
    """ Output list of strings where values come from generic class c with attributes from dc

    :param c:  class containing some or all of variables in dc
    :type c:  generic object

    :param dc:  dataclass definition containing the desired variables to output
    :type dc:  dataclass
    """
    try:
        dc_list = populate_list(c, dc)
    except TypeError as exc:
        raise TypeError(
            'Incorrect type of parameters: types should be class object, dataclass respectively'
        ) from exc
    return [val2txt(x) for x in dc_list]


# The next two functions are just variant / special cases of write_txt_class


def write_txt(dc: object) -> typing.List[str]:
    """ Output list of strings in order they appear in dataclass dc

    :param dc:  dataclass containing variables to output
    :type dc:  dataclass
    """
    return write_txt_class(dc, dc)


def write_txt_row(src_inst: object, dest_class: type = None) -> typing.List[str]:
    """ This function calls write_txt_class if dest_class is specified
        but calls write_txt if not specified

    :param src_inst:  class containing some or all of variables in dc
    :type src_inst:  generic object

    :param dest_class:  dataclass definition containing the desired variables to output
    :type dest_class:  dataclass
    """
    if dest_class is None:
        return write_txt(src_inst)
    return write_txt_class(src_inst, dest_class)
