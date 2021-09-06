"""
    Module Title:       method_helpers

    Author:             Mark Asiala
    Date:               2021/08/26
    Purpose:            This is a collection of functions to aid in creating
                        the methods for the primary and filesystem classes
"""

# Import global modules
import csv
import dataclasses
import logging
from sys import int_info
import openpyxl
import xlrd

# Import local modules
from formatting import read_txt, write_txt_class, write_txt_row, \
    process_container, fmt_dataclass, get_dc_type_hints

# Set up logging
logger = logging.getLogger(__name__)

# Register default dialect
csv.register_dialect('__unixpipe', delimiter='|', quoting=csv.QUOTE_NONE, lineterminator='\n')

def base_read_file(infile, rt_list, csv_dialect: str = '__unixpipe') -> int:
    """ Read pipe-delimited input file to dataclass records to add to database

    :param infile:  the path to open or file-like object
    :type infile:  string or pathlib.Path

    :param rt_list:  list of lists where each member list has form [<prefix>, <add_func>, <rt_class>]
    :type rt_list:  list[list]

    :param rt_list[i][0]:  record type indicator when writing ASCII file (e.g., <prefix>|var1|...)
    :type rt_list[i][0]:  string

    :param rt_list[i][1]:  function or method to add the dataclass record to database
    :type rt_list[i][1]:  function or method

    :param rt_list[i][2]:  dataclass structure of input variables in order of appearance on the ASCII file.
    :type rt_list[i][2]:  dataclass
    """
    nrows_read = 0
    with open(infile, 'r') as in_pipe:
        rows = csv.reader(in_pipe, csv_dialect)
        for row in rows:
            for row_defn in rt_list:
                try:
                    [prefix, add_func, rt_class] = row_defn
                except ValueError:
                    logger.warning(
                        'base_write_file: Row definition has insufficient number of values, ' \
                            + 'expected 3 got %d',
                        len(row_defn)
                    )
                    raise
                if prefix is not None:
                    if row[0] != prefix:
                        continue
                    row_inst = rt_class(*read_txt(row[1:]))
                else:
                    row_inst = rt_class(*read_txt(row))
                add_func(row_inst)
                nrows_read = nrows_read + 1
    return nrows_read

def base_write_file(outfile, rt_list, csv_dialect: str = '__unixpipe') -> int:
    """ Write pipe-delimited output file from dictionary of dataclasses

    :param outfile:  the path to open or file-like object
    :type outfile:  string or pathlib.Path

    :param rt_list:  list of lists where each member list has form [<prefix>, <row_dict>, <rt_class>]
    :type rt_list:  list[list]

    :param rt_list[i][0]:  record type indicator when writing ASCII file (e.g., <prefix>|var1|...)
    :type rt_list[i][0]:  string

    :param rt_list[i][1]:  dictionary linking dataclass key variable to dataclass instance for all records
    :type rt_list[i][1]:  dict[str, source dataclass]

    :param rt_list[i][2]:  dataclass structure of output variables in order of appearance on the ASCII file. Note that this can be a subset of the source dataclass variables
    :type rt_list[i][2]:  dataclass
    """
    nrows_written = 0
    with open(outfile, 'w') as out_pipe:
        f = csv.writer(out_pipe, csv_dialect)
        for row_defn in rt_list:
            try:
                [prefix, row_dict, rt_class] = row_defn
            except ValueError:
                logger.warning(
                    'base_write_file: Row definition has insufficient number of values, ' \
                        + 'expected 3 got %d',
                    len(row_defn)
                )
                raise
            for key in sorted(row_dict):
                if prefix is None:
                    row = write_txt_row(row_dict[key], rt_class)
                else:
                    row = [prefix] + write_txt_class(row_dict[key], rt_class)
                f.writerow(row)
                nrows_written = nrows_written + 1
    return nrows_written

