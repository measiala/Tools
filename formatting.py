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
import logging
import pathlib
import typing

# Set up logging
logger = logging.getLogger(__name__)

# Alternative to typing.get_field_types that is more robust for subclasses
# and also selective uses detailed versus generic type hints
def get_ga_types(ga_type):
    """ Return base origin and arguments type of Generic type in a version-independent method
    
    :param ga_type: Generic type defined using typing
    :type ga_type: typing.Generic
    """
    try:
        # python 3.8+: functions were added in 3.8
        _origin = typing.get_origin(ga_type)
        _args = typing.get_args(ga_type)
    except AttributeError:
        # python < 3.8: above results in AttributeError where not supported
        _origin = ga_type.__origin__
        _args = ga_type.__args__
    return _origin, _args

def get_dc_type_hints(dc: dataclasses.dataclass) -> dict:
    """ Create alternative to typing.get_field_types to see if fix problems 
    
    :param dc: dataclass with type hinting from which we will extract the type hints into a dictionary
    :type dc: dataclass
    """
    type_dict = {}
    try:
        fields = dataclasses.fields(dc)
    except (TypeError, AttributeError):
        logger.warning('Input to get_dc_type_hints must be a dataclass')
        raise
    for x in fields:
        if isinstance(x.type, (typing._GenericAlias, typing._VariadicGenericAlias)):
            ### Limited GenericAlias support to typing.Dict/List/Set/Tuple[bool/int/str]
            _args_in = True
            _origin, _args = get_ga_types(x.type)
            for _a in _args:
                # Only process typing.GenericAlias[bool/int/str/list/set/tuple]
                if _a not in [bool, int, str, list, set, tuple]:
                    _args_in = False
                    break
            if _origin in [list, dict, set, tuple] and _args_in:
                type_dict[x.name] = x.type              # Try basic GenericAlias approach
            else:
                type_dict[x.name] = _origin             # This removes the types of the args
        else:
            type_dict[x.name] = x.type
    return type_dict

# Format single element values, form is : fmt_<dynamic_type>(value, <dest_type>)

