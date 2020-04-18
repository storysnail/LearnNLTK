#coding:utf-8
import os
import time,string,random
import shutil
import sys
import gc
import re

from xlsxOP import XlsxOp
from mariadbOP import MariadbOp
from sentiWord import SentiWord
import numpy

def LoadExcelFile2SQL_Yelp_review21():
    #创建Excel操作类，打开Excel文件
    excelFile = XlsxOp()
    if(excelFile.Open_XLSX(r'./data/review21-en.xlsx') == False):
        print('invalid file name or sheet name')
        exit()

    #创建数据库操作类，打开数据库，创建review21表
    mariaDB = MariadbOp()
    mariaDB.open()
    mariaDB.create_review21_table()

    #从Excel文件中读取当前操作表的行数
    rows = excelFile.Get_Sheet1_rows()
    for i in range(1,rows,1):
        #得到行i的餐馆名和评论
        EN_restaurant_name,EN_Comment = excelFile.Read_XLSX_RestaurantName_and_Comment(i)
        #将餐馆名和评论插入数据库Yelp中的review21表
        mariaDB.insert_review21_table(EN_restaurant_name,EN_Comment)
    
    mariaDB.close()

#[[评论ID,句子ID,单词,pos_score,neg_score],
#[评论ID,句子ID,单词,pos_score,neg_score]]
def cal_score(SentiWords):
    #创建等比数列 2^0,2^1,2^2,2^3 .. 2^99共100个
    pro_series = numpy.logspace(0,99,100,base=2)
    
    words_score = []
    wordID = 0
    Weights = 0
    score = 0

    CurrentWord_ComID = SentiWords[0][0]
    CurrentWord_SenID = SentiWords[0][1]
    CurrentWord = SentiWords[0][2]
    #print('------------------------------')
    #print("开始计算  [%s]"%(CurrentWord))
    for SentiWord in SentiWords:
        if((CurrentWord == SentiWord[2]) and
           (CurrentWord_ComID == SentiWord[0]) and
           (CurrentWord_SenID == SentiWord[1])):
            #print("%.8f = (%.8f - %.8f) * (1 / %.8f)"%((SentiWord[3] - SentiWord[4]) * (1/pro_series[Weights]),SentiWord[3],SentiWord[4],pro_series[Weights]))
            score = score + (SentiWord[3] - SentiWord[4]) * (1/pro_series[Weights])
            #print("第%d次求和结果%.8f"%(Weights,score))
            if(Weights < 99): 
                Weights = Weights + 1
        else:
            words_score.append([CurrentWord_ComID,CurrentWord_SenID,wordID,CurrentWord,score])
            #print("%s -- score:[%.8f]"%(CurrentWord,score))
            #print('------------------------------')
            if(CurrentWord_ComID != SentiWord[0]):
                wordID = 0
            else:
                if(CurrentWord_SenID != SentiWord[1]):
                    wordID = 0
                else:
                    wordID = wordID + 1
                
            CurrentWord_ComID = SentiWord[0]
            CurrentWord_SenID = SentiWord[1]
            CurrentWord = SentiWord[2]
            Weights = 0
            score = 0
            #print('------------------------------')
            #print("开始计算  [%s]"%(CurrentWord))
            #print("%.8f = (%.8f - %.8f) * (1 / %.8f)"%((SentiWord[3] - SentiWord[4]) * (1/pro_series[Weights]),SentiWord[3],SentiWord[4],pro_series[Weights]))
            score = score + (SentiWord[3] - SentiWord[4]) * (1/pro_series[Weights])
            #print("第%d次求和结果%.8f"%(Weights,score))
            if(Weights < 99):
                Weights = Weights + 1
                        
    words_score.append([CurrentWord_ComID,CurrentWord_SenID,wordID,CurrentWord,score])
    #print("%s -- score:[%.8f]"%(CurrentWord,score))
    #print('------------------------------')
    return words_score
    
#=====================================================================================================
#主函数
#-----------------------------------------------------------------------------------------------------
if __name__=="__main__":
    #LoadExcelFile2SQL_Yelp_review21()

    '''
    mariaDB = MariadbOp()
    mariaDB.open()
    Percentage = 0
    total = 21000
    mariaDB.create_firstest_table()

    for i in range(1,total,1):
        data = mariaDB.fetch_review21_table(i)
        SentiWordScore = SentiWord(data)
        words_senti = SentiWordScore.SW_Get_words_senti_score()
        for word_senti in words_senti:
            mariaDB.insert_firstest_table(i,word_senti[0],word_senti[1],word_senti[2],
                                          word_senti[3],word_senti[4],word_senti[5]) 
        
        #print(words_senti)
        del SentiWordScore
        gc.collect()
        #print(gc.garbage)
        print(str(round(i/total*100,1)) + '%')
    
    mariaDB.close()
    '''

    mariaDB = MariadbOp()
    mariaDB.open()
    Percentage = 0
    total = 21000
    mariaDB.create_final_table()

    for i in range(1,total,10):
        words_scores = []
        #通过CommentID=M和SentenceID=N，得到第M条评论的第N个句子的所有情感词(形容词和副词)
        SentiWords = mariaDB.fetch_firstest_table(i,i+9)
        words_score = cal_score(SentiWords)
        for word_score in words_score:
            mariaDB.insert_final_table(word_score[0],word_score[1],word_score[2],word_score[3],word_score[4])
            
        del SentiWords
        gc.collect()
        

        print(str(round(i/total*100,1)) + '%')
    
    mariaDB.close()
#=====================================================================================================


