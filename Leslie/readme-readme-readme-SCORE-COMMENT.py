#这是一个python2的脚本，让我们来看看这个脚本究竟是做什么的！


#division(精确除法)，当没有导入该功能时，"/"操作符执行的是截断除法(Truncating Division)
from __future__ import division

#SentiWordNet类
class SentiWordNet():
    def __init__(self,netpath):
        self.netpath = netpath  #对应这个文件"C:\\Users\\Administrator\\Desktop\\SentiWordNet.txt"
        self.dictionary = {}    #初始化了一个字典类型的成员变量，用来存放什么呢？
    
    def infoextract(self):
        #初始化了一个字典，名字描述是临时的字典变量
        #从后面的代码得知，其key是"单词#词性"字符串,
        #其value是个list,[sensenumber,正面积极的情感 - 负面情感]
        tempdict = {}  
        templist = []  #初始化了一个列表，名字描述也是临时的列表变量
        
        try:
            #以只读的方式打开了"C:\\Users\\Administrator\\Desktop\\SentiWordNet.txt"文件
            #话说你用完可没关闭这个文件描述符啊！
            f = open(self.netpath,"r")
        except IOError:
            print ("failed to open file!")
            exit()
        print ('start extracting.......')

    # "C:\\Users\\Administrator\\Desktop\\SentiWordNet.txt"文件的数据格式
    # Example line:  示例行
    #猜猜各个分段是什么意思！！！
    # POS  -- 词性
    # ID   --标识
    # PosS -- 正面积极的情感  positive sentiment 是单精度数字
    # NegS -- 负面情感  negative sentiment       是单精度数字
    # SynsetTerm#sensenumber   这个是什么？可能是同义词集,sensenumber不清楚,只知道每个词集用空格分割
    # Desc  描述?
    # POS     ID     PosS  NegS SynsetTerm#sensenumber Desc
    # a   00009618  0.5    0.25  spartan#4 austere#3 ascetical#2  ……
    #POS(TAB)ID(TAB)PosS(TAB)NegS(TAB)SynsetTerm1#sensenumber1(空格)SynsetTerm1#sensenumber1(TAB)Desc

        for sor in f.readlines(): #从文件读一行
            if sor.strip().startswith("#"): #去除字符串sor的首尾空格，之后看看是否以#字符开头
                pass  #如果以#字符开头 pass 继续循环读下一行
            else:
                #以横向制表符对sor字符串进行切片,结果保存在data字符串列表中
                #应该有6列 (词性、标识、正面积极的情感、负面情感、同义词集、描述)
                data = sor.split("\t")
                if len(data) != 6:
                    print ('invalid data')
                    break

                #wordTypeMarker保存得到的单词词性
                wordTypeMarker = data[0]

                #data[1]是标识

                #得分，用正面积极的情感 - 负面情感  有正负喽
                synsetScore = float(data[2]) - float(data[3])   #// Calculate synset score as score = PosS - NegS

                #不同的同义词集用空格分割
                synTermsSplit = data[4].split(" ")    # word#sentimentscore
                
                for w in synTermsSplit:
                    #分开SynsetTermhe和sensenumber
                    synTermAndRank = w.split("#")
                    #synTerm = 单词#词性
                    synTerm = synTermAndRank[0] + "#" + wordTypeMarker    #单词#词性
                    synTermRank = int(synTermAndRank[1])  #取得sensenumber

                    #"单词#词性"字符串作为字典的key,检查这个key是否存在
                    if（tempdict.has_key(synTerm)）:
                        t = [synTermRank,synsetScore]
                        tempdict.get(synTerm).append(t)#如果key存在则在list末尾添加新的[synTermRank,synsetScore]        
                    else:
                        #如果不存在key,则新建一个字典，之后把这个新建的字典加入tempdict字典
                        temp = {synTerm:[]}
                        t = [synTermRank,synsetScore]
                        temp.get(synTerm).append(t)
                        tempdict.update(temp)            

                #开始遍历整个tempdict字典
                for key in tempdict.keys():
                    score = 0.0
                    ssum = 0.0
                    #通过key得到字典的value,然后进行了一些计算
                    for wordlist in tempdict.get(key):
                        score += wordlist[1]/wordlist[0] #(正面积极的情感 - 负面情感)/sensenumber
                        ssum += 1.0/wordlist[0]   #1.0/sensenumber
                        score /= ssum  # score = score/ssum
                        #把结果保存在self.dictionary字典类型的成员变量中
                        #key是"单词#词性"字符串,value是score
                        self.dictionary.update({key:score})
    
    def getscore(self,word,pos):
        #从self.dictionary字典类型的成员变量中得到score
        return self.dictionary.get(word + "#" + pos)
        
            
            
                
if __name__ == '__main__':
    #实例化SentiWordNet类
    netpath = "C:\\Users\\Administrator\\Desktop\\SentiWordNet.txt"
    swn= SentiWordNet(netpath)
    #提取信息，从SentiWordNet.txt提取什么信息呢？我们去SentiWordNet类里看看infoextract()成员函数
    swn.infoextract() 
    print "good#a "+str(swn.getscore('good','a'))
    print "bad#a "+str(swn.getscore('bad','a'))
    print "blue#a "+str(swn.getscore('blue','a'))
    print "blue#a "+str(swn.getscore('blue','n'))
    #这个脚本不是你想要的sentiwordnet，明天（3月1日）我开始做sentiwordnet



    
