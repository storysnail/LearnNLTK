#coding=utf8
import sys
import codecs
from nltk import pos_tag
import nltk.tokenize as token
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import jieba
import jieba.posseg as pseg
import re
from nltk.corpus import sentiwordnet as swn
'''
    从输入的句子中找到感情词，并计算该感情词的情感值
'''
class SentiWord(object):
    def __init__(self,text):
        self.text = text

    def is_Chinese(self,text):
        for ch in text:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    # 获取单词的词性
    def get_wordnet_pos(self,tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return None
    
    def SentiValue(self,stopList = ''):
        # 处理英文文本
        if(self.is_Chinese(self.text) == False):
            #print(self.text1,self.text2)
            
            # 将文本拆分成句子,
            #text中的所有句子放在sents list中
            sents = token.sent_tokenize(self.text)
            print(sents)
            print('==========================================')

            # 把text的所有句子拆分成单词list
            words = [word.lower() for sent in sents for word in token.word_tokenize(sent) if word.lower() not in stopList]
            print(words)
            print('==========================================')

            # 标注词性
            taggeds = pos_tag(words)
            print(taggeds)
            print('==========================================')

            # 词形还原,并将还原后的词形和词性组成列表，再将这个列表加入lemmas列表
            wnl = WordNetLemmatizer()
            lemmas = []
            for tagged in taggeds:
                wnpos = self.get_wordnet_pos(tagged[1]) or wordnet.NOUN
                lemmas.append([wnl.lemmatize(tagged[0], pos=wnpos),wnpos]) 

            print(lemmas)

            #遍历lemmas列表，将其中的形容词做情感词进行分析，之后将分析结果
            #组成列表[还原后的词形,词性,pos_score,neg_score,obj_score]，
            #再将这个列表加入senti_words列表
            senti_words = []
            for lemma in lemmas:
                #if(lemma[1] == wordnet.ADJ) or (lemma[1] == wordnet.ADV):
                if(lemma[1] == wordnet.ADJ):
                    SentiSynsets = swn.senti_synsets(lemma[0], lemma[1])
                    SentiSynset_list = list(SentiSynsets)
                    if(len(SentiSynset_list) > 0):
                        for SentiSynset in SentiSynset_list:
                            senti_words.append([lemma[0], lemma[1],SentiSynset.pos_score(),SentiSynset.neg_score(),SentiSynset.obj_score()])

            print(senti_words)
            return senti_words
            
        #处理中文文本
        else:
            #sents = re.split('(。|！|\!|\.|？|\?)',self.text)  #保留分割符号
            sents = re.split('。|！|\!|\.|？|\?',self.text)     #不保留分割符号
            print(sents)
            print('==========================================')

            #把text的所有句子拆分成单词list
            #words = [word for sent in sents for word in jieba.lcut(sent, cut_all=False) if word not in stopList and word != ' ' and word != '' and word != "\n"]
            words = [word for sent in sents for word in pseg.cut(sent) if word not in stopList and word != ' ' and word != '' and word != "\n"]
            print(words)
            print('==========================================')

            # 标注词性并将其中的名词、动词、形容词、副词提取出来
            lemmas = []
            for word, flag in words:
                #print('%s %s' % (word, flag))
                if(flag == 'a') or (flag == 'ad') or (flag == 'an') or (flag == 'ns') or (flag == 'n'):
                    if(lemmas.count([word,flag]) == 0):
                        lemmas.append([word,flag])
            print('==========================================')
            print(lemmas)
            print('==========================================')
            
            #读取中文senti_synset数据文件
            #这个数据文件实际上是把中文映射到对应的英文单词上面了
            senti_words = []
            known_cn = self.load_Chinese_Open_WordNet()
            for lemma in lemmas:
                Synset_list = self.fetch_Chinese_Open_WordNet(known_cn,lemma[0])
                for Synset_node in Synset_list:
                    SentiSynset = swn.senti_synset(Synset_node.name())
                    senti_words.append([lemma[0],SentiSynset.pos_score(),SentiSynset.neg_score(),SentiSynset.obj_score()])

            print(senti_words)
            return senti_words
                
    def fetch_Chinese_Open_WordNet(self,known_cn,word):
        fetch_list = []
        for kn in known_cn:
            if (kn[1] == word):
                if(len(kn[0]) != 0):
                    #用POS和offset序号来查询，返回一个synset,例如 'n',4543158
                    fetch_list.append(wordnet._synset_from_pos_and_offset(str(kn[0][-1:]), int(kn[0][:8])))
                    #print(str(kn[0][-1:]), int(kn[0][:8]))

        return fetch_list

    #读取中文的Wordnet文件
    def load_Chinese_Open_WordNet(self):
        file = codecs.open("./data/cow-not-full.txt", "rb", "utf-8")

        known_cn = set()
        for line in file:
            #去除首尾空格之后如果第一个字符是#，跳过该行继续读取下一行
            if line.startswith('#') or not line.strip():
                continue
            #用TAB对行分段
            col = line.strip().split("\t")
            if len(col) == 3:
                (synset, lemma, status) = col
            elif len(col) == 2: 
                (synset, lemma) = col 
                status = 'Y'
            else:
                print ("illformed line: ", line.strip())
                
            if status in ['Y', 'O' ]:
                if not (synset.strip(), lemma.strip()) in known_cn:
                    known_cn.add((synset.strip(), lemma.strip()))

        return known_cn











