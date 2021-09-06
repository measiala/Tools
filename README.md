# Tools

This is a collection of common tools to use across projects. No project specific tools should live here.

1. ``formatting``: This module includes a number of type conversion functions as well as functions to format, read and write type hinted dataclasses.
1. ``method_helpers``: This module provides some convenience function to read and write from a dataclass to a pipe delimited file.

## Formatting

The formatting functions are broadly separated into several groups and build upon one another going down.

### General Utilities

1. ``get_ga_types``: Standardized call to get base and argument types from a ``typing.Generic``.
1. ``get_dc_type_hints``: Customized version of ``typing.get_type_hints``.

### Base Formatting Functions

1. ``fmt_bool``: Formats known boolean value to specified format.
1. ``fmt_float``: Formats known float value to specified format.
1. ``fmt_int``: Formats known integer value to specified format.
1. ``fmt_none``: Formats known None value to specified format.
1. ``fmt_str``: Formats known string value to specified format.
1. ``fmt_dict``: Formats known dictionary value to specified format.
1. ``fmt_list``: Formats known list value to specified format.
1. ``fmt_set``: Formats known set value to specified format.
1. ``fmt_tuple``: Formats known tuple value to specified format.
1. ``fmt_value``: Using dynamic typing, it then calls the relevant function above to format value to specified format.
1. ``fmt_dataclass``: Formats dataclass values to type hints specified in its definition.

### Applications of the Base Functions

1. ``str2list``: Standardizes string or list input to list of string.
1. ``val2txt``: Converts generic input to text suitable for writing to text file.
1. ``txt2val``: Attempts to guess type of a text string within a limited set of types.
1. ``process_container``: Standardizes string, list, dataclass or list of dataclasses to a list of dataclass including defining the dataclass based on the sequence of values in the list.
1. ``define_dataclass``: Populates a dataclass instance taking its values from a second class.

### Helper Applications for Input and Output to ASCII Files

These applications grew from supporting ``namedtuples`` to ``dataclasses``. They can and will be cleaned up in the future to reduce redundancy.

1. ``read_txt``: Using ``txt2val`` it reads in a list of strings and returns a list of values using guessed types.
1. ``write_txt``: Using ``val2txt`` it reads in a list of various formatted values from a dataclass and returns a list of strings.
1. ``write_txt_class``: Using ``val2txt`` it returns a list of strings defined by the variables defined by the namedtuple or dataclass whose values are taken and reformatted from a second namedtuple or dataclass.
1. ``write_txt_row``: This function behaves like ``write_txt_class`` if the dest_class is specified and like ``write_txt`` if it is not specified.

## Method Helpers

The following helpers were developed in applications where a parent class holds a set of instances of a dataclass in a dictionary for organization, updating, and maintenance. 
1. ``__unixpipe``: This defines an internal default csv dialect that is pipe delimited.
1. ``base_read_file``: This reads from the specified ASCII file using the parameters for identifying and processing each record type into the given dataclass. It returns total number of records read from the file.
1. ``base_write_file``: This writes to the specified file file from a dictionary reference to a set of dataclass instances. It returns total number of records written to the file.
1. ``base_read_xls``: This reads from the specified XLS file using the parameters for identifying and processing each record type into the given dataclass. Its call is intended to be nearly transparent with calling the ``base_read_file`` using the same parameters. It returns total number of records read and number of records read by record type.
1. ``base_read_xlsx``: This reads from the specified XLSX file using the parameters for identifying and processing each record type into the given dataclass. Its call is intended to be nearly transparent with calling the ``base_read_file`` using the same parameters. It returns total number of records read and number of records read by record type.
1. ``base_add_item``: Iterates over a general container, creates an instance of the destination class and adds the instance to a specified dictionary using the given key. It returns a list of all keys added to aid subsequent processing.
