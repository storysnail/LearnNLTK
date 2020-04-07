''' 最后的final_scores输出有问题，应该是def的不对，也可能是没循环好'''

import pymysql
import pandas as pd
import nltk
import string
import re
import sys
import numpy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, BigInteger, NVARCHAR, Float
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer
from nltk.corpus import sentiwordnet as swn
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters


class usesql:
    def __init__(self):
        self.conn = pymysql.connect(host = 'localhost',port = 3306,
                                    user = 'Leslie',password = 'hsh56912341',
                                    db = 'Yelp',charset = 'utf8mb4')
     
        
    def getdata(self,i):   # 从mysql里读取数据，只读取一条
        result = '' #这里忽然忘了为什么要有这个''
        try:
            #sql = 'select review from review21 where id='+str(i)+';'  #参数是i
            sql = 'select review from review21 where id=%d;'%(i)
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close() 
        except:
            print("Error: unable to fetch data")
        finally:
            return result[0] #注意:result[0]是字符串，result则是包含一个字符串的元组
    
    def getSentenceIDs(self,CommentID):   # 得到每条评论哪些句子有情感词，把这些句子的id保存在结果中返回
        results = ''
        SentenceIDs = [] 
        try:
            sql = 'select `1` from firstest where `0`=%d;'%(CommentID) #0列是comment_id, 1列是sent_id
            cursor = self.conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
        except:
            print("Error: unable to fetch data")
        finally:
            if(results):
                for result in results:
                    if (SentenceIDs.count(result[0]) == 0): #如果SentenceIDs里没有result[0],append, 这么写是想要使sent_id不重复
                        SentenceIDs.append(result[0])
            return SentenceIDs
    
    def regetSentiWords(self,CommentID):   # 通过评论ID得到对应情感词元组
        result = ''
        try:
            sql = 'select `2`,`4`,`5` from firstest where `0`=%d;'%(CommentID) # 2列是word, 4列是pos分，5列是neg分
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        except:
            print("Error: unable to fetch data")
        finally:
            return result
    
    '''
    def getSentiWords(self,CommentID,SentenceID):   # 通过评论ID和句子ID得到对应情感词元组(对应计算多个情感词score的版本)
        result = ''
        try:
            sql = 'select `2`,`4`,`5` from firstest where `0`=%d and `1`=%d;'%(CommentID,SentenceID) # 2列是word, 4列是pos分，5列是neg分
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        except:
            print("Error: unable to fetch data")
        finally:
            return result
    '''
    
    def scoreout(self,word_scores):        
        final_scores = []
        for word_score in word_scores:
            final_scores.append(word_score) #   <----------这里改了一处  <-------------
        #for score in scores:
            #final_scores.append(score)
        return final_scores
               
    def sqlQuit(self):
        self.conn.close()

class pd_sql:  #这里使用了另一种数据库访问方法，按习惯是不应该混用两种数据库连接访问方法的，所以使用了pandas的单独class

    def output(self,result):    #将输出结果转为dataframe格式存入mysql，表的名称为测试阶段暂定，正式名称最后命名为reviewdata
        engine = create_engine('mysql+pymysql://Leslie:hsh56912341@localhost:3306/Yelp?charset=utf8') 
        df = pd.DataFrame (result)  #把传进来的数据结构转换成数据表格
        df.to_sql(             
            name = 'firstest',
            con = engine,
            if_exists='replace',
            index=False,
            #dtype = {'review_id': int(10)
             #        'sent_id': int(10)
              #       'word': varchar(500)
               #      'pos': char(20)
                #     'pos_score': float
                 #    'neg_score': float
                  #   'obj_score': float
                   #  'final_score': float
                    # }
            )

       
