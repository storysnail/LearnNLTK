#coding=utf8
import sys
from xlrd import open_workbook # xlrd用于读取xlsx
import xlwt  # 用于写入xlsx
from xlutils.copy import copy # 修改xlsx
'''
    XlsxOp用来读取Excel工作表中的数据，如果需要强大的excel编辑功能，可以使用xlwings。
    review21-en.xlsx Excel表格中只有一个sheet1工作表，该工作表共21001行，每一行的第一列
    都保存了一条用户评论。
    XlsxOp的作用就是打开该工作表、读取指定行内第一列中的评论内容。
'''
class XlsxOp(object):
    def __init__(self):
        self.XlsxOpState = False

    # 打开filename参数指定的Excel表格，成功返回True，失败返回False
    def Open_XLSX(self,filename):
        # 检查输入的filename参数
        if(len(filename) < 1):
            return self.XlsxOpState
        
        try:
            # 打开Excel表格
            workbook = open_workbook(filename)
            
            # 返回所有工作表的名称，sheet_names是个list类型
            sheet_names= workbook.sheet_names()
            # 得到工作表的数量
            sheet_num = len(sheet_names)

            # review21-en.xlsx表格只有一个工作表，所以sheet_num应该是1
            if sheet_num == 1:
                # 取得sheet1工作表并保存在本类的成员变量self.sheet1中
                # 当工作表通过数字索引表示时，索引值是从0开始计算的
                self.sheet1 = workbook.sheet_by_index(0)  
                self.XlsxOpState = True
        except Exception as err:
            print(f'{excel_path}或者{sheet_id}不存在')
            raise err
        
        return self.XlsxOpState

    # 读取成员变量self.sheet1指向的工作表，读取指定行第零列中的餐馆名和第一列中的评论内容
    # 成功读取返回餐馆名和评论内容，失败返回零长度字符串''
    def Read_XLSX_RestaurantName_and_Comment(self,row):
        # 检测表格文件是否正确打开
        if(self.XlsxOpState == False):
            return '',''

        #检测用户输入的参数row是否是有效数值
        # row的值不能小于0,row的值是从0开始的，若一共有10行，那么row的有效值就是0~9
        # 因为第一行并不是评论内容，所以需要略过row=0的这一行
        if(row < 1):  
            return '',''
        
        if(row < int(self.sheet1.nrows)):
            restaurant_name = self.sheet1.cell(row, 0).value
            Comment = self.sheet1.cell(row, 1).value
            return restaurant_name,Comment
        
        return '',''
