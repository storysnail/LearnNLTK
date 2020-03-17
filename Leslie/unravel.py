import pymysql
import pandas as pd
import nltk
import string
import re
import sys
from sqlalchemy import create_engine
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer
from nltk.corpus import sentiwordnet as swn

class usesql:

    def __init__(self):
        self.conn = pymysql.connect(host = 'localhost',port = 3306,
                                    user = 'Leslie',password = 'hsh56912341',
                                    db = 'Yelp',charset = 'utf8mb4')
     
        
    def getdata(self,i):   # 从mysql里读取数据，只读取一条
        result = ''
        try:
            sql = 'select review from review21 where id='+str(i)+';'  #参数是i
            #或者sql = 'select review from review21 where id=%d;'%(i)，还有其它写法
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()
        except:
            print("Error: unable to fetch data")
        finally:
            return result[0] #注意:result[0]是字符串，result则是包含一个字符串的list
         

    def output(self,result):    #将输出结果转为dataframe格式存入mysql，表的名称为测试阶段暂定，正式名称最后命名为reviewdata
        #这里使用了另一种数据库访问方法，按习惯是不应该混用两种数据库连接访问方法的
        engine = create_engine('mysql+pymysql://Leslie:hsh56912341@localhost:3306/Yelp?charset=utf8') 
        #把传进来的数据结构转换成数据表格
        df = pd.DataFrame (result)
        #print(df)
        #存入数据库
        df.to_sql(             
            'firstest',
            con=engine,
            if_exists='replace',#覆盖入库  append  增量入库
            index=False)
        
    def sqlQuit(self):
        self.conn.close()
        
class prepare:

    def sentoken(self,data):   #分句
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
            cleansent = sent.translate(trans) #去掉ASCII标点符号
            cleansents.append(cleansent)
        return cleansents

    def wordtoken(self,cleansents):
        words = []    #分词     
        for cleansent in cleansents:
            word = nltk.word_tokenize(cleansent)
            words.append(word)
        return words

    def wordtag(self,words): #标注词性
        word_tagss = []   
        for word in words:
            #word_tags.extend(nltk.pos_tag(word))
            word_tagss.append(nltk.pos_tag(word)) 
        return word_tagss
    #此处的 word_tagss是一段评论 is like [[('bigger', 'JJR'),('best', 'JJR')],[('bigger', 'JJR'),('best', 'JJR')]]
    def get_wordnet_pos(self,word_tagss):  #通过tag获得pos
        sent_id = 1
        word_poses = []
        for word_tags in word_tagss:        #此处的word_tags是评论中的一个句子 is like [('bigger', 'JJR'),('best', 'JJR')]
            for word_tag in word_tags:  #此处的 word_tag是一个句子中的一个词 is like ('bigger', 'JJR')
                if word_tag[1].startswith('J'):
                    pos = nltk.corpus.wordnet.ADJ
                elif word_tag[1].startswith('V'):
                    pos = nltk.corpus.wordnet.VERB
                elif word_tag[1].startswith('N'):
                    pos = nltk.corpus.wordnet.NOUN
                elif word_tag[1].startswith('R'):
                    pos = nltk.corpus.wordnet.ADV        
                else:
                    pos = ''
                word_poses.append([sent_id,word_tag[0],pos])#这里的结构多了一个句子的ID
            sent_id = sent_id+1
                
        return word_poses

   
    def wordstem(self,word_poses):   
        lmtzr = WordNetLemmatizer()        # lemmatize()方法将word还原成pos词性的形式
        stemwords = []
        for word_pos in word_poses:
            if(len(word_pos[2]) < 1):
                lemmatized_word = lmtzr.lemmatize(word_pos[1],nltk.corpus.wordnet.NOUN)  
            else:
                lemmatized_word = lmtzr.lemmatize(word_pos[1],word_pos[2])  # word_pos = [word_tag[0],pos]
            stemwords.append([word_pos[0],lemmatized_word,word_pos[2]]) 
        return stemwords
   
    def wordclean(self,stemwords):   #去除停用词(emoji什么的先不管后续有时间再处理)
        cleanwords = []
        for stemword in stemwords:
            if stemword[1] not in stopwords.words('english'):
               cleanwords.append(stemword)
        return cleanwords

    #此处应有 打分

    #遍历lemmas列表，将其中的形容词做情感词进行分析，之后将分析结果
    #组成列表[还原后的词形,词性,pos_score,neg_score,obj_score]，
    #再将这个列表加入senti_words列表
    def senti(self,cleanwords):
        senti_words = []
        for lemma in cleanwords:
            #if(lemma[2] == wn.ADJ) or (lemma[2] == wn.ADV):
            if(lemma[2] == wn.ADJ):
                SentiSynsets = swn.senti_synsets(lemma[1], lemma[2])
                SentiSynset_list = list(SentiSynsets)
                if(len(SentiSynset_list) > 0):
                    for SentiSynset in SentiSynset_list:
                        #[句子ID,还原后的词形,词性,pos_score,neg_score,obj_score]
                        senti_words.append([lemma[0], lemma[1],lemma[2],SentiSynset.pos_score(),SentiSynset.neg_score(),SentiSynset.obj_score()])

        return senti_words



class operate:
    
    def _main_(self,data):   #连接数据库后的清洗过程整合                                                  
        
        #print(data)
        prep = prepare()
        sents = prep.sentoken(data)  #分句
        #print(sents)
        #print('\n')
        cleansents = prep.sentclean(sents)    #去除特殊符号
        #print(cleansents) 
        #print('\n')    
        words = prep.wordtoken(cleansents) 
        #print(words)
        #print('\n')    #分词
        word_tagss = prep.wordtag(words)     #标注词性
        #print(word_tags)
        #print('\n')
        word_poses = prep.get_wordnet_pos(word_tagss)   #利用tag得到pos
        #print(word_poses)
        #print('\n')
        stemwords = prep.wordstem(word_poses)          #词形还原                                                            
        #print(stemwords)
        #print('\n')
        cleanwords = prep.wordclean(stemwords)         #去停用词
        #print(cleanwords)
        #print('\n')
        senti_words = prep.senti(cleanwords)
        #print(senti_words)
        #print('\n')
        return senti_words          


sql = usesql()  #先连接数据库，以免循环时重复连接
op = operate()

i=1
cleanreview = []
Percentage = 0
#total = 21000
total = 210
while i<total:
    #输出进度百分比
    print(str(round(i/total*100,1)) + '%')
    data = sql.getdata(i)
    senti_words = op._main_(data)  # 每运行一次_main_()就是处理一条review
    for senti_word in senti_words:
        #[评论ID,句子ID,还原后的词形,词性,pos_score,neg_score,obj_score]
        cleanreview.append([i,senti_word[0],senti_word[1],senti_word[2],senti_word[3],senti_word[4],senti_word[5]]) 
    sql.output(cleanreview)  #导出清洗后的数据到mysql
    i=i+1
    #print(data)

print('100%')
sql.sqlQuit()