class prepare:

    def sentoken(self,data):   #分句
        #token = nltk.data.load('tokenizers/punkt/english.pickle')
        #sents = token.tokenize(str(data))
        text = re.sub('\n', ' ', str(data)) #将data里的换行符替换成空格
        if isinstance(text, str):
            text = text
        else:
            raise ValueError('Document is not string')
        point_re = re.compile(r'(\D)\.') #用于匹配以.结尾的非数字字符串
        text = re.sub(point_re, '\g<1>. ', str(text)) #\g<1>相当于引用匹配置换前的内容
        text = re.sub(r'\.', '. ', str(text))
        text = re.sub(r'\?', '? ', str(text))
        text = re.sub(r'\!', '! ', str(text))
        text = re.sub(r'i\. e\. ', 'i.e.', str(text)) #复原被插入了空格的缩略语
        text = text.strip() #移除字符串头尾指定的字符(默认为空格或换行符)
        
        punkt_param = PunktParameters()
        abbreviation = ['i.e']
        punkt_param.abbrev_types = set(abbreviation) #自定义缩写词表，集合set是一个无序不重复的序列
        tokenizer = PunktSentenceTokenizer(punkt_param)
        sents = tokenizer.tokenize(text)
        sents = [sent.strip() for sent in sents]
        return sents
    
    '''
    e.g.:
        punkt_param = PunktParameters()
        abbreviation = ['u.s.a', 'fig']
        punkt_param.abbrev_types = set(abbreviation)
        tokenizer = PunktSentenceTokenizer(punkt_param)
        tokenizer.tokenize('Fig. 2 shows a U.S.A. map.')  # It returns this to me: ['Fig. 2 shows a U.S.A. map.']
    '''

    def sentclean(self,sents):    #去除标点等无用的符号
        tmpsents = []
        replacement_patterns = [(r'won\'t', 'will not'),  #把won't缩写还原成will not形式
                                (r'can\'t', 'cannot'),
                                (r'i\'m', 'i am'),
                                (r'ain\'t', 'is not'),
                                (r'isnt', 'is not'),
                                (r'(\w+)\'ll', '\g<1> will'),
                                (r'(\w+)n\'t', '\g<1> not'),
                                (r'(\w+)\'ve', '\g<1> have'),
                                (r'(\w+)\'s', '\g<1> is'),
                                (r'(\w+)\'re', '\g<1> are'),
                                (r'(\w+)\'d', '\g<1> would')]
        patterns = [(re.compile(regex), repl) for (regex, repl) in replacement_patterns] #这里用re.compile(regex)置换了 regex,具体作用应该就是把regex给编译了
        for sent in sents:
            for (pattern, repl) in patterns:
                (tmpsent, n) = re.subn(pattern, repl, sent)  # re.subn('正则表达式（pattern）','替换的字符','待替换的字符串') 返回替换后的字符串及替换的次数
            tmpsents.append(tmpsent)
   
        delEStr = string.punctuation + string.digits     #再去除ASCII标点符号
        DelEDict = {}
        for char in delEStr:
            DelEDict[char] = '' # char是key, 令key对应的value都为空
        trans = str.maketrans(DelEDict) # 这里是在建立翻译表trans，str.maketrans(DelEDict) == str.maketrans(key,value) == str.maketrans(char, '')
        cleansents = []
        for tmpsent in tmpsents:
            cleansent = tmpsent.translate(trans) #利用翻译表trans去掉ASCII标点符号
            cleansents.append(cleansent)
        return cleansents
        
    
    def repeat_replace(self, word):  #通过递归调用处理重复字母的单词,例如"gooooooood"会被还原成"good"
        # \w 匹配非特殊字符(单词字符)，即字母，数字及下划线，* 指匹配前面的子表达式零次或多次。例如，zo* 能匹配 "z" 以及 "zoo"。
        repeat_reg = re.compile(r'(\w*)(\w)\2(\w*)') #关键就是这两行，感觉没看懂
        repl = r'\1\2\3'
        if wn.synsets(word):  # 判断当前字符串是否是单词
            return word
        repl_word = repeat_reg.sub(repl, word)
        if repl_word != word:
            return self.repeat_replace(repl_word)
        else:
            return repl_word
    
    #对于"I love u"这样有简写单词的强烈正向感情的句子还是不能正确处理，分词没办法正确将简写单词"u"还原成原有单词"you",这导致后面对词性词义的分析是错误的
    def wordtoken(self,cleansents):
        repeat_reg = re.compile(r'(\w*)(\w)\2(\w*)')
        repl = r'\1\2\3'
        wordss = []    #分词     
        for cleansent in cleansents: #取得一个句子
            New_words = []
            words = nltk.word_tokenize(cleansent) #对一个句子进行分词,得到这个句子中每个单词组成的列表
            for word in words:  #从单词列表中取得一个单词
                if wn.synsets(word): #如果这是一个有效单词则加入New_words列表
                    New_words.append(word)
                else: # 如果单词不是有效词汇,那么尝试清除其中的重复字母，看看能不能得到有效单词
                    New_words.append(self.repeat_replace(word))    
            wordss.append(New_words)
        return wordss
    
    def wordtag(self,wordss): #标注词性
        word_tagss = []
        for words in wordss: #words是一个句子的所有单词
            #word_tags.extend(nltk.pos_tag(words))
            word_tagss.append(nltk.pos_tag(words))  
        return word_tagss
    
    def wordNER(self,word_tagss): #命名实体
        NERItems = []
        for word_tags in word_tagss:
            NERItems.append(nltk.ne_chunk(word_tags))
        word_and_NER_tagss = []
        for item in NERItems:
            word_and_NER_tags = [] #一个句子里所有单词(包括识别的命名实体)及其词性会保存在这个列表里
            for item_tree in item:
                if hasattr(item_tree, 'label'):
                    NERName = ' '.join(c[0] for c in item_tree.leaves())
                    NERType = item_tree.label()
                    word_and_NER_tags.append((NERName,NERType))
                else:
                    word_and_NER_tags.append(item_tree)
            word_and_NER_tagss.append(word_and_NER_tags) 
        return word_and_NER_tagss
        
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
  
    #遍历lemmas列表，将其中的所有形容词和副词做情感词进行分析，之后将分析结果
    #组成列表[句子ID,还原后的词形,词性,pos_score,neg_score,obj_score],
    #再将这个列表加入senti_words列表
    def senti(self,cleanwords):
        senti_words = []
        for lemma in cleanwords:
            if(lemma[2] == wn.ADJ) or (lemma[2] == wn.ADV) or (lemma[2] == wn.VERB):
            #if(lemma[2] == wn.ADJ) or (lemma[2] == wn.ADV):
                SentiSynsets = swn.senti_synsets(lemma[1], lemma[2])
                SentiSynset_list = list(SentiSynsets)
                if(len(SentiSynset_list) > 0):
                    for SentiSynset in SentiSynset_list:
                        #[句子ID,还原后的词形,词性,pos_score,neg_score,obj_score]
                        senti_words.append([lemma[0], lemma[1],lemma[2],SentiSynset.pos_score(),SentiSynset.neg_score(),SentiSynset.obj_score()])
        return senti_words
        
    #def sent_uni_method(self,senti_words):        
        
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
        wordss = prep.wordtoken(cleansents)  #分词
        #print(wordss)
        #print('\n')   
        word_tagss = prep.wordtag(wordss)     #标注词性
        #print(word_tagss)
        #print('\n')
        word_and_NER_tagss = prep.wordNER(word_tagss) #命名实体
        #print(word_and_NER_tagss)
        #print('\n')
        word_poses = prep.get_wordnet_pos(word_and_NER_tagss)   #利用tag得到pos
        #print(word_poses)
        #print('\n')
        stemwords = prep.wordstem(word_poses)          #词形还原                                                            
        #print(stemwords)
        #print('\n')
        cleanwords = prep.wordclean(stemwords)         #去停用词
        #print(cleanwords)
        #print('\n')
        senti_words = prep.senti(cleanwords)  #根据词性得到评分
        #print(senti_words)
        #print('\n')
        return senti_words          

