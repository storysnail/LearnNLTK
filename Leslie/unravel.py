import pymysql
import nltk
import string
import re
import sys
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer

class usesql:
    
    def _init_(self,conn,cursor):
        self.conn = conn
        self.cursor = cursor


    def getdata(self,sql):   # 从mysql里读取数据
        '''
        self.conn = pymysql.connect(
            host = 'localhost',
            port = 3306,
            user = 'Leslie',
            password = 'hsh56912341',
            db = 'Yelp',
            charset = 'utf8'
        )
        self.cursor = self.conn.cursor()
        sql='select review from review21;'
        readfile = self.cursor.execute(sql)
        result = readfile.fetchmany(10)   #测试的时候先用fetchmany（10）,正式运行时再改成fetchall
        return list(result)
        '''
        print("sql getdata")

    def output(self,word):
        '''
        self.cursor = self.conn.cursor()
        df = pd.DataFrame (list(word))
        df.to_sql(         #将输出结果转为dataframe格式存入mysql，表的名称为测试阶段暂定，正式名称最后命名为reviewdata
            name='firstest',
            conn=conn,
            if_exists='append',
            index=False,
        )
        self.cursor.close()
        self.conn.close()
        '''
        print("sql output")
        

class prepare:

    def _init_(self,word,relativity,id,ordinal):
        self.word = word
        self.relativity = relativity
        self.id = id
        self.ordinal = ordinal
        
    def sentoken(self,data):   #分句
        #载入英语的分句模型
        token = nltk.data.load('tokenizers/punkt/english.pickle')
        sents = token.tokenize(str(data))
        return sents
        
    def sentclean(self,sents):   #去除标点等无用的符号
        delEStr = string.punctuation + string.digits
        DelEDict = {}
        for ch in delEStr:
            DelEDict[ch] = ''
        trans = str.maketrans(DelEDict)

        cleansents = []
        for sent in sents:
            cleansent = sent.translate(trans) #去掉ASCII 标点符号和空格
            cleansents.append(cleansent)
        return cleansents

    def wordtoken(self,sents):     #分词
        words = []
        for sent in sents:
            word = nltk.word_tokenize(sent)
            words.append(word)
        return words

    def wordtag(self,words):        #标注词性
        words_tags = []
        for word in words:
            words_tags.extend(nltk.pos_tag(word))
        return words_tags


    def get_wordnet_pos(self,words_tags):  #通过tag获得pos
        posedwords = []
        for word_tag in words_tags:
            if word_tag[1].startswith('J'):
                pos = nltk.corpus.wordnet.ADJ
            elif word_tag[1].startswith('V'):
                pos = nltk.corpus.wordnet.VERB
            elif word_tag[1].startswith('N'):
                pos = nltk.corpus.wordnet.NOUN
            elif word_tag[1].startswith('R'):
                pos = nltk.corpus.wordnet.ADV
            else:
                pos =  ''

            posedwords.append([word_tag[0],pos])
        return posedwords
        
    def wordstem(self,posedwords):   #词干提取
        lmtzr = WordNetLemmatizer()
        stemword = []
        for word in self.word:
            if word:
                tag = nltk.pos_tag(word_tokenize(word))   # tag is like [('bigger', 'JJR')]
                pos = get_wordnet_pos(tag[0][1])
                if pos:                # lemmatize()方法将word还原成pos词性的形式
                    lemmatized_word = lmtzr.lemmatize(word, pos)
                    stemword.append(lemmatized_word)
                else:
                    stemword.append(word)
        return stemword
    
    def wordclean(self,word):   #去除停用词(emoji什么的先不管后续有时间再处理)
        for word in self.word:
            cleanword = [word for word in self.word if word not in stopwords.words('english')]
        return cleanword


class operate:
    
    def _main_(self):   #过程整合
        #sql = usesql()
        #data = sql.getdata('select review from review21;')    #从mysql读取数据
        data = "The food was awesome as always but the service and overall hospitality was unsatisfactory. The waiter, Jake, was very unprofessional when we asked a simple question regarding billing/gratuity. He walked off, slapped his leg, and uttered the words ""are you freaking kidding me?"". In addition to making matters even worse, there was a manager by the name of Kelly (red haired) that didn't alleviate the situation. She approached the table very frazzled, with an attitude and didn't introduce herself. I have worked in hospitality for about 8 years to date and the proper way would have been ""Good Evening All, my name is Kelly and I'm one of the managers here. I was told that you all have a concern regarding your bill ?"" SIMPLE. But instead, she made the entire situation much worse and continued to vent about how much of a terrible day she had. Rule #1 in Customer Service, guests/customers are first priority. We do not care how bad of a day you're having. If you're at work or clocked in, you are there to provide a [great] service and that Sunday evening, we did not. Overall, the vibe and the service was extremely lack luster. I advise upper management and corporate to have a mandatory Customer Service training/refresher course for their employees. Thank You"
        prep = prepare()
        sents = prep.sentoken(data)           #分句
        print(sents)
        print('\n')
        cleansents = prep.sentclean(sents)             #去除特殊符号
        print(cleansents)
        print('\n')
        words = prep.wordtoken(cleansents)             #分词
        print(words)
        print('\n')
        taggedwords = prep.wordtag(words)              #标注词性
        print(taggedwords)
        print('\n')
        posedwords = prep.get_wordnet_pos(taggedwords) #利用tag得到pos
        print(posedwords)
        print('\n')
        #后边的自己写吧
        #stemword = prep.wordstem(posedwords)          #词形还原
        #print(stemword)
        #print('\n')
        #cleanword = prep.wordclean(stemword)         #去停用词
        #return cleanword          

Op = operate()
cleanword = Op._main_()   #导出清洗后的数据到mysql

#sql = usesql()
#sql.output(cleanword)

print('Finished')
