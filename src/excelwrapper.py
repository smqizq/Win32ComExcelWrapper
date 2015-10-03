#!/usr/bin/env python
# --*-- encoding: iso-8859-1 --*--

import logging

from logging.handlers import RotatingFileHandler
from win32com import client

class Win32comExcelWrapper(object):
    def __init__(self):
        #avoid pop up blocking execution during automation
        self.displayAlerts = 0
        #Excel is visible
        self.visible = 1
        #you won't see what happens (faster)
        self.screenUpdating = False
        #clics on the Excel window have no effect
        #(set back to True before closing Excel)
        self.interactive = False
        self.initLogger()

    def initLogger(self):
        self.logger = logging.getLogger("Excel wrapper")
        #setting level to debug to see everything
        self.logger.setLevel(logging.DEBUG)
        #pretty self.logger.info(for logger
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        #First logger writting on file, 1MB max
        file_handler = RotatingFileHandler('ExcelWrapper.log', 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        #second logger writing over the console
        steam_handler = logging.StreamHandler()
        steam_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(steam_handler)

    def openExcel(self):
        """ Lauch Excel and set it's configuration"""
        self.logger.info("Opening Excel")
        self.xl = client.Dispatch("Excel.Application")
        self.logger.info("Setting Excel configuration")
        self.xl.DisplayAlerts = self.displayAlerts
        self.xl.Visible = self.visible
        self.xl.ScreenUpdating = self.screenUpdating
        self.xl.Interactive = self.interactive

    def getWorkbook(self, workbook_absolute_path):
        """Open a workbook and returns it"""
        self.logger.info("Opening workbook %s" %workbook_absolute_path)
        return self.xl.Workbooks.Open(workbook_absolute_path)

    def closeWorkbookWithoutSaving(self, wb):
        """close workbook without saving
            -wb : a workbook object
        """
        self.logger.info("Closing workbook without saving")
        wb.Close()

    def saveWorkbook(self, wb):
        """Save the workbook passed in parameters
            -wb : a workbook object
        """
        self.logger.info("Saving workbook")
        wb.Save()

    def saveWorkbookAs(self, wb, filename):
        """Save the workbook passed in parameters with a new name
            -wb : a workbook object
            -filename : a string
        """
        self.logger.info("Saving workbook as %s" %filename)
        wb.SaveAs(filename)

    def closeExcel(self):
        """Put back Excel interativity online and close it"""
        self.logger.info("Re-activating Excel interactivity")
        self.xl.Interactive = True
        self.logger.info("Closing Excel")
        self.xl.Quit()

    def getWorksheet(self, wb, ws_name_or_number):
        """Returns a worksheet object corresponding to ws_name
            -wb : a workbook object
            -ws_name : string containing the worksheet name or int for it's number
        """
        self.logger.info("Getting worksheet %s" %ws_name_or_number)
        return wb.Sheets(ws_name_or_number)

    def copyWorksheet(self, wb, source_sheet, new_name):
        """Copy a worksheet, source_sheet must be the name of the
        worksheet in a String, you cannot use an integer"""
        self.logger.info("Duplicating worksheet %s to %s" %(source_sheet, new_name))
        ws = wb.Sheets(source_sheet)
        ws.Copy(Before=wb.Sheets(source_sheet))
        ws = wb.Sheets(source_sheet + " (2)")
        ws.Name = new_name

    def deleteworksheet(self, wb, ws_name_or_number):
        """Delete a worksheet, you can use the number of the sheet,
        or it's actual name as a string, the first worksheet is 1"""
        self.logger.info("Deleting worksheet %s" %ws_name_or_number)
        ws = wb.Sheets(ws_name_or_number)
        ws.Delete()

    def insertWorksheet(self, wb, position, name):
        """Insert a new worksheet 1 step behind position
            -wb : workbook object from openWorkbook()
            -position : name or number of a sheet
            -name : name of the new worksheet
        """
        self.logger.info("inserting new worksheet %s before %s" %(name, position))
        wb.Sheets(position).Select()
        new_ws = wb.Worksheets.Add()
        new_ws.Name = name

    def moveWorksheet(self, wb, ws_name_or_number, new_position):
        """Moves a worksheet to a new position
            -wb : workbook object from openWorkbook()
            -ws_name_or_number : the worksheet to move
            -new_position : an int
        """
        self.logger.info("moving worksheet %s just before %s" %(ws_name_or_number, new_position))
        wb.Sheets(ws_name_or_number).Move(Before=wb.Sheets(new_position+1))

    def renameworkSheet(self, wb, ws_name_or_number, new_name):
        """Renames a worksheet
            -wb : workbook object from openWorkbook()
            -ws_name_or_number : the worksheet to rename
            -new_name : the new name
        """
        self.logger.info("Renaming worksheet %s to %s" %(ws_name_or_number, new_name))
        wb.Sheets(ws_name_or_number).Name = new_name

    def hideSheet(self, wb, ws_name_or_number):
        """Hide a worksheet by name or position"""
        self.logger.info("Hiding worksheet %s" %ws_name_or_number)
        wb.Sheets(ws_name_or_number).Visible = False

    def unhideSheet(self, wb, ws_name):
        """Unhide a worksheet by name (a hidden sheet has no position)"""
        self.logger.info("Unhiding worksheet %s" %ws_name)
        wb.Sheets(ws_name).Visible = True

    def writeCellValue(self, ws, row, column, value):
        """Write a value inside a cell
            -ws : worksheet object aquired by calling getWorksheet()
            -row : int representing cell row location
            -column : int representing cell column location
            -value : the value to be written
        """
        self.logger.info("Writing cell(%s, %s) value %s" %(row, column, value))
        ws.Cells(row, column).Value = value

    def writeCellFormula(self, ws, row, column, formula):
        """Write a formula inside a cell
            -ws : worksheet object aquired by calling getWorksheet()
            -row : int representing cell row location
            -column : int representing cell column location
            -formula : the formula to be written
        """
        self.logger.info("Writing cell(%s, %s) formula %s" %(row, column, formula))
        ws.Cells(row, column).FormulaR1C1 = formula

    def writeCell(self, ws, row, column, value):
        """Write a value inside a cell, autodetect forumula by cheking for '='
            -ws : worksheet object aquired by calling getWorksheet()
            -row : int representing cell row location
            -column : int representing cell column location
            -value : the value/formula to be written
        """
        def isFormulaR1C1(value):
            return isinstance(value, (str, unicode)) and len(value) > 1 and value[0] == '='
        if isFormulaR1C1(value):
            self.writeCellFormula(ws, row, column, value)
        else:
            self.writeCellValue(ws, row, column, value)

    def writeAreaCellByCell(self, ws, ul_row, ul_col, data):
        """write the content of data in an excel worksheet, autodetect formula,
        unrecommended for large amount of data, very slow
            -ws : worksheet object aquired by calling getWorksheet()
            -ul_row : upper left row of the location where the data mus be writen
            -ul_col : upper left column of the location where the data mus be writen
            -data : data stored in a list of list, each list is a row
        """
        for row in data:
            paste_column = ul_col
            for value in row:
                self.writeCell(ws, ul_row, paste_column, value)
                paste_column = paste_column +1
            ul_row = ul_row + 1

    def writeAreaInOneCall(self, ws, ul_row, ul_col, data):
        """Write an area in one call, 100 times faster than writing by cell
            -ws : worksheet object aquired by calling getWorksheet()
            -ul_row : upper left row of the location where the data mus be writen
            -ul_col : upper left column of the location where the data mus be writen
            -data : data store in a list of list, each list is a row
        """
        length = len(data)
        width = len(data[0])
        lr_row = ul_row+length-1
        lr_col = ul_col+width-1
        self.logger.info("writring data at location %s,%s to %s,%s" %(ul_row, ul_col, lr_row, lr_col))
        ws.Range(ws.Cells(ul_row, ul_col), ws.Cells(lr_row, lr_col)).Value = data

    class RangeCoordinate():
        """
        Class representing a Range Coordinate, typical use :

        data = ws.Range(
                         ws.Cells(coord.tline, coord.tcol),
                         ws.Cells(coord.bline, coord.bcol)
                        ).Value
        """
        def __init__(self, tline, tcol, bline, bcol):
            """Constructor
                -tline : top left line, int
                -tcol : top left column, int
                -bline : bottom right line, int
                -bcol : bottom right column, int
            """
            self.tline = tline
            self.tcol = tcol
            self.bline = bline
            self.bcol = bcol
