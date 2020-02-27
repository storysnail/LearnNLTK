#coding:utf-8
import os
import time,string,random
import shutil
import sys

from xlsxOP import XlsxOp   


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
        
    Comment = excelFile.Read_XLSX_Comment(1239)
    print(Comment)

#=====================================================================================================


