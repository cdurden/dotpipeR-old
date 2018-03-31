setGeneric(name="eval.Pipeline",def=function(pipeline, nodes=get_nodes(pipeline), run.preprocessor=TRUE, recurse=FALSE, envir=environment(), ...) standardGeneric("eval.Pipeline"))

setGeneric(name="addNode",def=function(node, pipeline, attrs) standardGeneric("addNode"))
setGeneric(name="addEdge",def=function(from, to, pipeline, attrs) standardGeneric("addEdge"))