print("开始扫描数据提取情感词并存入数据库")
sql = usesql()  #先连接数据库，以免循环时重复连接
ps = pd_sql()
op = operate()
i=1
cleanreview = []
Percentage = 0
#total = 21001
total = 5     #测试版本少写几个
while i<total:
    #输出进度百分比
    print(str(round(i/total*100,1)) + '%')
    data = sql.getdata(i)
    senti_words = op._main_(data)  # 每运行一次_main_()就是处理一条review
    for senti_word in senti_words:
        #[评论ID,句子ID,还原后的词形,词性,pos_score,neg_score,obj_score]
        cleanreview.append([i,senti_word[0],senti_word[1],senti_word[2],senti_word[3],senti_word[4],senti_word[5]]) 
    ps.output(cleanreview)  #导出清洗后的数据到mysql
    i=i+1
    #print(data)
sql.sqlQuit()
print('100%,成功扫描情感词并存入数据库')
print('------------------------------')


#从数据库中提取CommentID段评论第一个情感词并计算其得分：
sql = usesql() 
op = operate()
pro_series = numpy.logspace(0,99,100,base=2)
word_scores = []  #    <----------这里从下面的循环里移动出来  <-------------
for CommentID in range(1,5,1):                  #       |
    op._main_(sql.getdata(CommentID))           #       |
                                                # <------
    SentiWords = sql.regetSentiWords(CommentID)
    if SentiWords:  #如果得到的情感词列表不是空的，那么就开始对这些情感词做评分计算
        wordID = 1
        Weights = 0
        score = 0
        CurrentSentiWord = SentiWords[0][0]
        for SentiWord in SentiWords: 
            if(CurrentSentiWord == SentiWord[0]):
                score = score + (SentiWord[1] - SentiWord[2]) * (1/pro_series[Weights])
                #print("第%d次求和结果%.8f"%(Weights,score))
                if(Weights < 100): 
                    Weights = Weights + 1
            else:
                pass   
        word_scores.append([CommentID,wordID,CurrentSentiWord,score]) #word_scores形式为 [[2, 1, 'love', 0.5], [2, 1, 'love', 1.0], [2, 1, 'love', 1.15625], [2, 1, 'love', 1.1875]]

#               ps改成sql
final_scores = sql.scoreout(word_scores) #这里就不管怎么都一个数字一个数字地print出来
for final_score in final_scores:
    print("第%s条评论，第%s个情感词%s，得分%s"%(final_score[0],final_score[1],final_score[2],final_score[3]))

sql.sqlQuit()
