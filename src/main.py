#coding:utf-8
import os
import time,string,random
import shutil
import sys

from xlsxOP import XlsxOp
from mariadbOP import MariadbOp
from Bow_CosineSimilarity import Bow_CosSim
from sentiWord import SentiWord

def Read_Txt(row):
    CurRow = 0
    getLine = ''
    
    file_object = open('./data/review20-cn.txt',encoding='utf-8') 
    try:
        line = file_object.readline() 
        while line:
            if(CurRow == row):
                getLine = line
                break
            
            line = file_object.readline()
            CurRow = CurRow + 1
    finally:
        file_object.close()

    return getLine

#=====================================================================================================
#主函数
#-----------------------------------------------------------------------------------------------------
if __name__=="__main__":
    excelFile = XlsxOp()
    if(excelFile.Open_XLSX(r'./data/review21-en.xlsx') == False):
        print('invalid file name or sheet name')
        exit()

    CN_Comment = Read_Txt(105)
    sentiWd = SentiWord(CN_Comment)
    stoplist='! , . / < > \ in'.split()
    sentiWd.SentiValue(stoplist)
    
    EN_restaurant_name,EN_Comment = excelFile.Read_XLSX_RestaurantName_and_Comment(10)
    sentiWd = SentiWord(EN_Comment)
    stoplist='! , . this at is a of the and to in'.split()
    sentiWd.SentiValue(stoplist)
    
    '''
    CN_Comment1 = Read_Txt(100)
    CN_Comment2 = Read_Txt(67)
    bcs = Bow_CosSim(CN_Comment1,CN_Comment2)
    stoplist='! , . / < > \ in'.split()
    stoplist.append('\n')
    bcs.CosSim(stoplist)
    
    EN_restaurant_name1,EN_Comment1 = excelFile.Read_XLSX_RestaurantName_and_Comment(10)
    EN_restaurant_name2,EN_Comment2 = excelFile.Read_XLSX_RestaurantName_and_Comment(11)
    bcs = Bow_CosSim(EN_Comment1,EN_Comment2)
    stoplist='! , . this at is a of the and to in'.split()
    bcs.CosSim(stoplist)
    
    
    mariaDB = MariadbOp()
    mariaDB.open()
    mariaDB.create_AffectiveWords_table()

    for i in range(1,20,1):
        restaurant_name,Comment = excelFile.Read_XLSX_RestaurantName_and_Comment(i)
        mariaDB.insert_AffectiveWords_table('word'+str(i),i,0,restaurant_name,'NNP','n',0.9)

    mariaDB.fetch_AffectiveWords_table()
    mariaDB.close()
    '''
#=====================================================================================================