def base_read_xls(infile, rt_list) -> int:
    """ Read older Excel files (.xls) to import data from each sheet into database

    :param infile:  the path to open or file-like object
    :type infile:  string or pathlib.Path

    :param rt_list:  list of lists where each member list has form [<prefix>, <add_func>, <rt_class>]
    :type rt_list:  list[list]

    :param rt_list[i][0]:  name of worksheet containing record type
    :type

    :param rt_list[i][1]:  function to add dataclass to defined database
    :type rt_list[i][1]:  function or class method

    :param rt_list[i][2]:  dataclass storing the record with variables in same order as columns in worksheet
    :type rt_list[i][2]:  dataclass
    """
    total_nrows_read = 0
    rt_counts = []
    with xlrd.open_workbook(infile) as wb:
        # This should use sheet name in future
        for nsheet in range(len(rt_list)):
            rt_nrows_read = 0
            [prefix, add_func, rt_class] = rt_list[nsheet]
            try:
                ws = wb.sheet_by_index(nsheet)
            except:
                logger.error('Error loading Sheet %d from Excel Workbook', nsheet)
                raise
            logger.debug(
                'Sheet %d for %s: NROWS = %d, NCOLS = %d',
                nsheet, repr(rt_class), ws.nrows, ws.ncols
            )
            for xlsrow in range(1, ws.nrows):
                row = [str(ws.cell_value(xlsrow, j)) for j in range(ws.ncols)]
                try:
                    row_inst = rt_class(*read_txt(row))
                except TypeError:
                    logger.error('Excel Workbook has %d columns in Sheet %d, expecting %d',\
                        ws.ncols, nsheet, len(get_dc_type_hints(rt_class)))
                    raise
                try:
                    add_func(row_inst)
                except:
                    logger.warning('%s was not added, import stopped.', repr(row_inst))
                    raise
                rt_nrows_read = rt_nrows_read + 1
            rt_counts.append[rt_nrows_read]
            total_nrows_read = total_nrows_read + rt_nrows_read
    return total_nrows_read, rt_counts

def base_read_xlsx(infile, rt_list) -> int:
    """ Read newer Excel files (.xlsx, .xlsm) to import data from each sheet into database

    :param infile:  the path to open or file-like object
    :type infile:  string or pathlib.Path

    :param rt_list:  list of lists where each member list has form [<prefix>, <add_func>, <rt_class>]
    :type rt_list:  list[list]

    :param rt_list[i][0]:  name of worksheet containing record type
    :type

    :param rt_list[i][1]:  function to add dataclass to defined database
    :type rt_list[i][1]:  function or class method

    :param rt_list[i][2]:  dataclass storing the record with variables in same order as columns in worksheet
    :type rt_list[i][2]:  dataclass
    """
    total_nrows_read = 0
    rt_counts = []
    with openpyxl.load_workbook(infile) as wb:
        for [sheet_name, add_func, rt_class] in rt_list:
            rt_nrows_read = 0
            try:
                ws = wb[sheet_name]
            except KeyError:
                raise KeyError(
                    'Excel worksheet %s not found in workbook %s, make sure source sheet is defined and named correctly.' \
                        % (sheet_name, str(infile))
                )
            for xlsrow in ws.values:
                row = [str(val) for val in xlsrow]
                try:
                    row_inst = rt_class(*read_txt(row))
                except TypeError:
                    raise TypeError('Excel workbook has %d columns in worksheet %s, expecting %d' \
                        % (len(row), sheet_name, len(get_dc_type_hints(rt_class)))
                    )
                try:
                    add_func(row_inst)
                except Exception:
                    raise
                rt_nrows_read = rt_nrows_read + 1
            rt_counts.append[rt_nrows_read]
            total_nrows_read = total_nrows_read + rt_nrows_read
    return total_nrows_read, rt_counts

def base_add_item(item_container, item_src_class, item_dest_class, item_key: str, item_dict: dict) -> list:
    """ Iterates over a container (e.g., list of item_src_class instances), creates item_dest_class
        instance, and then adds the instance to item_dict with key item_key 
    
    :param item_container: a variable containing one or more records in either raw or formatted form
    :type item_container: list of variables in order of item_src_class, item_src_class, or list[item_src_class]
    
    :param item_src_class: a dataclass with type hinting for each variable, typically defined to contain only the variables for input/output
    :type item_src_class: dataclass

    :param item_dest_class: a dataclass that contains a superset of variables as item_src_class and in the same order
    :type item_dest_class: dataclass

    :param item_key: one of the variables of item_dest_class that is unique to an instance
    :type item_key: string
    
    :param item_dict: dictionary that aids in the reference and organization of the item_dest_class instances
    :type item_dict: Dictionary[item_key, item_dest_class instance]
    """
    try:
        item_list = process_container(item_container, item_src_class)
    except ValueError:
        logger.error('base_add_item: item container does not match item class')
        raise
    items_added = []
    for item_raw in item_list:
        try:
            item_clean = fmt_dataclass(item_raw)
        except ValueError:
            logger.error('base_add_item: Incorrect types for item_container')
            raise
        item_inst = item_dest_class(*dataclasses.astuple(item_clean))
        try:
            item_inst_key = getattr(item_inst, item_key)
        except AttributeError:
            logger.error('base_add_item: item_key is not an attribute of item_class')
            raise
        if item_inst_key in item_dict:
            logger.info('Dataclass for %s already defined', item_inst_key)
            continue
        item_dict[item_inst_key] = item_inst
        items_added.append(item_inst_key)
        logger.debug('Dataclass for %s added', item_inst_key)
    return items_added
