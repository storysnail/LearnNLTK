#coding=utf8
import sys
import pymysql
'''
pymysql的参考手册地址 https://pymysql.readthedocs.io/en/latest/modules/index.html
'''

class MariadbOp(object):
    def __init__(self):
        self.MariadbOpState = False
        self.host = "localhost"
        self.port = 3306
        self.user = "Leslie"
        self.password = "hsh56912341"
        self.db = "Yelp"
        self.charset = "utf8mb4"

    #打开Yelp数据库        
    def open(self):
        try:
            self.conn = pymysql.connect(host=self.host,port=self.port,
                                           user=self.user,password=self.password,
                                           database=self.db,charset=self.charset)

            self.MariadbOpState = True
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT VERSION()")
            data = cursor.fetchone()
            print('Database version : %s ' % data)
            cursor.close()
        except Exception as err:
            print(f'连接mariadb失败')
            raise err
        
        return self.MariadbOpState

    #关闭Yelp数据库
    def close(self):
        if(self.MariadbOpState == True):
            self.conn.close()

    #=====================================================================================
    #在Yelp数据库中创建新的review21表,如果表已经存在则删除原来的表重新创建
    def create_review21_table(self):
        if(self.MariadbOpState == False):
            return

        Create_review21_SQL = """CREATE TABLE `review21` (
                  `id` int(10) NOT NULL AUTO_INCREMENT,
                  `restaurant_name` varchar(255) NOT NULL,
                  `review` text,
                  PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS review21")
            cursor.execute(Create_review21_SQL)
            cursor.close()
        except Exception as err:
            print(f'创建review21表格失败')
            raise err

    #向review21表插入数据
    def insert_review21_table(self,restaurant_name,review):
        if(self.MariadbOpState == False):
            return ''

        Insert_review21_SQL = 'INSERT INTO review21(restaurant_name,review) VALUES (%s, %s);'
        param = (restaurant_name, review)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(Insert_review21_SQL,param)
            #print(cursor.rowcount)
            cursor.close()
            self.conn.commit()
        except Exception as err:
            self.conn.rollback()
            print(f'插入review21表格失败')
            raise err

    #从review21表中读取数据
    def fetch_review21_table(self,row_id):
        if(self.MariadbOpState == False):
            return ''

        sql = 'select review from review21 where id=%s;'
        param = ('%d' %(row_id))

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql,param)
            result = cursor.fetchone()
            cursor.close()
            return result[0]
        except Exception as err:
            self.conn.rollback()
            print(f'读取review21表格失败')
            raise err

    #=====================================================================================
    #创建单词打分表
    #review_id是第几条评论
    #senti_id是评论中第几条句子
    def create_firstest_table(self):
        if(self.MariadbOpState == False):
            return

        Create_firstest_SQL = """CREATE TABLE `firstest` (
                  `num_id` int(64) NOT NULL AUTO_INCREMENT,
                  `review_id` int(10) NOT NULL,
                  `senti_id` int(10) NOT NULL,
                  `word` char(255),
                  `pos` char(10),
                  `pos_score` float DEFAULT 0,
                  `neg_score` float DEFAULT 0,
                  `obj_score` float DEFAULT 0,
                  PRIMARY KEY (`num_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
            
        try:
            cursor = self.conn.cursor()
            # 如果创建单词打分表存在则删除
            cursor.execute("DROP TABLE IF EXISTS firstest")
            cursor.execute(Create_firstest_SQL)
            cursor.close()
        except Exception as err:
            print(f'创建firstest表格失败')
            raise err

    def insert_firstest_table(self,review_id,senti_id,word,pos,pos_score,neg_score,obj_score):
        if(self.MariadbOpState == False):
            return ''

        Insert_firstest_SQL = "INSERT INTO firstest(review_id,senti_id, \
word,pos, pos_score,neg_score,obj_score) \
VALUES (%d, %d, '%s', '%s', %f, %f, %f);" % (review_id, senti_id, word,\
pos, pos_score,neg_score,obj_score)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(Insert_firstest_SQL)
            #print(cursor.rowcount)
            cursor.close()
            self.conn.commit()
        except Exception as err:
            self.conn.rollback()
            print(f'插入firstest表格失败')
            raise err

    def get_firstest_table_SentenceIDs(self,CommentID):   # 得到每条评论哪些句子有情感词，把这些句子的id保存在结果中返回
        results = ''
        SentenceIDs = [] 
        try:
            sql = 'select senti_id from firstest where review_id=%d;'%(CommentID) #0列是comment_id, 1列是sent_id
            cursor = self.conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
        except:
            print("Error: unable to fetch data")
        finally:
            if(results):
                for result in results:
                    if (SentenceIDs.count(result[0]) == 0): #去除重复SentenceID
                        SentenceIDs.append(result[0])
            return SentenceIDs
        
    def fetch_firstest_table(self,CommentID_start,CommentID_end):
        if(self.MariadbOpState == False):
            return ''

        sql = 'select review_id,senti_id,word,pos_score,neg_score from firstest where review_id between %d and %d;'%(CommentID_start,CommentID_end)

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as err:
            self.conn.rollback()
            print(f'读取firstest表格失败')
            raise err

    #=====================================================================================
    #创建单词最终打分表
    #review_id是第几条评论
    #senti_id是评论中第几条句子
    def create_final_table(self):
        if(self.MariadbOpState == False):
            return

        Create_final_SQL = """CREATE TABLE `final` (
                  `num_id` int(64) NOT NULL AUTO_INCREMENT,
                  `review_id` int(10) NOT NULL,
                  `senti_id` int(10) NOT NULL,
                  `word_id` int(10) NOT NULL,
                  `word` char(255),
                  `final_score` float DEFAULT 0,
                  PRIMARY KEY (`num_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
            
        try:
            cursor = self.conn.cursor()
            # 如果创建单词打分表存在则删除
            cursor.execute("DROP TABLE IF EXISTS final")
            cursor.execute(Create_final_SQL)
            cursor.close()
        except Exception as err:
            print(f'创建final表格失败')
            raise err

    def insert_final_table(self,review_id,senti_id,word_id,word,final_score):
        if(self.MariadbOpState == False):
            return ''

        Insert_final_SQL = "INSERT INTO final(review_id,senti_id, word_id,word,final_score) \
VALUES (%d, %d, %d,'%s', %f);" % (review_id, senti_id, word_id,word,final_score)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(Insert_final_SQL)
            #print(cursor.rowcount)
            cursor.close()
            self.conn.commit()
        except Exception as err:
            self.conn.rollback()
            print(f'插入final表格失败')
            raise err
        
    def fetch_final_table(self,CommentID,SentenceID):
        if(self.MariadbOpState == False):
            return ''

        sql = 'select word,final_score from final where review_id=%d and senti_id=%d;'%(CommentID,SentenceID)

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as err:
            self.conn.rollback()
            print(f'读取final表格失败')
            raise err


        

