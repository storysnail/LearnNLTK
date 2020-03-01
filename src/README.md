# LearnNLTK

</br>
2020-03-01</br>
&emsp; 用WordNet实现中文、英文文本的情感分析</br>
下面的模型训练需要花时间研究研究资料了。
</br>
2020-02-29</br>
&emsp; 开始尝试用NLTK分词，但nltk_data下只有netword,翻墙下载了638MB的nltk_data.zip,解压后将里面的packages</br>
文件夹下的所有文件拷贝到nltk_data目录下，以为这样就可以了，运行程序却提示下面的错误：</br>
<pre>
  Resource [93mpunkt[0m not found.
  Please use the NLTK Downloader to obtain the resource:

  >>> import nltk
  >>> nltk.download('punkt')
  Attempted to load [tokenizers/punkt/PY3/english.pickle
 </pre>
 猪头了一个多小时，期间在网上各种搜索也没有解决方法！饭后灵光一现，提示的这么明白了还乱搜索，</br>
 把nltk_data/tokenizers/punkt.zip解压，问题解决。</br>
 </br>
 然后是需要用gensim，用清华的源会快很多：</br>
 pip3 install -i  https://pypi.tuna.tsinghua.edu.cn/simple/ gensim</br>
</br>
测试中文、英文的分句和分词，词袋(语料庫）、语料庫数字映射、各段文本的向量表，以及计算两段文本的余弦相似度.</br>
</br>
2020-02-28</br>
&emsp; 初步了解NLTK对英文的分词操作，安装jieba模块，阅读jieba中文分词手册，用jieba做了第一次中文分词尝试。</br>
从网上找到2个中文评论语料文件，加上原来的英文语料文件，放在了src/data文件夹下。这两个语料文件格式</br>
分别为.txt和.cvs，以后可以使用pandas来统一读取，现在暂时使用python的readline来处理。</br>
</br>
2020-02-27</br>
&emsp; mariadbOP.py文件实验pymysql模块，使用方式和C、PHP下使用数据库的类似。xlsxOP.py文件尝试读取Excel文件,</br>
简单实现对指定cell（行、列）里的数据的读取。 </br></br>