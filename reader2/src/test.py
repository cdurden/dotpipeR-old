import pydotreader

g = pydotreader.load_networkx_digraph_from_dot("ex1.dot")
#g = pydotreader.load_graphviz_digraph_from_dot("ex1.dot")
#node_attrs = [d for n,d in g.node.items()]
#print(node_attrs)
#print(type(g))
#print(g)

def set_node_attr(g, node, key, value):
    attrs = {key: value}
    g.add_node(node, **attrs)
    return(g)

def convert_networkx_digraph_to_graphviz_digraph(g):
    from graphviz import Digraph
    graph = Digraph()
    for node in g.nodes_iter(data=True):
        attrs = node[1]
        graph.node(node[0],**attrs)

    for edge in g.edges_iter(data=True):
        graph.edge(edge[0],edge[1],**(edge[2]))
    return(graph)

for node in g.nodes_iter(data=False):
    g = set_node_attr(g, node, 'href', 'javascript:void();')
graphviz_digraph = convert_networkx_digraph_to_graphviz_digraph(g)
with open('out.svg', 'w') as f:
    f.write(graphviz_digraph._repr_svg_())
#g.render('out.svg',format='svg')

#import networkx as nx

#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
#plt.figure(1,figsize=(8,8))
## layout graphs with positions using graphviz neato
#pos=nx.drawing.nx_agraph.graphviz_layout(g,prog="neato")
#nx.draw(g,
#     pos=pos,
#     node_size=40,
#     vmin=0.0,
#     vmax=1.0,
#     with_labels=False
#     )
#plt.savefig("out.svg")
