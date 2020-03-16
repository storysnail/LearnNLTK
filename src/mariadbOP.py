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

    def close(self):
        if(self.MariadbOpState == True):
            self.conn.close()

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

            # 如果情感词表存在则删除
            cursor.execute("DROP TABLE IF EXISTS review21")
            cursor.execute(Create_review21_SQL)
            cursor.close()
        except Exception as err:
            print(f'创建review21表格失败')
            raise err

    def insert_review21_table(self,restaurant_name,review):
        if(self.MariadbOpState == False):
            return ''

        Insert_review21_SQL = '\
INSERT INTO review21(restaurant_name,review) \
VALUES (%s, %s);'
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

    def fetch_review21_table(self,row_id):
        if(self.MariadbOpState == False):
            return ''

        cursor = self.conn.cursor()
        sql = 'select * from review21 where id=%s;'
        param = ('%d' %(row_id))
        cursor.execute(sql,param)
        #result = cursor.fetchmany(10)   #测试代码的时候先用fetchmany（10）,正式运行时再改成fetchall
        result = cursor.fetchone()
        #raw = list(result)
        raw = result[0]
        return raw
    
    def create_AffectiveWords_table(self):
        if(self.MariadbOpState == False):
            return

        '''
            id:数据表中自动生成的唯一ID，由数据库维护
            word_str:情感词字符串
            line_num:该情感词所在的评论行
            ordinal_in_line:该情感词是line_num评论行中出现的第几个情感词
            restaurant_name:该情感词是评论哪个餐馆的
            tag:该情感词的词性（含词形、时态等概念）
            pos：和tag类似
            relativity：相对性
        '''
        Create_AffectiveWords_SQL = """CREATE TABLE `AffectiveWords` (
                  `id` int(10) NOT NULL AUTO_INCREMENT,
                  `word_str` char(20) NOT NULL,
                  `line_num` int(10) DEFAULT 0,
                  `ordinal_in_line` int(10) DEFAULT 0,
                  `restaurant_name` char(100) DEFAULT NULL,
                  `tag` char(20) DEFAULT NULL,
                  `pos` char(20) DEFAULT NULL,
                  `relativity` float DEFAULT 0,
                  PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
            
        try:
            cursor = self.conn.cursor()

            # 如果情感词表存在则删除
            cursor.execute("DROP TABLE IF EXISTS AffectiveWords")
            cursor.execute(Create_AffectiveWords_SQL)
            cursor.close()
        except Exception as err:
            print(f'创建AffectiveWords表格失败')
            raise err

    def insert_AffectiveWords_table(self,word_str,line_num,ordinal_in_line,restaurant_name,tag,pos,relativity):
        if(self.MariadbOpState == False):
            return ''

        Insert_AffectiveWord_SQL = "\
INSERT INTO AffectiveWords(word_str,line_num, ordinal_in_line,restaurant_name, tag,pos,relativity) \
VALUES ('%s', %d, %d, '%s', '%s', '%s', %f);" % (word_str, line_num, ordinal_in_line,\
restaurant_name, tag,pos,relativity)
        
        try:
            cursor = self.conn.cursor()
            print(Insert_AffectiveWord_SQL)
            cursor.execute(Insert_AffectiveWord_SQL)
            #print(cursor.rowcount)
            cursor.close()
            self.conn.commit()
        except Exception as err:
            self.conn.rollback()
            print(f'插入AffectiveWords表格失败')
            raise err
        
    def fetch_AffectiveWords_table(self):
        if(self.MariadbOpState == False):
            return ''

        cursor = self.conn.cursor()
        sql = 'select * from AffectiveWords;'
        cursor.execute(sql)
        result = cursor.fetchmany(10)   #测试代码的时候先用fetchmany（10）,正式运行时再改成fetchall
        raw = list(result)
        return raw

