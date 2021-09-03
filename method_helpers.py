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
import xlrd

# Import local modules
from tools.formatting import read_txt, write_txt_class, write_txt_row, \
    process_container, fmt_dataclass, get_dc_type_hints

# Set up logging
logger = logging.getLogger(__name__)

def base_read_file(infile, row_list) -> int:
    """ Write pipe-delimited output file from dictionary of dataclasses """
    nrows_read = 0
    with open(infile, 'r') as in_pipe:
        rows = csv.reader(in_pipe, 'unixpipe')
        for row in rows:
            for row_defn in row_list:
                try:
                    [prefix, add_func, row_class] = row_defn
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
                    row_inst = row_class(*read_txt(row[1:]))
                else:
                    row_inst = row_class(*read_txt(row))
                add_func(row_inst)
                nrows_read = nrows_read + 1
    return nrows_read

def base_write_file(outfile, row_list) -> int:
    """ Write pipe-delimited output file from dictionary of dataclasses """
    nrows_written = 0
    with open(outfile, 'w') as out_pipe:
        f = csv.writer(out_pipe, 'unixpipe')
        for row_defn in row_list:
            try:
                [prefix, row_dict, row_class] = row_defn
            except ValueError:
                logger.warning(
                    'base_write_file: Row definition has insufficient number of values, ' \
                        + 'expected 3 got %d',
                    len(row_defn)
                )
                raise
            for key in sorted(row_dict):
                if prefix is None:
                    row = write_txt_row(row_dict[key], row_class)
                else:
                    row = [prefix] + write_txt_class(row_dict[key], row_class)
                f.writerow(row)
                nrows_written = nrows_written + 1
    return nrows_written

def base_read_xlsx(infile, row_list) -> int:
    """ Write pipe-delimited output file from dictionary of dataclasses """
    nrows_read = 0
    with xlrd.open_workbook(infile) as wb:
        for nsheet in range(len(row_list)):
            [prefix, add_func, row_class] = row_list[nsheet]
            try:
                ws_memo = wb.sheet_by_index(nsheet)
            except:
                logger.error('Error loading Sheet %d from Excel Workbook', nsheet)
                raise
            logger.debug(
                'Sheet %d for %s: NROWS = %d, NCOLS = %d',
                nsheet, repr(row_class), ws_memo.nrows, ws_memo.ncols
            )
            for xlsrow in range(1, ws_memo.nrows):
                row = [str(ws_memo.cell_value(xlsrow, j)) for j in range(ws_memo.ncols)]
                try:
                    row_inst = row_class(*read_txt(row))
                except TypeError:
                    logger.error('Excel Workbook has %d columns in Sheet %d, expecting %d',\
                        ws_memo.ncols, nsheet, len(get_dc_type_hints(row_class)))
                    raise
                try:
                    add_func(row_inst)
                except:
                    logger.warning('%s was not added, import stopped.', repr(row_inst))
                    raise
                nrows_read = nrows_read + 1
    return nrows_read

def base_add_item(item_container, item_src_class, item_dest_class, item_key, item_dict) -> list:
    """ Iterates over a container (e.g., list of item_src_class instances), creates item_dest_class
        instance, and then adds the instance to item_dict with key item_key """
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
