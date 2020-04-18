#coding=utf8
import pymysql
import pandas as pd
import nltk
import string
import re
import sys
import numpy
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer
from nltk.corpus import sentiwordnet as swn
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
'''
    从输入的句子中找到感情词，并计算该感情词的情感值
'''
class SentiWord(object):
    def __init__(self,data):
        self.data = data
        #print(self.data)
        
        self.SW_sents_token()  #self.sents = ['sent1','sent2',sent3']
        #print(self.sents)
        
        self.SW_sents_clean()  #self.cleansents = ['cleansent1','cleansent2',cleansent3']
        #print(self.cleansents)
        
        self.SW_wordss_token() #self.wordss = [['cleansent1_word1','cleansent1_word2','cleansent1_word3'],
                            #                 ['cleansent2_word1','cleansent2_word2','cleansent2_word3'],
                            #                 ['cleansent3_word1','cleansent3_word2','cleansent3_word3']]
        #print(self.wordss)
        
        self.SW_wordss_tag()  #self.wordss_tag = [[('cleansent1_word1','pos'),('cleansent1_word2','pos')],
                            #                    [('cleansent2_word1','pos')],
                            #                    [('cleansent3_word1','pos'),('cleansent3_word2','pos')]]
        #print(self.wordss_tag)
        
        self.SW_wordss_NER_tag() #self.wordss_NER_tag struct same with self.wordss_tag
        #print(self.wordss_NER_tag)

        self.SW_words_get_pos() #self.words_pos = [[sent_id,'word','pos'],
                                #                   [sent_id,'word','pos']]
        #print(self.words_pos)

        self.SW_words_stem()   #self.words_stem = [[sent_id,'word_stem','pos'],
                                #                   [sent_id,'word_stem','pos']]
        #print(self.words_stem)


        
    #分句
    def SW_sents_token(self):   
        #token = nltk.data.load('tokenizers/punkt/english.pickle')
        #sents = token.tokenize(str(self.data))
        text = re.sub('\n', ' ', str(self.data)) #将data里的换行符替换成空格
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
        self.sents = [sent.strip() for sent in sents]

    #去除标点等无用的符号
    def SW_sents_clean(self):    
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
        patterns = [(re.compile(regex), repl) for (regex, repl) in replacement_patterns] #这里用re.compile(regex)置换了 regex,具体作用是把regex给编译了
        for sent in self.sents:
            for (pattern, repl) in patterns:
                (tmpsent, n) = re.subn(pattern, repl, sent)  # re.subn('正则表达式（pattern）','替换的字符','待替换的字符串') 返回替换后的字符串及替换的次数
            tmpsents.append(tmpsent)
   
        delEStr = string.punctuation + string.digits     #再去除ASCII标点符号
        DelEDict = {}
        for char in delEStr:
            DelEDict[char] = '' # char是key, 令key对应的value都为空
        trans = str.maketrans(DelEDict) # 这里是在建立翻译表trans，str.maketrans(DelEDict) == str.maketrans(key,value) == str.maketrans(char, '')

        self.cleansents = []
        for tmpsent in tmpsents:
            cleansent = tmpsent.translate(trans) #利用翻译表trans去掉ASCII标点符号
            self.cleansents.append(cleansent)
        #print(self.cleansents)

    def SW_repeat_replace(self, word):  #通过递归调用处理重复字母的单词,例如"gooooooood"会被还原成"good"
        # \w 匹配非特殊字符(单词字符)，即字母，数字及下划线，* 指匹配前面的子表达式零次或多次。例如，zo* 能匹配 "z" 以及 "zoo"。
        repeat_reg = re.compile(r'(\w*)(\w)\2(\w*)') #关键就是这两行，感觉没看懂
        repl = r'\1\2\3'
        if wn.synsets(word):  # 判断当前字符串是否是单词
            return word
        repl_word = repeat_reg.sub(repl, word)
        if repl_word != word:
            return self.SW_repeat_replace(repl_word)
        else:
            return repl_word

    #分词      
    #对于"I love u"这样有简写单词的强烈正向感情的句子还是不能正确处理，分词没办法正确将简写单词"u"还原成原有单词"you",这导致后面对词性词义的分析是错误的
    def SW_wordss_token(self):
        # \w 匹配非特殊字符(单词字符)，即字母，数字及下划线，* 指匹配前面的子表达式零次或多次。
        #()表示分组，(\w*)是第一分组，(\w)是第二分组，\2表示引用第二分组，(\w*)是第三分组
        #例如:gooogleabcd被匹配后(\w*)对应g,(\w)对应o,\2表示引用第二分组的值o,(\w*)第三分组对应ogleabcd
        #所以这一次会在gooogleabcd字符串中尝试匹配gooogle字符串，如果匹配到，
        #则按照repl规则把第一分组、第二分组、第三分组的内容保存成一个新字符串googleabcd
        #如果字符串不是一个有效字符，程序还会尝试递归调用repeat_replace去不断的去除重复的字符。
        repeat_reg = re.compile(r'(\w*)(\w)\2(\w*)')
        repl = r'\1\2\3'
        self.wordss = []       
        for cleansent in self.cleansents: #取得一个句子
            New_words = []
            words = nltk.word_tokenize(cleansent) #对一个句子进行分词,得到这个句子中每个单词组成的列表
            for word in words:  #从单词列表中取得一个单词
                if wn.synsets(word): #如果这是一个有效单词则加入New_words列表
                    New_words.append(word)
                else: # 如果单词不是有效词汇,那么尝试清除其中的重复字母，看看能不能得到有效单词
                    New_words.append(self.SW_repeat_replace(word))    
            self.wordss.append(New_words)

    #标注词性
    def SW_wordss_tag(self): 
        self.wordss_tag = []
        for words in self.wordss: 
            self.wordss_tag.append(nltk.pos_tag(words))

    #命名实体
    def SW_wordss_NER_tag(self): 
        NERItems = []
        for words_tag in self.wordss_tag:
            NERItems.append(nltk.ne_chunk(words_tag))
            
        self.wordss_NER_tag = []
        for item in NERItems:
            words_and_NER_tag = [] #一个句子里所有单词(包括识别的命名实体)及其词性会保存在这个列表里
            for item_tree in item:
                if hasattr(item_tree, 'label'):
                    NERName = ' '.join(c[0] for c in item_tree.leaves())
                    NERType = item_tree.label()
                    words_and_NER_tag.append((NERName,NERType))
                else:
                    words_and_NER_tag.append(item_tree)
            self.wordss_NER_tag.append(words_and_NER_tag) 


    #通过tag获得pos
    def SW_words_get_pos(self):  
        sent_id = 1
        self.words_pos = []
        for words_NER_tag in self.wordss_NER_tag:    #此处的words_NER_tag是评论中的一个句子 is like [('bigger', 'JJR'),('best', 'JJR')]
            for word_NER_tag in words_NER_tag:  #此处的word_NER_tag是一个句子中的一个词 is like ('bigger', 'JJR')
                if word_NER_tag[1].startswith('J'):
                    pos = nltk.corpus.wordnet.ADJ
                elif word_NER_tag[1].startswith('V'):
                    pos = nltk.corpus.wordnet.VERB
                elif word_NER_tag[1].startswith('N'):
                    pos = nltk.corpus.wordnet.NOUN
                elif word_NER_tag[1].startswith('R'):
                    pos = nltk.corpus.wordnet.ADV        
                else:
                    pos = ''
                self.words_pos.append([sent_id,word_NER_tag[0],pos])#这里的结构多了一个句子的ID
            sent_id = sent_id+1
                

    #单词还原并且去除停用词
    def SW_words_stem(self):   
        lmtzr = WordNetLemmatizer()        # lemmatize()方法将word还原成pos词性的形式
        self.words_stem = []
        for word_pos in self.words_pos:
            if(len(word_pos[2]) < 1):
                lemmatized_word = lmtzr.lemmatize(word_pos[1],nltk.corpus.wordnet.NOUN)  
            else:
                lemmatized_word = lmtzr.lemmatize(word_pos[1],word_pos[2])  # word_pos = [word_tag[0],pos]

            if lemmatized_word not in stopwords.words('english'):
                self.words_stem.append([word_pos[0],lemmatized_word,word_pos[2]]) 


    #遍历lemmas列表，将其中的所有形容词和副词做情感词进行分析，之后将分析结果
    #组成列表[句子ID,还原后的词形,词性,pos_score,neg_score,obj_score],
    #再将这个列表加入words_senti列表
    def SW_Get_words_senti_score(self):
        words_senti = []
        for lemma in self.words_stem:
            if(lemma[2] == wn.ADJ) or (lemma[2] == wn.ADV) or (lemma[2] == wn.VERB):
                SentiSynsets = swn.senti_synsets(lemma[1], lemma[2])
                SentiSynset_list = list(SentiSynsets)
                if(len(SentiSynset_list) > 0):
                    for SentiSynset in SentiSynset_list:
                        #[句子ID,还原后的词形,词性,pos_score,neg_score,obj_score]
                        words_senti.append([lemma[0], lemma[1],lemma[2],SentiSynset.pos_score(),SentiSynset.neg_score(),SentiSynset.obj_score()])

        return words_senti
    
