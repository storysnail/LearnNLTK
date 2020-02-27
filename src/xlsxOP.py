#coding=utf8
import sys
from xlrd import open_workbook # xlrd用于读取xlsx
import xlwt  # 用于写入xlsx
from xlutils.copy import copy # 修改xlsx

#如果需要强大的excel编辑功能，可以使用xlwings

def Read_Txt():
    file_object = open('review22.txt',encoding='utf-8') 
    try:
        line = file_object.readline() 
        while line:
            print(line)
            line = file_object.readline() 
    finally:
        file_object.close()

#Workbook就是一个excel工作表；
#Sheet是工作表中的一张表页;
#Cell就是简单的一个格
def Read_XLSX():
    workbook = open_workbook(r'./review21.xlsx')  # 打开xls文件
    sheet_names= workbook.sheet_names()  # 打印所有sheet名称，是个list
    sheet_num = len(sheet_names)

    if sheet_num == 1:
        sheet1 = workbook.sheet_by_index(0)  # 得到sheet1
        #sheet1= workbook.sheet_by_name('sheet1') 
        print(sheet1.name, sheet1.nrows, sheet1.ncols)  # sheet1的名称、行数、列数

        # 获得某一行或某一列数据，返回list
        #row_4 = sheet1.row_values(3)
        #cloumn_5 = sheet1.col_values(4)
        #Row_4 = sheet1.row(3)  # 此方法list中包含单元格类型
        #Column_5 = sheet1.col(4)  # 此方法list中包含单元格类型

        #col_values = sheet1.col_values(col)  
        #print(content)
        
        for row in range(0,int(sheet1.nrows),1):
            for col in range(0,int(sheet1.ncols),1):
                cell_value = sheet1.cell(row, col).value

                #cell_1_1 = ws.cell(0, 0).value
                #cell_1_1 = ws.row_values(0)[0]
                #cell_1_1 = ws.col_values(0)[0]
                #cell_1_1 = ws.row(0)[0].value
                #cell_1_1 = ws.col(0)[0].value
                print(cell_value)
                
            if row > 100:
                break

def Write_XLSX():
    # 创建一个新的工作薄
    Workbook = xlwt.Workbook(encoding="utf-8")
    
    # 在其上创建一个新的工作表
    sheet = Workbook.add_sheet('S1', cell_overwrite_ok=True)

    # 按单元格方式添加数据
    sheet.write(0, 0, 'HELLO')
    # 整行整列的添加数据
    title = ['NAME', 'AGE', 'SEX']
    for i in range(len(title)):
        sheet.write(0, i, title[i])
    name = ['Tom', 'Smith', 'SuiXin', 'Make']
    for j in range(len(name)):
        sheet.write(j + 1, 0, name[j])
    
    # 保存文件
    sheet.save('test.xls')

def Modify_XLSX():
    rd_book = xlrd.open_workbook('test.xls')
    
    # 使用copy方法将xlrd.Book对象拷贝为一个xlwt.workbook对象，可写入
    wt_book = copy(rd_book)
    # 获取一个sheet对象（支持index和name）
    ws = wt_book.get_sheet('S1')
    # 修改工作表
    age = [32, 38, 24, 40]
    for j in range(len(age)):
        ws.write(j + 1, 1, age[j])
        
    # 保存文件
    wt_book.save('test_new.xls')

if __name__=="__main__":
    Read_XLSX()

