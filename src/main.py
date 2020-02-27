#coding:utf-8
import os
import time,string,random
import shutil
import sys

from xlsxOP import XlsxOp
from mariadbOP import MariadbOp



def Read_Txt():
    file_object = open('review22.txt',encoding='utf-8') 
    try:
        line = file_object.readline() 
        while line:
            print(line)
            line = file_object.readline() 
    finally:
        file_object.close()

#=====================================================================================================
#主函数
#-----------------------------------------------------------------------------------------------------
if __name__=="__main__":
    excelFile = XlsxOp()
    if(excelFile.Open_XLSX(r'./review21.xlsx') == False):
        print('invalid file name or sheet name')
        exit()

    mariaDB = MariadbOp()
    mariaDB.open()
    mariaDB.create_AffectiveWords_table()

    for i in range(1,20,1):
        restaurant_name,Comment = excelFile.Read_XLSX_RestaurantName_and_Comment(i)
        mariaDB.insert_AffectiveWord('word'+str(i),i,0,restaurant_name,'NNP','n',0.9)

    mariaDB.fetch()
    mariaDB.close()
#=====================================================================================================