def fmt_bool(value, fmt) -> typing.Any:
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
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt, _args = get_ga_types(fmt)
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            return fmt_list([fmt_bool(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_float(value, fmt) -> typing.Any:
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
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt, _args = get_ga_types(fmt)
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            return fmt_list([fmt_float(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_int(value, fmt) -> typing.Any:
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
        return not (value == 0)
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
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt, _args = get_ga_types(fmt)
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            print(base_fmt, elem_fmt, fmt_int(value, elem_fmt))
            return fmt_list([fmt_int(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_none(value, fmt) -> typing.Any:
    """ Convert known None value to fmt 
    
    :param value:  None value to be reformatted
    :type value:  None

    :param fmt:  destination format: str | None | dict | list[] | set[] | tuple[]
    :type fmt:  type class
    """
    # Simple conversions
    if fmt == None:
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
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt, _args = get_ga_types(fmt)
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            return fmt_list([fmt_str(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_str(value, fmt) -> typing.Any:
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
            raise
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
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt, _args = get_ga_types(fmt)
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            if value:
                return fmt_list([fmt_str(value, elem_fmt)], base_fmt)
            else:
                return fmt_str(value, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (value, str(fmt)))

def fmt_dict(value, fmt) -> typing.Any:
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
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt, _args = get_ga_types(fmt)
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

def fmt_list(value, fmt) -> typing.Any:
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
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt, _args = get_ga_types(fmt)
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
            else:
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
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of set to format, then convert the set
        # base_fmt is standard generic format of type
        base_fmt, _args = get_ga_types(fmt)
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            new_set = {fmt_value(x, elem_fmt) for x in value}
            return fmt_set(new_set, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_tuple(value, fmt) -> typing.Any:
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
    if isinstance(fmt, typing._GenericAlias):
        # base_fmt is standard generic format of type
        base_fmt, _args = get_ga_types(fmt)
        elem_fmt = _args[0]
        if base_fmt in [list, set, tuple]:
            new_tuple = tuple([fmt_value(x, elem_fmt) for x in value])
            return fmt_tuple(new_tuple, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_value(value, fmt) -> typing.Any:
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

def fmt_dataclass(dc: dataclasses.dataclass) -> dataclasses.dataclass:
    """ Format the variable values in dataclass according to its defined type hints

    :param dc: dataclass with type hints defined but with unformatted values
    :type dc: dataclass
    """
    try:
        dc_dict = dataclasses.asdict(dc)
        dc_types = get_dc_type_hints(dc)
    except TypeError:
        logger.warning('Must supply a type hinted dataclass as input')
        raise

    rdc_dict = {}
    for x in dc_dict:
        try:
            rdc_dict[x] = fmt_value(dc_dict[x], dc_types[x])
        except TypeError:
            logger.warning(
                'Check that %s is in dataclass fields: %s', x, list(dc_dict.keys())
            )
            logger.warning(
                'Check that %s is in dataclass type hints: %s', x, list(dc_types.keys())
            )
            raise
        except ValueError:
            logger.warning(
                'Cannot handle putting field %s = %s into format %s',
                str(x), str(dc_dict[x]), str(dc_types[x])
            )
            raise

    rdc = getattr(dc, '__class__')
    return rdc(**rdc_dict)

##
## Routines to convert a value from one type to text and vice versa. These can serve as
## examples of specialized applications of the formatting above.
##

def str2list(name) -> list:
    """ If name is string then return list else if already a list then simply return name 
    
    :param name:  standardizes input of string or list to be a list
    :type name:  string | list
    """
    if not isinstance(name, (str, list)):
        logger.warning("Expecting name %s to be a string or a list", name)
        raise ValueError
    try:
        return fmt_value(name, list)
    except ValueError:
        logger.warning("Expecting name %s to be item that can be converted to a list", name)
        raise

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
    if isinstance(v, (bool, dict, float, int, list, tuple)):
        return fmt_value(v, str)
    raise ValueError('Following value cannot be converted to text', v)

def txt2val(v) -> typing.Any:
    """ Convert text value provided to guessed python type 
    
    :param v:  value of unknown type read in from a string input
    :type v:  string
    """
    # If the string contains a boolean keyword then treat as boolean
    if not isinstance(v, str):
        return v
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

def process_container(container, dc: dataclasses.dataclass = str) -> list:
    """ Process container to format into list of dataclasses 
    
    :param container:  this is a generic container to be standardized to list[dataclass]. 
        If it is a list then it is assumed that only the first element has its intended 
        format and that the number of elements equals the number of variables in the dataclass.
    :type container:  str | list | dataclass | list[dataclass]
    """
    if dc == str:
        if isinstance(container, list):
            for x in container:
                if not isinstance(x, str):
                    raise ValueError(
                        'If container is a list and dc=str, ' \
                        + 'then must have a string or list of strings'
                    )
            return container
        if isinstance(container, str):
            return [container]
        raise ValueError(
            'If container is a list and dc=str, ' \
            + 'then must have a string or list of strings'
        )
    if isinstance(container, list):
        if isinstance(container[0], dc):
            # List containing a dataclass
            for x in container:
                if not isinstance(x, dc):
                    raise ValueError(
                        'If container is a list, ' \
                        + 'it must contain only dataclasses or lists and not both'
                    )
            return container
        if isinstance(container[0], list):
            # List containing a list
            for x in container:
                if not isinstance(x, list):
                    raise ValueError(
                        'If container is a list, ' \
                        + 'it must contain only dataclasses or lists and not both'
                    )
                if len(x) != len(dataclasses.fields(dc)):
                    raise ValueError(
                        'If container is a list of lists, ' \
                        + 'each list must equal length of the total number of fields'
                    )
            return [dc(*x) for x in container]
        if isinstance(container[0], typing.get_type_hints(dc)[dataclasses.fields(dc)[0].name]):
            # List containing whose first entry is of correct dataclass field type
            if len(container) != len(dataclasses.fields(dc)):
                raise ValueError(
                    'If container is a list of field values, ' \
                    + 'the list must equal length of the total number of fields'
                )
            return [dc(*container)]
        raise ValueError('Container is a list but cannot be processed')
    if isinstance(container, dc):
        return [container]
    raise ValueError('process container reached end of decision tree with no action')

##
## Helpers to read and write dataclasses to lists and vice versa
##

def define_dataclass(c: object, dc: dataclasses.dataclass) -> dataclasses.dataclass:
    """ Output dataclass instance where values come from generic class c corresponding to attributes listed in dc 
    
    :param c:  class containing some or all of variables in dc
    :type c:  generic object

    :param dc:  dataclass definition containing the desired variables to be filled
    :type dc:  dataclass
    """
    # Note write_txt_class(c,t) == write_txt(define_tup_class(c,t))
    ret_list = []
    c_attrs = dir(c)
    for field in get_dc_type_hints(dc):
        if field in c_attrs:
            ret_list.append(getattr(c, field))
        else:
            ret_list.append('')
    return dc(*ret_list)

def read_txt(input_list) -> list:
    """ Attempt to autoconvert values in input_list and return a new list containing guessed formatted values
    
    :param input_list:  unformatted list of strings
    :type input_list:  list[str]
    """
    return [txt2val(x) for x in input_list]

def write_txt(dc) -> typing.List[str]:
    """ Output list of strings in order they appear in dataclass dc 
    
    :param dc:  dataclass containing variables to output
    :type dc:  dataclass
    """
    try:
        field_names = get_dc_type_hints(dc)
    except (TypeError, AttributeError):
        try:
            field_names = dc._fields
        except AttributeError:
            logger.warning('Input to write_txt must be dataclass or tuple')
            raise TypeError
    return [val2txt(getattr(dc, field)) for field in field_names]

def write_txt_class(c: object, dc: object) -> typing.List[str]:
    """ Output list of strings where values come from generic class c with attributes from dc 
    
    :param c:  class containing some or all of variables in dc
    :type c:  generic object

    :param dc:  dataclass definition containing the desired variables to output
    :type dc:  dataclass
    """
    try:
        field_names = get_dc_type_hints(dc)
    except (TypeError, AttributeError):
        try:
            field_names = dc._fields
        except AttributeError:
            logger.warning('Input to write_txt must be dataclass or tuple')
            raise TypeError
    return [val2txt(getattr(c, field)) for field in field_names]

def write_txt_row(src_inst: object, dest_class: object=None):
    """ This function acts like write_txt_class if dest_class is specified
        but is equivalent to write_txt if not specified 

    :param src_inst:  class containing some or all of variables in dc
    :type src_inst:  generic object

    :param dest_class:  dataclass definition containing the desired variables to output
    :type dest_class:  dataclass
    """
    if dest_class is None:
        dest_class = type(src_inst)
    try:
        field_names = get_dc_type_hints(dest_class)
    except (TypeError, AttributeError):
        logger.warning('Input to write_txt_row must be dataclass')
        raise TypeError
    return [val2txt(getattr(src_inst, field)) for field in field_names]
