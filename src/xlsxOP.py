#coding=utf8
import sys
from xlrd import open_workbook # xlrd用于读取xlsx
import xlwt  # 用于写入xlsx
from xlutils.copy import copy # 修改xlsx

#如果需要强大的excel编辑功能，可以使用xlwings
#Workbook就是一个excel工作表；
#Sheet是工作表中的一张表页;
#Cell就是简单的一个格
class XlsxOp(object):
    def __init__(self):
        self.XlsxOpState = False

    def Open_XLSX(self,filename):
        try:
            workbook = open_workbook(filename)  # 打开xls文件
            sheet_names= workbook.sheet_names()  # 返回所有sheet名称，sheet_names是个list
            sheet_num = len(sheet_names)
            if sheet_num == 1:
                self.sheet1 = workbook.sheet_by_index(0)  # 得到sheet1
                self.XlsxOpState = True
        except Exception as err:
            print(f'{excel_path}或者{sheet_id}不存在')
            raise err
        
        return self.XlsxOpState

    
    def Read_XLSX_Comment(self,row):
        if(self.XlsxOpState == False):
            return ''
        
        if(row < 0):
            return ''
        
        if(row > int(self.sheet1.nrows)):
            return ''
        
        cell_value = self.sheet1.cell(row, 1).value
        return cell_value

