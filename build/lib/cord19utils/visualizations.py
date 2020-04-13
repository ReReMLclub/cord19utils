import networkx as nx
import holoviews as hv
import pandas as pd
from holoviews import opts, dim
hv.extension('bokeh')

def drawChordGraph(sgraph, id2label, nodeOfInterest = False):
    nodeData = {
        'id' : [],
        'name' : []
    }

    edgeData = {
        'source' : [],
        'target' : [],
        'value' : []
    }
    
    if nodeOfInterest:
        nodesToKeep = [nodeOfInterest] + [node for node in sgraph.predecessors(nodeOfInterest)] + [node for node in sgraph.successors(nodeOfInterest)]
        sgraph = sgraph.subgraph(nodesToKeep)
        
    for edge in sgraph.edges():

    for node in sgraph.nodes():
        nodeData['id'].append(node)
        nodeData['name'].append(id2label[node])

    for source, target in sgraph.edges():
        value = sgraph.edges()[(source, target)]['weight']
        edgeData['source'].append(source)
        edgeData['target'].append(target)
        edgeData['value'].append(value)

    nodeDF = pd.DataFrame(nodeData)
    edgeDF = pd.DataFrame(edgeData)

    chord = hv.Chord((edgeDF, hv.Dataset(pd.DataFrame(nodeDF), 'id'))).select(value=(5, None))
    chord.opts(
        opts.Chord(cmap='Category20', edge_cmap='Category20', edge_color=dim('source').str(), 
                   labels='name', node_color=dim('id').str()))

    return chord