import pymysql
import pandas as pd
import nltk
import string
import re
import sys
import numpy
from sqlalchemy import create_engine
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
            return result[0] #注意:result[0]是字符串，result则是包含一个字符串的元组

    # 得到每条评论哪些句子有情感词，把这些句子的id保存在结果中返回
    def getSentenceIDs(self,CommentID):   
        results = ''
        SentenceIDs = [] 
        try:
            sql = 'select `1` from firstest where `0`=%d;'%(CommentID)
            cursor = self.conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
        except:
            print("Error: unable to fetch data")
        finally:
            if(results):
                for result in results:
                    if (SentenceIDs.count(result[0]) == 0):
                        SentenceIDs.append(result[0])
 
            return SentenceIDs
        
    # 通过评论ID和句子ID得到对应情感词元组
    def getSentiWords(self,CommentID,SentenceID):   
        result = ''
        try:
            sql = 'select `2`,`4`,`5` from firstest where `0`=%d and `1`=%d;'%(CommentID,SentenceID)
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        except:
            print("Error: unable to fetch data")
        finally:
            return result
        

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
        #token = nltk.data.load('tokenizers/punkt/english.pickle')
        #sents = token.tokenize(str(data))
        text = re.sub('\n', ' ', str(data))
        if isinstance(text, str):
            text = text
        else:
            raise ValueError('Document is not string!')
        point_re = re.compile(r'(\D)\.')
        text = re.sub(point_re, '\g<1>. ', str(text))
        #text = re.sub(r'\.', '. ', str(text))
        text = re.sub(r'\?', '? ', str(text))
        text = re.sub(r'!', '! ', str(text))
        text = re.sub(r'i\. e\. ', 'i.e.', str(text))
        text = text.strip()
        
        punkt_param = PunktParameters()
        abbreviation = ['i.e']
        punkt_param.abbrev_types = set(abbreviation)
        tokenizer = PunktSentenceTokenizer(punkt_param)
        sents = tokenizer.tokenize(text)
        sents = [sent.strip() for sent in sents]
        return sents

    #去除标点等无用的符号
    def sentclean(self,sents):
        #先去除can't这样的词
        Tmpsents = []
        replacement_patterns = [(r'won\'t', 'will not'),
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
        patterns = [(re.compile(regex), repl) for (regex, repl) in replacement_patterns]
        for sent in sents:
            for (pattern, repl) in patterns:
                (sent, count) = re.subn(pattern, repl, sent)
            Tmpsents.append(sent)

        #再去除标点符号
        delEStr = string.punctuation + string.digits
        DelEDict = {}
        for ch in delEStr:
            DelEDict[ch] = ''
        trans = str.maketrans(DelEDict)

        cleansents = []
        for sent in Tmpsents:
            cleansent = sent.translate(trans) #去掉ASCII标点符号
            cleansents.append(cleansent)
        return cleansents

        
    #通过递归调用处理重复字母的单词,例如"gooooooood"会被还原成"good"
    def repeat_replace(self, word):
        repeat_reg = re.compile(r'(\w*)(\w)\2(\w*)')
        repl = r'\1\2\3'

        if wn.synsets(word):  # 判断当前字符串是否是单词
            return word
        repl_word = repeat_reg.sub(repl, word)
        if repl_word != word:
            return self.repeat_replace(repl_word)
        else:
            return repl_word

    #对于"I love u"这样有简写单词的强烈正向感情的句子还是不能正确处理，分词没办法正确将简写单词"u"
    #还原成原有单词"you",这导致后面对词性词义的分析都是错误的!
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

    #此处应有 打分

    #遍历lemmas列表，将其中的所有形容词和副词做情感词进行分析，之后将分析结果
    #组成列表[句子ID,还原后的词形,词性,pos_score,neg_score,obj_score],
    #再将这个列表加入senti_words列表
    def senti(self,cleanwords):
        senti_words = []
        for lemma in cleanwords:
            if(lemma[2] == wn.ADJ) or (lemma[2] == wn.ADV):
            #if(lemma[2] == wn.ADJ):
                SentiSynsets = swn.senti_synsets(lemma[1], lemma[2])
                SentiSynset_list = list(SentiSynsets)
                if(len(SentiSynset_list) > 0):
                    for SentiSynset in SentiSynset_list:
                        #[句子ID,还原后的词形,词性,pos_score,neg_score,obj_score]
                        senti_words.append([lemma[0], lemma[1],lemma[2],SentiSynset.pos_score(),SentiSynset.neg_score(),SentiSynset.obj_score()])

        return senti_words

    #def senti_uni_method(self,cleanwords):

class operate:
    
    def _main_(self,data):   #连接数据库后的清洗过程整合                                                  
        
        #print(data)
        prep = prepare()
        sents = prep.sentoken(data)  #分句
        print(sents)
        print('\n')
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
        print(word_and_NER_tagss)
        print('\n')
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
op = operate()
i=1
cleanreview = []
Percentage = 0
#total = 21000
total = 21
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

sql.sqlQuit()
print('100%,成功扫描情感词并存入数据库')
print('------------------------------')



print('从数据库中提取CommentID段评论每一句话的多个情感词并计算其得分')
sql = usesql()  #先连接数据库，以免循环时重复连接
op = operate()

#创建等比数列 2^0,2^1,2^2,2^3 .. 2^99共100个，应该够用了吧
pro_series = numpy.logspace(0,99,100,base=2)

for CommentID in range(1,21,1):  #数据库中的评论ID，数据库中一共有21000条评论,这里只分析前面的21条
#for CommentID in range(3,4,1):
    print('------------------------------')
    print("开始分析第[%d]条评论"%(CommentID))
    data = sql.getdata(CommentID)
    print(data)

    #data = "People say you can't beat Surf N' Turf.It's 5.30 o'clock.gooooooood place!That is good?I looooooove u very much! I am very excited i.e. about the next generation of Apple products."
    senti_words = op._main_(data)
    print(senti_words)

    words_score = []
    SentenceIDs = sql.getSentenceIDs(CommentID)
    for SentenceID in SentenceIDs:
        #通过CommentID=M和SentenceID=N，得到第M条评论的第N个句子的所有情感词(形容词和副词)
        SentiWords = sql.getSentiWords(CommentID,SentenceID)
        if(SentiWords): #如果得到的情感词列表不是空的，那么就开始对这些情感词做评分计算
            wordID = 0
            Weights = 0
            score = 0
            CurrentSentiWord = SentiWords[0][0]
            print('------------------------------')
            print("开始计算  [%s]"%(CurrentSentiWord))
            for loopNum in range(0,len(SentiWords),1):
                if(CurrentSentiWord == SentiWords[loopNum][0]):
                    print("%.8f = (%.8f - %.8f) * (1 / %.8f)"%((SentiWords[loopNum][1] - SentiWords[loopNum][2]) * (1/pro_series[Weights]),SentiWords[loopNum][1],SentiWords[loopNum][2],pro_series[Weights]))
                    score = score + (SentiWords[loopNum][1] - SentiWords[loopNum][2]) * (1/pro_series[Weights])
                    print("第%d次求和结果%.8f"%(Weights,score))
                    if(Weights < 100):
                        Weights = Weights + 1
                else:
                    words_score.append([CommentID,SentenceID,wordID,CurrentSentiWord,score])
                    print("%s -- score:[%.8f]"%(CurrentSentiWord,score))
                    print('------------------------------')
                    CurrentSentiWord = SentiWords[loopNum][0]
                    wordID = wordID + 1
                    Weights = 0
                    score = 0
                    print('------------------------------')
                    print("开始计算  [%s]"%(CurrentSentiWord))
            words_score.append([CommentID,SentenceID,wordID,CurrentSentiWord,score])
            print("%s -- score:[%.8f]"%(CurrentSentiWord,score))
            print('------------------------------')   


    print('------------------------------')
    print("整理第%s段评论的情感词结果"%(CommentID))
    for word_score in words_score:
        print("第%s段评论，第%s个句子中的第%s个情感词%s，得分%s"%(word_score[0],word_score[1],word_score[2],word_score[3],word_score[4]))
    print('------------------------------')

sql.sqlQuit()








