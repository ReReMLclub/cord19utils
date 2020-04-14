# cord19utils
This package contains the function and class definitions for the Kaggle notebook found here: https://www.kaggle.com/lbvigilantdata/a-citation-network-model-for-topic-discovery.


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

where `graph` is a networkx `DiGraph` type created by the `builder.buildGraph` method, and `nCommunities` is the desired number of communities to find.  This method returns a list of sets of nodeIDs, with each set representing a community.  After assigning communities, a supergraph.
