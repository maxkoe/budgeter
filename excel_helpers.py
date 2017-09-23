import os
import shutil
from itertools import product

import pandas as pd

import openpyxl as pyxl
from gspread.utils import a1_to_rowcol, rowcol_to_a1

###############################################################################
# Convert a range string into a python list of individual cells               #
###############################################################################

def list_from_range_string(range_string) :
    """Extract all individual cell names from a Excel range.

    Keyword arguments:
        range_string -- The Excel expression for the range

    Example:
        If range_string == 'A1:B3' then the list 
        ['A1', 'B1', 'A2', 'B2', 'A3', 'B3'] is returned
    """
    colon_position = range_string.find(':')
    if colon_position == -1 :
        raise
    first_cell = range_string[:colon_position]
    last_cell = range_string[colon_position+1:]

    first_row, first_col = a1_to_rowcol(first_cell)
    last_row, last_col = a1_to_rowcol(last_cell)

    return [rowcol_to_a1(i,j) for i,j in 
            product(range(first_row, last_row+1), range(first_col, last_col+1))]

###############################################################################
# Read data from a specific range in an Excel worksheet; convert dates to     #
# pandas Timestamps                                                           #
###############################################################################

def date_convert(item) :
    """Try to get a DateTime from the Excel cell, independent if it is 
    represented by an integer, i.e. in the native Excel date format, or a 
    string representation
    """
    try :
          return pyxl.utils.datetime.from_excel(item)
    except :
        if type(item) is str :
            return pd.to_datetime(item)
        else :
            return pd.Timestamp(item)
        #pass


def get_df_by_range(sheet, first_cell, last_cell, date_cols=None) :
    """Read a given range on the given sheet and return a DataFrame containing 
    the data. The main functionality lies in reading only a small range in a 
    work book

    Keyword arguments:
        sheet      -- a openpyxl sheet object which is to be read
        first_cell -- the top left cell of the range to be read; in Excel cell 
                      notation
        last_cell  -- the bottom right cell of the range to be read; in Excel 
                      cell notation
        date_cols  -- a column (or list of columns) which are assumed to 
                      contain dates and shall be returned as pandas Timestamp 
                      object; can be given either as number (starting in zero) 
                      or a Excel column name

    """
    
    ## ToDo : Look if starting in zero is correct 

    data_rows = [[cell.value for cell in row] + \
                ['{0}:{1}'.format(row[0].coordinate, row[-1].coordinate)]
        for row in sheet[first_cell:last_cell]]

    df = pd.DataFrame(data_rows)
    new_index = df.iloc[:,range(len(df.columns)-1)].dropna(how='all').index
    if date_cols is not None and type(date_cols) is int :
        df.iloc[:,date_cols] = df.iloc[:,date_cols].apply(date_convert).copy()
    elif type(date_cols) is str : 
        df.loc[:,date_cols] = df.loc[:,date_cols].apply(date_convert).copy()
    elif type(date_cols) is list :
        for col in date_cols :
            if type(col) is int :
                df.iloc[:,col] = df.iloc[:,col].apply(date_convert).copy()
            if type(col) is str : 
                df.loc[:,col] = df.loc[:,col].apply(date_convert).copy()
    return df.loc[new_index]

###############################################################################
# Add a specific comment into multiple Excel cells                            #
###############################################################################

def put_comment_into_excel(sheet, cells, comment_text) :
    comment = pyxl.comments.Comment(comment_text, 'budgeter')
    if type(cells) is list :
        for cell in cells :
            sheet[cell].comment = comment
    elif type(cells) is str :
        sheet[cells].comment = comment
    else :
        raise ValueError('Unexpected type of argument recieved for cells')


###############################################################################
# Filewrappers for Excel Workbooks                                            #
# 1.) Open a workbook after a prompt asking if this is ok.                    #
# 2.) Process a workbook and ask if read data is as expected.                 #
###############################################################################

## ToDo : Hier fehlt einiges an Funktionalität zum Dateien bearbeiten  

def use_excel_for_data_entry(workbook_path, copy_mode=True,
                             temp_path='./temp_workbook.xlsx',
                             delete_temp=True, open_before_read=True) :
    """Open an Excel workbook for data entry. Afterwards parse it with pandas
    and prompt the result. Reopen the document, if the read data is not 
    satisfactory.

    Keyword arguments:
        workbook_path -- path to the Excel document to be opened
        copy_mode     -- if True, copy the document into a temporary file 
                         before opening it
        temp_path     -- path for the temporary file
        delete_temp   -- if True, delete the temporary file in the end 
    """
    def abort_with_q(signal) :
        if signal in ['Q', 'q'] :
            raise RuntimeError('The Excel data entry procedure was aborted.')

    if copy_mode :
        shutil.copy(workbook_path, temp_path)
        workbook_path = temp_path

    data_is_final = False

    while not data_is_final :
        # Opening the file 
        if open_before_read :
            signal = input('The file ' + workbook_path + ' will be opened in'
                           ' Excel for data entry. Enter Q to abort, enter'
                           ' anything else to continue. ')
            abort_with_q(signal)

            os.system('open ' + workbook_path)
            input('Make any input to continue.')

        # Reading the data
        read_data = pd.read_excel(workbook_path)
        
        ## ToDo : Here one could do a replace with a dict if the transaction 
        ##        type was abbreviated 

        print('The read data is:')
        display(read_data)
        print('')

        signal = input('If you are not satisfied with the read data, enter any'
                       ' number. If you do this, the workbook will be opened'
                       ' again. Continue with any other input; abort with Q.')
        abort_with_q(signal)

        def is_number(s) :
            try :
                float(s)
                return True
            except ValueError :
                return False

        if not is_number(signal) :
            print('OK.')
            data_is_final = True
        else :
            # This really makes sure the file will be opened again
            open_before_read = True

    if delete_temp :
        os.remove(temp_path)
    
    return read_data
