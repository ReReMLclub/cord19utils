import numpy as np
from collections import defaultdict
import networkx as nx
from networkx.algorithms.community import asyn_fluidc

class NodeCounter:
    def __init__(self, initialCount = 0):
        self.count = initialCount
    def get(self):
        cur = self.count
        self.count += 1
        yield cur
        
class GraphBuilder:
    
    def __init__(self, reader):
        self.reader = reader
        
    def clampWeight(self, w, bound):
        if bound < 0 or w < bound:
            return w
        else:
            return bound
        
    def keepEdge(self, graph, n0, n1, citeOutCutoff, citeInCutoff):
        keep0 = graph.nodes()[n0]['citeOut'] > citeOutCutoff or graph.nodes()[n0]['citeIn'] > citeInCutoff
        keep1 = graph.nodes()[n1]['citeOut'] > citeOutCutoff or graph.nodes()[n1]['citeIn'] > citeInCutoff
        return keep0 and keep1
        
    def buildGraph(self, citeOutCutoff = 0, citeInCutoff = 0, weightBound = -1):
        self.nodeCounter = NodeCounter()
        self.ref2ID = {}
        graph = nx.DiGraph()
        for article in self.reader.iterateArticles():
            titleNodeID = next(self.nodeCounter.get())
            bib = article.bib
            ref_ids = bib.keys()
            graph.add_node(titleNodeID, title = article.title, citeOut = len(ref_ids), citeIn = 0, source = 'corpus', text = article.mainText)
            for ref_id in ref_ids:
                refTitle = bib[ref_id]['title']
                refCount = bib[ref_id]['count']
                if refTitle in self.ref2ID.keys():
                    refNodeID = self.ref2ID[refTitle]
                    graph.nodes[refNodeID]['citeIn'] += 1
                else:
                    self.ref2ID[refTitle] = next(self.nodeCounter.get())
                    refNodeID = self.ref2ID[refTitle]
                    graph.add_node(refNodeID, title = refTitle, citeOut = 0, citeIn = 1, source = 'external', text = refTitle)
                    
                graph.add_edge(titleNodeID, self.ref2ID[refTitle], weight = self.clampWeight(refCount, weightBound))
                    
        return self.pruneGraph(graph, citeOutCutoff, citeInCutoff)
    
    def pruneGraph(self, graph, citeOutCutoff, citeInCutoff):
        edgesToPrune = []
        nodesToPrune = []
        
        for n0, n1 in graph.edges:
            if not self.keepEdge(graph, n0, n1, citeOutCutoff, citeInCutoff):
                edgesToPrune.append((n0, n1))
        
        graph.remove_edges_from(edgesToPrune)
        
        for n in graph.nodes:
            if graph.degree(n) == 0:
                nodesToPrune.append(n)
                
        graph.remove_nodes_from(nodesToPrune)

        return graph
    
    def assignCommunities(self, graph, nCommunities = 20, max_iter = 20):
        gSize = graph.number_of_nodes()
        connectedComponents = nx.connected_components(nx.Graph(graph))
        subgraphs = [nx.Graph(graph).subgraph(cc) for cc in connectedComponents]
        communities = []
        for subgraph in subgraphs:
            sgSize = subgraph.number_of_nodes()
            if sgSize >= gSize*0.01:
                communities.extend(list(asyn_fluidc(nx.Graph(graph).subgraph(subgraph), k = int((sgSize/gSize)*nCommunities), max_iter = max_iter)))
        
        return communities
    
    def buildSupergraph(self, graph, communities, weightCutoff = -1):
        sgraph = nx.DiGraph()
        node2com = {n : i for (i, community) in enumerate(communities) for n in list(community)}
        weightedEdges = defaultdict(int)
        
        for i, community in enumerate(communities):
            sgraph.add_node(i)
        
        for i0, community in enumerate(communities):
            for n0 in community:
                for n1 in graph.successors(n0):
                    i1 = node2com[n1]
                    if i0 != i1:
                        weightedEdges[(i0, i1)] += 1
        
        for (i0, i1), weight in weightedEdges.items():
            if weight > weightCutoff and weightCutoff > 0: 
                sgraph.add_edge(i0, i1, weight = weight)
            
        return sgraph
    
