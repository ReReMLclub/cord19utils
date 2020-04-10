import networkx as nx
import holoviews as hv
from holoviews import opts, dim
hv.extension('bokeh')

def drawChordGraph(sgraph, id2label):
    nodeData = {
        'id' : [],
        'name' : []
    }

    edgeData = {
        'source' : [],
        'target' : [],
        'value' : []
    }

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

    chord = hv.Chord((edgeDF, hv.Dataset(pd.DataFrame(nodeDF), 'index'))).select(value=(5, None))
    chord.opts(
        opts.Chord(cmap='Category20', edge_cmap='Category20', edge_color=dim('source').str(), 
                   labels='name', node_color=dim('index').str()))

    return chord