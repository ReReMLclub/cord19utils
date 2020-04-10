import numpy as np 
import pandas as pd 
import glob
import json
from collections import defaultdict

class Article:
    def __init__(self, file_path, id2title):
        self.problemTitleWords = ['pubmed', 'springer nature']
        self.problemTitles = ['world health organization', "publisher's note"]
        with open(file_path) as file:
            content = json.load(file)
            self.paper_id = content['paper_id']
            if id2title[self.paper_id]:
                self.title = id2title[self.paper_id]
            else:
                self.title = self.paper_id
            self.citations = []
            self.bib = self.filterBibEntries(content['bib_entries'])
            for ref_id in self.bib.keys():
                self.bib[ref_id]['count'] = 1
            for entry in content['body_text']:
                if len(entry['cite_spans']) > 0:
                    self.citations.extend(entry['cite_spans'])
            for citation in self.citations:
                ref_id = citation['ref_id']
                if ref_id in self.bib.keys():
                    self.bib[ref_id]['count'] += 1
            self.mainText = self.getMainText(content)
            
    def __repr__(self):
        return f'ID: {self.paper_id}\ttitle: {self.title}'
    
    def getMainText(self, content):
        mainText = ''
        if 'metadata' in content.keys() and 'title' in content['metadata'].keys() and content['metadata']['title']:
            mainText += content['metadata']['title']
            mainText += ' '
        if 'abstract' in content.keys() and content['abstract']:
            for entry in content['abstract']:
                mainText += entry['text']
                mainText += ' '

        return mainText
    
    def filterBibEntries(self, rawEntries):
        cleanEntries = {}
        for ref_id in rawEntries.keys():
            title = rawEntries[ref_id]['title'].lower()
            if title and title not in self.problemTitles and not any([w for w in self.problemTitleWords if w in title]):
                cleanEntries[ref_id] = rawEntries[ref_id]
        
        return cleanEntries
    
class CorpusReader:
    def __init__(self, filePaths, meta_df):
        self.filePaths = filePaths
        self.id2title = defaultdict(str)
        self.meta_df = meta_df
        for row in self.meta_df.itertuples():
            if not pd.isnull(row.sha):
                self.id2title[row.sha] = str(row.title)
                
    def iterateArticles(self):
        for path in self.filePaths:
            yield Article(path, self.id2title)
            
