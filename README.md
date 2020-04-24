# cord19utils
This package contains the function and class definitions for the Kaggle notebook found here: https://www.kaggle.com/reremlclub/a-citation-network-model-for-topic-discovery.


## CorpusReader
This object is used to iterate through the articles in the corpus.  It is initialized with the following:

`reader = cord19utils.CorpusReader(filePaths, meta_df)`

Here, `filePaths` is a list of json file names and `meta_df` is a Pandas DataFrame originating from the competition metadata csv file.

## GraphBuilder
This object constructs the graph representing the citation network and provides some additional processing functions.  It is intiallized by: 

`builder = cord19utils.GraphBuilder(reader)`

where `reader` is CorpusReader object.  After initializing, a graph is generated with:

`graph = builder.buildGraph(citeOutCutoff, citeInCutoff, weightBound)`

The parameters are:
* `citeOutCutoff`:  An integer representing the minimum outgoing citations a corpus document must have to be included in the graph.
* `citeInCutoff`:  An integer representing the minimum incoming citations an external article must have to be included in the graph.
* `weightBound`:  An integer representing the maximum edge weight from a corpus document to an external article.  The edge weight is equal to the number of times a corpus document cites an external article in its abstract or body text sections.

The `buildGraph` method resturns a `DiGraph` object from the [networkx](https://networkx.github.io/) library.

Once a graph has been built, communities can be assigned with

`communities = builder.assignCommunities(graph, nCommunities)`

where `graph` is a networkx `DiGraph` type created by the `builder.buildGraph` method, and `nCommunities` is the desired number of communities to find.  This method returns a list of sets of nodeIDs, with each set representing a community.  After assigning communities, a "graph of graphs" or supergraph can be created using

`sgraph = builder.buildSupergraph(graph, communities, weightCutOff)`

where the return value `sgraph` is again a networkx `DiGraph`.  The `weightCutOff` parameter specifies a minimum weight for an edge to be included in the supergraph, where the weight of an edge between communities is defined by the number of citations from documents in one community to documents in another.  

## TextProcessor
This object is used to assign short, meaningful topics to each community of documents using Latent Dirichlet Allocation.  It is initialized with:

`proc = cord19utils.TextProcessor(graph)`

where graph is the `DiGraph` representing the citation network.  After initializing, a dictionary of words found in the titles and abstracts of the nodes in `graph` can be built using

`proc.buildDictionary()`

Finally, community topics can then be assigned using 

`proc.assignCommunityTopics(communities, verbose)`

where `communities` is the list of node sets produced by `builder.assignCommunities(graph, nCommunities`).  The `verbose` parameter is a boolean value, if set to `True` the topics will be printed to screen as the method runs.  After it completes, the topics assigned to each community can be accessed via the `proc.id2label` object, which is a dict of node ID to topic.

## Visualizations
With topics assigned to communities, a chord graph illustrating the relationshis between communities can be drawn with

`cord19utils.drawChordGraph(sgraph, proc.id2label)`

Optionally, the argument `nodeOfInterest` can be provided with an integer community ID, which will restrict the resulting chord graph to just the specified community and it's neighbors in `sgraph`.
