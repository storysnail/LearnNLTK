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

    #word_poses是成员函数get_wordnet_pos返回的list
    def wordstem(self,word_poses):
        lmtzr = WordNetLemmatizer()
        stemwords = []
        for word_pos in word_poses:
            """
            遍历word_poses list中的每一个结点并将结点赋值给word_pos，
            word_pos也是一个list，有两个结点，第一个word_pos[0]存储单词，第二个word_pos[1]存储pos
            在get_wordnet_pos成员函数中只处理了"J V N R"四种词性，其它词性一律返回空字符''
            lmtzr.lemmatize函数需要传人两个参数，第一个是单词、第二个是词性，如果传人的词性是空字符
            则会出错，所以这里将"J V N R"四种词性之外的其它词性一律标识为"N",注意：这种做法很粗暴，
            会因为标识了错误的词性而导致lmtzr.lemmatize返回错误的结果,查看输出结果可以发现as被错误的
            转换成了a!另外这里也没有对一些特殊词做处理，例如Im
            """
            if(len(word_pos[1]) < 1):
                lemmatized_word = lmtzr.lemmatize(word_pos[0],nltk.corpus.wordnet.NOUN)  
            else:
                lemmatized_word = lmtzr.lemmatize(word_pos[0],word_pos[1])  
            stemwords.append(lemmatized_word)

        return stemwords
    
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
        stemword = prep.wordstem(posedwords)          #词形还原
        print(stemword)
        #print('\n')
        #cleanword = prep.wordclean(stemword)         #去停用词
        #return cleanword          

Op = operate()
cleanword = Op._main_()   #导出清洗后的数据到mysql

#sql = usesql()
#sql.output(cleanword)

print('Finished')
