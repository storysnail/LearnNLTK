#coding:utf-8
import os
import time,string,random
import shutil
import sys

from xlsxOP import XlsxOp
from mariadbOP import MariadbOp

#=====================================================================================================
#主函数
#-----------------------------------------------------------------------------------------------------
if __name__=="__main__":
    excelFile = XlsxOp()
    if(excelFile.Open_XLSX(r'./data/review21-en.xlsx') == False):
        print('invalid file name or sheet name')
        exit()

    mariaDB = MariadbOp()
    mariaDB.open()
    '''
    mariaDB.create_review21_table()
    
    rows = excelFile.Get_Sheet1_rows()
    for i in range(1,rows,1):
        EN_restaurant_name,EN_Comment = excelFile.Read_XLSX_RestaurantName_and_Comment(i)
        mariaDB.insert_review21_table(EN_restaurant_name,EN_Comment)
    '''
    mariaDB.fetch_review21_table(1)
    mariaDB.close()

#=====================================================================================================


