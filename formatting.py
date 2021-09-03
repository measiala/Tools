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

def get_dc_type_hints(dc: dataclasses.dataclass) -> dict:
    """ Create alternative to typing.get_field_types to see if fix problems """
    type_dict = {}
    try:
        fields = dataclasses.fields(dc)
    except (TypeError, AttributeError):
        logger.warning('Input to get_dc_type_hints must be a dataclass')
        raise
    for x in fields:
        if isinstance(x.type, (typing._GenericAlias, typing._VariadicGenericAlias)):
            ### Limited GenericAlias support to typing.Dict/List/Set/Tuple[bool/int/str]
            # python < 3.8
            _origin = x.type.__origin__
            _args = x.type.__args__
            # python 3.8+
            # _origin = x.get_origin()
            # _args = x.get_args()
            _args_in = True
            for _a in _args:
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

def fmt_bool(value, fmt):
    """ Convert known boolean value to fmt """
    if fmt == bool:
        return value
    if fmt in [str, list, set, tuple]:
        if fmt == str:
            return str(value)
        if fmt == list:
            return [value]
        if fmt == set:
            return {value}
        if fmt == tuple:
            return tuple([value])
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt = fmt.__origin__
        elem_fmt = fmt.__args__[0]
        if base_fmt in [dict, list, set, tuple]:
            return fmt_list([fmt_str(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_int(value, fmt):
    """ Convert known integer value to fmt """
    if fmt == int:
        return value
    if fmt in [bool, str, float, list, set, tuple]:
        if fmt == bool:
            # Strict interpretation as 1 = True else False vs non-zero = True
            return value == 1
        if fmt == str:
            return str(value)
        if fmt == float:
            return float(value)
        if fmt == list:
            return [value]
        if fmt == set:
            return {value}
        if fmt == tuple:
            return tuple([value])
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt = fmt.__origin__
        elem_fmt = fmt.__args__[0]
        if base_fmt in [dict, list, set, tuple]:
            return fmt_list([fmt_str(value, elem_fmt)], base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_none(value, fmt):
    """ Convert known None to fmt """
    if fmt == list:
        return []
    if fmt == str:
        return ''
    if fmt == set:
        return set()
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_str(value, fmt):
    """ Convert known string value to fmt """
    if fmt == str:
        return value
    if fmt in [int, float]:
        new_value = txt2val(value)
        if isinstance(new_value, (int, float)):
            return new_value
    if fmt in [dict, list, set, tuple, bool, pathlib.PosixPath, pathlib.Path]:
        if value == '':
            if fmt == dict:
                return {}
            if fmt == list:
                return []
            if fmt == set:
                return set()
            if fmt == tuple:
                return tuple()
            raise ValueError('Cannot handle putting blank value into format %s' % str(fmt))
        if fmt == list:
            return [value]
        if fmt == set:
            return {value}
        if fmt == tuple:
            return tuple([value])
        if fmt == bool:
            return value == 'True'
        if fmt == pathlib.PosixPath:
            return pathlib.PosixPath(value)
        if fmt == pathlib.Path:
            return pathlib.Path(value)
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt = fmt.__origin__
        elem_fmt = fmt.__args__[0]
        if base_fmt in [dict, list, set, tuple]:
            if value:
                return fmt_list([fmt_str(value, elem_fmt)], base_fmt)
            else:
                return fmt_str(value, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (value, str(fmt)))

# Format structured values (list, set, etc.)

def fmt_list(value, fmt):
    """ Convert known list value to fmt """
    if fmt == list:
        return value
    if fmt in [set, tuple, str, dict]:
        if fmt == set:
            return set(value)
        if fmt == tuple:
            return tuple(value)
        if fmt == str:
            # Return str(list) but without the square brackets
            return val2txt(value)
        if fmt == dict and len(value) % 2 == 0:
            # Convert list of dict pairs to dictionary
            temp = value
            return {temp[k]: temp[k+1] for k in range(0, len(temp), 2)}
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of list to format, then convert the list
        # base_fmt is standard generic format of type
        base_fmt = fmt.__origin__
        if base_fmt in [dict, list, set, tuple]:
            if len(value):
                new_list = []
                for elem_value, elem_fmt in zip(value, itertools.cycle(fmt.__args__)):
                    new_list.append(fmt_value(elem_value, elem_fmt))
                return fmt_list(new_list, base_fmt)
            else:
                return fmt_list(value, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_set(value, fmt):
    """ Convert known set to fmt """
    if fmt == set:
        return value
    if fmt in [list, tuple]:
        if fmt == list:
            return list(value)
        if fmt == tuple:
            return tuple(value)
    if isinstance(fmt, typing._GenericAlias):
        # Order is to convert all elements of set to format, then convert the set
        # base_fmt is standard generic format of type
        base_fmt = fmt.__origin__
        if base_fmt in [list, set, tuple]:
            new_set = set()
            for elem_value, elem_fmt in zip(value, itertools.cycle(fmt.__args__)):
                new_set.add(fmt_value(elem_value, elem_fmt))
            return fmt_set(new_set, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_tuple(value, fmt):
    """ Convert known tuple to fmt """
    if fmt == tuple:
        return value
    if fmt in [list, set]:
        if fmt == list:
            return list(value)
        if fmt == set:
            return set(value)
    if isinstance(fmt, typing._GenericAlias):
        # base_fmt is standard generic format of type
        base_fmt = fmt.__origin__
        if base_fmt in [list, set, tuple]:
            new_tuple = ()
            for elem_value, elem_fmt in zip(value, itertools.cycle(fmt.__args__)):
                new_tuple = new_tuple + (fmt_value(elem_value, elem_fmt),)
            return fmt_tuple(new_tuple, base_fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_value(value, fmt):
    """ Convert value to given fmt """
    # Note that we are purposely using type rather than isinstance to distingish bool
    # from int. isinstance will be true for both cases for value = True which is not
    # what we want here.
    if type(value) == fmt:
        return value
    if value is None:
        return fmt_none(value, fmt)
    if isinstance(value, list):
        return fmt_list(value, fmt)
    if isinstance(value, str):
        return fmt_str(value, fmt)
    if isinstance(value, bool):
        return fmt_bool(value, fmt)
    if isinstance(value, int):
        return fmt_int(value, fmt)
    if isinstance(value, set):
        return fmt_set(value, fmt)
    raise ValueError('Cannot handle putting %s into format %s' % (str(value), str(fmt)))

def fmt_dataclass(dc: dataclasses.dataclass) -> dataclasses.dataclass:
    """ Format the entries in dataclass according to its type hints """
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
## Routines to convert a value from one type to text and vice versa
##

def str2list(name):
    """ If name is string then return list else if already a list then simply return name """
    if not isinstance(name, (str, list)):
        logger.warning("Expecting name %s to be a string or a list", name)
        raise ValueError
    try:
        return fmt_value(name, list)
    except ValueError:
        logger.warning("Expecting name %s to be item that can be converted to a list", name)
        raise

def val2txt(v):
    """ Convert value v to a string form for easy exporting to a file """
    if isinstance(v, str):
        return v
    if v is None:
        return ''
    if isinstance(v, (bool, float, int, pathlib.Path, pathlib.PurePath, pathlib.PosixPath)):
        return str(v)
    if isinstance(v, list):
        nv = []
        for x in v:
            try:
                in_nv = val2txt(x)
            except ValueError:
                logger.warning('Element %s in list %s failed', str(x), str(v))
                raise
            else:
                nv.append(in_nv)
        return ','.join(nv)
    if isinstance(v, dict):
        d_list = []
        for k in v:
            d_list.append(val2txt(k))
            d_list.append(val2txt(v[k]))
        return val2txt(d_list)
    if isinstance(v, (tuple, set)):
        try:
            nv = val2txt(sorted(v))
        except ValueError:
            logger.warning('Cannot convert to text:', v)
            raise
        else:
            return nv
    logger.warning('Value unexpected: %s', str(v))
    logger.warning('Type of value is %s', type(v))
    raise ValueError

def txt2val(v):
    """ Convert text value provided to guessed python type """
    # If the string contains a boolean keyword then treat as boolean
    if not isinstance(v, str):
        return v
    if v in ['True', 'true', 'False', 'false']:
        return v.lower() == 'true'
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
    """ Process container to format into list of dataclasses """
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

def define_dataclass(c, dc: dataclasses.dataclass) -> dataclasses.dataclass:
    """ Output dataclass where values come from generic class c with attributes from dc """
    # Note write_txt_class(c,t) == write_txt(define_tup_class(c,t))
    ret_list = []
    c_attrs = dir(c)
    for field in get_dc_type_hints(dc):
        if field in c_attrs:
            ret_list.append(getattr(c, field))
        else:
            ret_list.append('')
    return dc(*ret_list)

def read_txt(input_list):
    """ Attempt to autoconvert values in input_list and return a new list """
    return [txt2val(x) for x in input_list]

def write_txt(dc) -> list:
    """ Output list of strings where values come from attributes from dataclass dc """
    try:
        field_names = get_dc_type_hints(dc)
    except (TypeError, AttributeError):
        try:
            field_names = dc._fields
        except AttributeError:
            logger.warning('Input to write_txt must be dataclass or tuple')
            raise TypeError
    return [val2txt(getattr(dc, field)) for field in field_names]

def write_txt_class(c, dc) -> list:
    """ Output list of strings where values come from generic class c with attributes from dc """
    try:
        field_names = get_dc_type_hints(dc)
    except (TypeError, AttributeError):
        try:
            field_names = dc._fields
        except AttributeError:
            logger.warning('Input to write_txt must be dataclass or tuple')
            raise TypeError
    return [val2txt(getattr(c, field)) for field in field_names]

def write_txt_row(src_inst, dest_class=None):
    """ This function acts like write_txt_class if dest_class is specified
        but is equivalent to write_txt if not specified """
    if dest_class is None:
        dest_class = type(src_inst)
    try:
        field_names = get_dc_type_hints(dest_class)
    except (TypeError, AttributeError):
        logger.warning('Input to write_txt_row must be dataclass')
        raise TypeError
    return [val2txt(getattr(src_inst, field)) for field in field_names]
