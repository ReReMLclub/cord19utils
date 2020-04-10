from collections import defaultdict
import networkx as nx
from networkx.algorithms.community import asyn_fluidc
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import nltk
nltk.download('wordnet')
from gensim import corpora, models

class TextProcessor:
    def __init__(self, graph):
        self.graph = graph
        self.customStopWords = ['virus', 'pmc', 'infect', 'coronavirus', 'respiratory', 'protein', 'disease', 'human', 'patient', 'cell']
        self.allowedWords = ['dna', 'rna', 'sar', 'mer', 'ace', 'orf', 'bat', 'cat', 'dog']
        
        self.stemmer = SnowballStemmer('english')
        self.destemmer = defaultdict(set)
    
    def addStopWords(self, words):
        self.customStopWords.extend(words)
        
    def addAllowedWords(self, words):
        self.allowedWords.extend(words)
        
    def lemmatize(self, text):
        return self.stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))
    
    def preprocess(self, text):
        result = []
        stopWords = STOPWORDS.union(set(self.customStopWords))
        for token in gensim.utils.simple_preprocess(text):
            token_lemma = self.lemmatize(token)
            self.destemmer[token_lemma].add(token)
            if token not in stopWords and token_lemma not in stopWords and (len(token) > 3 or token in self.allowedWords):
                result.append(token_lemma)
        return result
    
    def buildDictionary(self):
        documents = [self.preprocess(self.graph.nodes()[node]['text']) for node in self.graph.nodes()]
        self.dictionary = gensim.corpora.Dictionary(documents)
        self.dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
        
    def extractTopics(self, community, num_topics = 3):
        documents = [self.preprocess(self.graph.nodes()[node]['text']) for node in community]
        bag = [self.dictionary.doc2bow(doc) for doc in documents]
        tfidf = models.TfidfModel(bag)
        com_tfidf = tfidf[bag]
        lda_model_tfidf = gensim.models.LdaMulticore(com_tfidf, num_topics = num_topics, id2word=self.dictionary, passes=2, workers=4)
        
        topics = [t[1] for t in lda_model_tfidf.show_topics()]
        topicWords = [[sorted(list(self.destemmer[w.replace('"', '')]), key = lambda w: len(w))[0] for w in re.findall(r'\"[a-z0-9]*\"', aTopic)] for aTopic in topics]
        
        return topicWords
    
    def assignCommunityTopics(self, communities, verbose = False):
        self.id2label = defaultdict(str)
        for (cid, nodes) in enumerate(communities):
            topics = self.extractTopics(nodes)
            label = '\n'.join([f"{t+1}: {','.join(words[:3])}" for t, words in enumerate(topics)])
            self.id2label[cid] = label
            if verbose:
                print(f'======community {cid}======')
                print(label)