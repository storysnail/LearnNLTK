#coding=utf8
import sys
import nltk.tokenize as token
import jieba
import re
from gensim import corpora
from gensim.similarities import Similarity
'''
    在信息检索中，BOW(Bag-of-words)模型假定对于一个文档，忽略它的单词顺序和语法、
    句法等要素，将其仅仅看作是若干个词汇的集合，文档中每个单词的出现都是独立的，
    不依赖于其它单词是否出现。也就是说，文档中任意一个位置出现的任何单词，都不受
    该文档语意影响而独立选择的。
'''
class Bow_CosSim(object):
    def __init__(self,text1,text2):
        self.text1 = text1
        self.text2 = text2
        self.is_chinese = False

    def is_Chinese(self,text):
        for ch in text:
            if '\u4e00' <= ch <= '\u9fff':
                self.is_chinese = True
                return True
        return False

    def CosSim(self,stopList = ''):
        if(self.is_Chinese(self.text1) != self.is_Chinese(self.text2)):
            return False

        #处理英文文本
        if(self.is_chinese == False):
            #print(self.text1,self.text2)
            
            #将文本1和文本2都拆分成句子,
            #text1中的所有句子放在sents1 list中
            #text2中的所有句子放在sents2 list中
            sents1 = token.sent_tokenize(self.text1)
            sents2 = token.sent_tokenize(self.text2)
            print(sents1)
            print(sents2)
            print('==========================================')

            #把text1的所有句子拆分成单词list
            words1 = [word.lower() for sent in sents1 for word in token.word_tokenize(sent) if word.lower() not in stopList]
            print(words1)
            print('==========================================')

            #把text2的所有句子拆分成单词list
            words2 = [word.lower() for sent in sents2 for word in token.word_tokenize(sent) if word.lower() not in stopList]
            print(words2)
            print('==========================================')


        #处理中文文本
        else:
            #print(self.text1,self.text2)
            
            #sents1 = re.split('(。|！|\!|\.|？|\?)',self.text1)  #保留分割符号
            sents1 = re.split('。|！|\!|\.|？|\?',self.text1)     #不保留分割符号
            sents2 = re.split('。|！|\!|\.|？|\?',self.text2)
            print(sents1)
            print(sents2)
            print('==========================================')

            #把text1的所有句子拆分成单词list
            words1 = [word for sent in sents1 for word in jieba.lcut(sent, cut_all=False) if word not in stopList]
            print(words1)
            print('==========================================')

            #把text2的所有句子拆分成单词list
            words2 = [word for sent in sents2 for word in jieba.lcut(sent, cut_all=False) if word not in stopList]
            print(words2)
            print('==========================================')


        #把两个word list放在一起，从中抽取一个“词袋（bag-of-words)"，为token映射id
        words = [words1,words2]
        dictionary = corpora.Dictionary(words)
        print(dictionary.token2id,dictionary.dfs)#显示token映射id和词频
        print('==========================================')

        #转换为用id表示的文档向量
        corpus = [dictionary.doc2bow(words_id) for words_id in words]
        print(corpus)
        print('==========================================')

        similarity = Similarity('-Similarity-index', corpus, num_features=len(dictionary))
        print(similarity)
        print('==========================================')

        test_corpus_1 = dictionary.doc2bow(words1)
        test_corpus_2 = dictionary.doc2bow(words2)
        cosine_sim1 = similarity[test_corpus_1][1]
        cosine_sim2 = similarity[test_corpus_2][0]
        print("利用gensim计算得到两段文本的相似度： %.4f  |  %.4f。"%(cosine_sim1,cosine_sim2))













