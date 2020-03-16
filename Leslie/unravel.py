import pymysql
import nltk
import string
import re
import sys
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer

class usesql:
    def __init__(self):
        self.conn = pymysql.connect(host = 'localhost',port = 3306,
                                    user = 'Leslie',password = 'hsh56912341',
                                    db = 'Yelp',charset = 'utf8mb4')

    def getdata(self,row_id):   # 从mysql里读取数据
        sql = 'select review from review21 where id=%d;'%(row_id)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        return result[0]

    #这个成员函数没有改
    def output(self,word):
        cursor = self.conn.cursor()
        df = pd.DataFrame (list(word))
        df.to_sql(
            name='firstest',
            conn=conn,
            if_exists='append',
            index=False,
        )
        self.cursor.close()
    def sqlQuit(self):
        self.conn.close()
        

class prepare:
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
    
    def _main_(self,data):   #过程整合
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

sql = usesql()
Op = operate()

for i in range(1,10,1):
    data = sql.getdata(i)    #从mysql读取数据
    cleanword = Op._main_(data)   #导出清洗后的数据到mysql


#sql.output(cleanword)

sql.sqlQuit()
