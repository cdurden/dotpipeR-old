#    dotpipeR: R package for computational pipelines using the DOT grammar
#    Copyright (C) 2013  Christopher L Durden <cdurden@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

paste0 <- function(...) { paste(...,sep="") }

get_nodes <- nodes

parents <- function(pipeline,nodes) {
  parents = unlist(sapply(nodes,function(node) inEdges(node,pipeline)[[1]]))
  return(parents)
}

ancestors <- function(pipeline,nodes) {
  parents = unlist(sapply(nodes,function(node) inEdges(node,pipeline)[[1]]))
  if(length(parents)==0) {
    return(parents)
  } else {
    return(union(ancestors(pipeline,parents),parents))
  }
}

do.callInPipelineNode <- function(fn, nodeargs, pipeline, node, envir=parent.frame()) {
  pipeline@env[[node]] <- do.call(what=fn,args=nodeargs,quote=FALSE,envir=envir)
  return(pipeline[node])
}

do.evalInPipelineNode <- function(expr, nodeargs, pipeline, node, envir=parent.frame()) {
  if(length(nodeargs)==0) {
    tmpenv <- new.env(parent=envir)
  } else {
    tmpenv <- list2env(nodeargs,parent=envir)
  }
  pipeline@env[[node]] <- eval(expr,envir=tmpenv)
  return(pipeline[node])
}

# run the preprocessor lines as normal R code in the specified environment
preprocessor <- function(pipeline, envir=globalenv()) {
    expr=paste0(pipeline@preprocessor_lines, collapse='')
    eval(parse(text=expr),envir=envir)
}

# Return the function or expression object assocate to the node, or NULL if not found.
getNodeEvaluatorString <- function(pipeline, node, envir=parent.frame()) { 
  fn_name <- tryCatch({nodeData(pipeline,node,"function")[[node]]}, error=function(err) { return(NA) })
  if(!is.na(fn_name)) { # If a function name is found in the attributes list, remove surrounding quotes, and search for the function in the given environment.
    fn <- tryCatch({get(x=unquote(nodeData(pipeline,node,"function")[[node]]), mode="function", envir=envir)}, error=function(err) { stop("Function ",fn_name," not found when evaluating node ",node,": ",err) }) 
    return(fn_name)
  } else { # Otherwise, look for an expression attribute, remove the surrounding quotes and parse the expression.
    expr_text = tryCatch({unquote(nodeData(pipeline,node,"expression")[[node]])}, error=function(err) { stop("Missing evaluator for node ",node) })
    return(expr_text)
  }
}

# Return the function or expression object assocate to the node, or NULL if not found.
getNodeEvaluator <- function(pipeline, node, envir=parent.frame()) { 
  fn_name <- tryCatch({nodeData(pipeline,node,"function")[[node]]}, error=function(err) { return(NA) })
  if(!is.na(fn_name)) { # If a function name is found in the attributes list, remove surrounding quotes, and search for the function in the given environment.
    fn <- tryCatch({get(x=unquote(nodeData(pipeline,node,"function")[[node]]), mode="function", envir=envir)}, error=function(err) { stop("Function ",fn_name," not found when evaluating node ",node,": ",err) }) 
    return(fn)
  } else { # Otherwise, look for an expression attribute, remove the surrounding quotes and parse the expression.
    expr_text = tryCatch({unquote(nodeData(pipeline,node,"expression")[[node]])}, error=function(err) { stop("Missing evaluator for node ",node) })
    expr <- tryCatch({parse(text=expr_text)}, error=function(err) { stop("Error parsing expression for node ",node,": ",err) })
    return(expr)
  }
}

# Remove surrounding quotes from the node's attribute values and evaluate the expression in the given environment
parseArgAttrValue <- function(identifier,envir=parent.frame()) {
  if (grepl('^".*"$',identifier)) {
    identifier <- gsub('^"|"$','',identifier)
    identifier <- gsub('\\"','"',identifier,fixed=TRUE)
  }
  identifier
}

# Remove surrounding quotes from the node's attribute values and evaluate the expression in the given environment
processArgAttrValue <- function(identifier,envir=parent.frame()) {
  if (grepl('^".*"$',identifier)) {
    identifier <- gsub('^"|"$','',identifier)
    identifier <- gsub('\\"','"',identifier,fixed=TRUE)
  }
  eval(parse(text=identifier),envir=envir)
}

# Set the name of the argument defined by an edge to the "name" attribute in the edge statement attributes list
# If this attribute is not set, use the name of the parent node
edgeArgName <- function(parent,pipeline,node) {
  argName <- tryCatch(unquote(edgeData(pipeline,from=parent,to=node,attr="name")[[1]]),error=function(e) { return(NULL) })
  if(is.null(argName) || is.na(argName)) {
    # for arguments without names, set name to name of parent node
    argName <- parent
    # for arguments without names, set name to "" per R convention
    #argName <- ""
  }
  argName
}

cleanArgs<-function(argstr,fn,exclude.repeats=FALSE,exclude.other=NULL, # from plotrix package
 dots.ok=TRUE) {

 fnargs<-names(formals(fn))
 if(length(argstr) > 0 && !is.primitive(fn) && !("..." %in% fnargs && dots.ok)) {
  badargs<-names(argstr)[!sapply(names(argstr),"%in%",c(fnargs,""))]
  for(i in badargs) argstr[[i]]<-NULL
 }
 if(exclude.repeats) {
  ntab<-table(names(argstr))
  badargs<-names(ntab)[ntab > 1 & names(ntab) != ""]
  for (i in badargs) argstr[[i]]<-NULL
 }
 for(i in exclude.other) argstr[[i]]<-NULL
 argstr
}

# Generate an arguments list by combining the values of parent nodes with the values of the expressions in the node's attributes list.
# Also, set the names of the arguments appropriately.
genNodeArgsStrings <- function(pipeline,node,evaluator,envir=parent.frame()) { 
  parents <- inEdges(node,pipeline)[[node]]
  nodeargs <- as.list(parents)
  argnames <- lapply(parents,edgeArgName,pipeline,node)
  names(nodeargs) <- argnames

# create an environment for evaluating arguments given as node attributes 
# containing the arguments from parent nodes
  if(length(nodeargs)==0) {
    tmpenv <- new.env(parent=envir)
  } else {
    tmpenv <- list2env(nodeargs,parent=envir)
  }

  extra_argnames_ <- names(which(!is.na(nodeData(pipeline,node)[[node]])))
  if(is.function(evaluator)) {
    extra_argnames <- extra_argnames_[extra_argnames_ != "function"]
  } else {
    extra_argnames <- extra_argnames_[extra_argnames_ != "expression"]
  }
  extra_args <- lapply(extra_argnames, function(arg) { 
    val <- parseArgAttrValue(nodeData(pipeline,node,arg)[[node]],envir=tmpenv)
    return(val)
  }) 
  names(extra_args) <- extra_argnames
  args <- c(nodeargs, extra_args)

  # clean args to avoid error about extra arguments
  if(is.function(evaluator)) {
    args <- cleanArgs(args,evaluator)
  }

  which.named = vapply(names(args),function(x) {x!=""},FUN.VALUE=TRUE)
  if(length(which.named)>0) {
    # sort args by name, using R builtin sort function with LC_COLLATE set to 'C'
    locale = Sys.getlocale("LC_COLLATE")
    if(locale!='C') {
      Sys.setlocale("LC_COLLATE",'C')
    }
  
    # only sort args which have names
    args[which.named] = args[sort(names(args[which.named]))]
    names(args)[which.named] <- sort(names(args[which.named]))
    if(locale!='C') {
      Sys.setlocale("LC_COLLATE",locale)
    }
  }
  args
}

# Generate an arguments list by combining the values of parent nodes with the values of the expressions in the node's attributes list.
# Also, set the names of the arguments appropriately.
genNodeArgs <- function(pipeline,node,evaluator,envir=parent.frame()) { 
  parents <- inEdges(node,pipeline)[[node]]
  nodeargs <- lapply(parents,function(parent) { pipeline@env[[parent]] })
  argnames <- lapply(parents,edgeArgName,pipeline,node)
  names(nodeargs) <- argnames

# create an environment for evaluating arguments given as node attributes 
# containing the arguments from parent nodes
  if(length(nodeargs)==0) {
    tmpenv <- new.env(parent=envir)
  } else {
    tmpenv <- list2env(nodeargs,parent=envir)
  }

  extra_argnames_ <- names(which(!is.na(nodeData(pipeline,node)[[node]])))
  if(is.function(evaluator)) {
    extra_argnames <- extra_argnames_[extra_argnames_ != "function"]
  } else {
    extra_argnames <- extra_argnames_[extra_argnames_ != "expression"]
  }
  extra_args <- lapply(extra_argnames, function(arg) { 
    val <- processArgAttrValue(nodeData(pipeline,node,arg)[[node]],envir=tmpenv)
    return(val)
  }) 
  names(extra_args) <- extra_argnames
  args <- c(nodeargs, extra_args)

  # clean args to avoid error about extra arguments
  if(is.function(evaluator)) {
    args <- cleanArgs(args,evaluator)
  }

  which.named = vapply(names(args),function(x) {x!=""},FUN.VALUE=TRUE)
  if(length(which.named)>0) {
    # sort args by name, using R builtin sort function with LC_COLLATE set to 'C'
    locale = Sys.getlocale("LC_COLLATE")
    if(locale!='C') {
      Sys.setlocale("LC_COLLATE",'C')
    }
  
    # only sort args which have names
    args[which.named] = args[sort(names(args[which.named]))]
    names(args)[which.named] <- sort(names(args[which.named]))
    if(locale!='C') {
      Sys.setlocale("LC_COLLATE",locale)
    }
  }
  args
}

# This function evaluates, or loads through the caching system, each node in the nodes argument.
# If it fails to get the node value through the cache, it will call itself recursively on the parent nodes.
# This recursion will continue until it is able to get the values of the parents, possibly by first evaluating the grandparents, and their ancestors. 
# This is efficient for evaluating a single node, but when multiple nodes need to be evaluated, it is better to order the nodes using a topological sort and then evaluate the nodes in such a sequence. This is what the eval.Pipeline function does, and it sets a "live" flag on each node to signal that eval.PipelineNodes should not re-evaluate the node
eval.PipelineNodes <- function(pipeline, nodes, load.cache=TRUE, save.cache=TRUE, cachedir=tempdir(), cacheMethod=cacheMethodDigest, run.preprocessor=TRUE, overrides=list(...),context=digest(list()),envir=environment(),silent=FALSE,...) { # NOTE: for caching purposes, it is important that this function not modify upstream/ancestor nodes, when processing their children
  for (node in names(overrides)) {
      pipeline[node] <- overrides[[node]]
  }
  pipeline <- setLiveFlags(pipeline,names(overrides))
  
  if (run.preprocessor) {
    preprocessor(pipeline, envir=envir)
  }
  for (node in nodes) {
    if(!is.character(node)) stop("node must be a character vector")
    if(getLiveFlag(pipeline,node)) { # skip (re-)evaluation if node has already been evaluated
      next
    }
    if (load.cache) {
      pipeline[node] <- try({cacheObj <- cacheMethod(pipeline,node,cachedir=cachedir,envir=envir,context=context); loadCache(cacheObj,node);}, silent=TRUE)
    }
    if (!load.cache || class(pipeline[node])=="try-error") {
      parents <- parents(pipeline,node)
      pipeline <- eval.PipelineNodes(pipeline, parents, load.cache=load.cache, save.cache=save.cache, cachedir=cachedir, cacheMethod=cacheMethod, run.preprocessor=FALSE,overrides=list(),context=context,envir=envir)

# evaluate node
      evaluator <- getNodeEvaluator(pipeline, node, envir=envir)
      if(!is.function(evaluator) && !is.expression(evaluator)) { stop(paste0("Valid evaluator (function or expression) not found for node ",node)) }
      nodeargs <- genNodeArgs(pipeline, node, evaluator, envir=envir)
      if(!silent) {
        print(paste0("running function call for node '",node,"'"))
      }
      if(is.function(evaluator)) {
        pipeline[node] <- do.callInPipelineNode(evaluator, nodeargs, pipeline, node, envir=envir)
      } else {
        if(is.expression(evaluator)) {
          pipeline[node] <- do.evalInPipelineNode(evaluator, nodeargs, pipeline, node, envir=envir)
        }
      }
# save (cache) node data
      if (save.cache) {
        cacheObj <- cacheMethod(pipeline,node,cachedir=cachedir,envir=envir,context=context)
        saveCache(cacheObj, node)
      }
    }
  }
  pipeline
}

code.PipelineNodes <- function(pipeline, nodes, recursive=FALSE, run.preprocessor=TRUE, silent=FALSE,envir=environment(),...) { # NOTE: for caching purposes, it is important that this function not modify upstream/ancestor nodes, when processing their children
  if (run.preprocessor) {
    preprocessor(pipeline, envir=envir)
  }
  #expr=paste0(pipeline@preprocessor_lines, collapse='')
  for (node in nodes) {
    if(!is.character(node)) stop("node must be a character vector")
    if(getLiveFlag(pipeline,node)) { # skip (re-)evaluation if node has already been evaluated
      next
    }
    if (recursive) {
      parents <- parents(pipeline,node)
      expr <- paste0(expr,code.PipelineNodes(pipeline, parents, run.preprocessor=FALSE, envir=envir),"\n")
    } else {
      expr <- ""
    }

# evaluate node
    evaluator <- getNodeEvaluator(pipeline, node, envir=envir)
    if(!is.function(evaluator) && !is.expression(evaluator)) { stop(paste0("Valid evaluator (function or expression) not found for node ",node)) }
    nodeargs <- genNodeArgsStrings(pipeline, node, evaluator, envir=envir)
    evaluator_string <- getNodeEvaluatorString(pipeline, node, envir=envir)
    if(is.function(evaluator)) {
        expr <- paste0(expr,paste0(node," <- ", evaluator_string, "(",paste(names(nodeargs),nodeargs,sep="=",collapse=","),")"))
    } else {
      if(is.expression(evaluator)) {
        expr <- paste0(expr,paste0(node," <- ", evaluator_string))
      }
    }
  }
  expr
}


setMethod("eval.Pipeline",signature=c("character","ANY","ANY","ANY","ANY"),
def = function(pipeline, nodes=get_nodes(pipeline), run.preprocessor=TRUE, recurse=FALSE, envir=environment(), ...) {
  pipeline = read.Pipeline(pipeline)
  eval.Pipeline(pipeline,nodes,run.preprocessor,recurse,...)
})
.eval.Pipeline <- function(pipeline, nodes=get_nodes(pipeline), run.preprocessor=TRUE, recurse=FALSE, envir=environment(),...) {
  if (run.preprocessor) {
    preprocessor(pipeline, envir=envir)
  }
  error <- FALSE
  ancestors <- ancestors(pipeline,nodes)
  names(ancestors) <- NULL
  if(length(ancestors) > 0) {
    pipeline <- eval.Pipeline(pipeline,ancestors,run.preprocessor=FALSE, recurse=TRUE, envir=envir,...)
    pipeline <- setLiveFlags(pipeline,ancestors)
  }
  remainder = setdiff(nodes,ancestors)
  pipeline <- eval.PipelineNodes(pipeline,remainder,run.preprocessor=FALSE,envir=envir,...)
  if(!recurse) {
    pipeline <- resetLiveFlags(pipeline)
  }
  return(pipeline)
}

setMethod("eval.Pipeline",signature=c("Pipeline","ANY","ANY","ANY"),
def = .eval.Pipeline)

cacheMethodPipelineDigest <- function(pipeline, nodes, cachedir=tempdir(), envir=parent.frame(), context=NULL) {
  cacheObj <- list(pipeline=pipeline,cachePaths=c())
  cacheObj$cachePaths <- sapply(nodes, function(node) { file.path(cachedir,paste0(digest(c(pipeline@dot,node,context)),".Rdata")) })
  return(cacheObj)
}

# This function calls itself recursively on the ancestors of the nodes argument.
# After the cache data for the ancestors has returned from the recursive call,
# the ancestor data are used to get the caching information for the remaining nodes,
# which are then loaded and returned.
cacheMethodDigest <- function(pipeline, nodes, cachedir=tempdir(), envir=parent.frame(), context=NULL) { #NOTE: this function should only find the appropriate cached data when the parent nodes can be evaluated using the same cache method. This gives a recursive condition on the ancestor nodes.
  if(length(nodes)==0) return(list(pipeline=pipeline,cachePaths=c()))
  ancestors <- ancestors(pipeline,nodes)
  cacheObj <- cacheMethodDigest(pipeline,ancestors,cachedir=cachedir,context=context,envir=envir)

  parents <- parents(cacheObj$pipeline,nodes)
  rank1ancestors <- setdiff(parents,ancestors(cacheObj$pipeline,parents)) # Where the rank of an ancestor is the largest k such that the ancestor is in parents^k(nodes)
  remainder = setdiff(nodes,ancestors)
  for (node in rank1ancestors) {
    cacheObj$pipeline[node] <- loadCache(cacheObj,node)
  }
  for (node in remainder) {
    evaluator <- getNodeEvaluator(cacheObj$pipeline,node,envir=envir)
    nodeargs = genNodeArgs(cacheObj$pipeline,node,evaluator,envir=envir)
    path <- file.path(cachedir,paste0(digest(c(deparse(evaluator),nodeargs,context)),".Rdata"))
    cacheObj$cachePaths[node] <- path
  }
  return(cacheObj)
}

loadCache <- function(cacheObj, node, notlive=TRUE, throwerror=TRUE) { 
  if(getLiveFlag(cacheObj$pipeline,node) && notlive) return(cacheObj$pipeline[node])
  if(!file.exists(cacheObj$cachePaths[node])) stop(paste0("cache file for node '",node,"' does not exist at ",cacheObj$cachePaths[node]))
  tmpenv = new.env()
  print(paste0("loading cache for node '",node,"': ",cacheObj$cachePaths[node]))
  load(file=cacheObj$cachePaths[node], envir=tmpenv)
  if(length(tmpenv)!=1) { stop("cache contains more than one object") }
  if(!exists("data",tmpenv)) { stop("cache does not contain data") }
  tmpenv$data
}

cache <- function(pipeline,nodes=get_nodes(pipeline),cacheMethod=cacheMethodDigest,cachedir=tempdir(),run.preprocessor=TRUE, overrides=list(...),context=digest(list()),envir=globalenv(),...) {
  for (node in names(overrides)) {
      pipeline[node] <- overrides[node]
  }
  pipeline <- setLiveFlags(pipeline,names(overrides))
  if (run.preprocessor) {
    preprocessor(pipeline,envir)
  }
  cacheObj <- cacheMethod(pipeline,nodes=nodes,cachedir=cachedir,context=context,envir=envir)
  for (node in nodes) {
    data <- cacheObj$pipeline@env[[node]]
    save(data,file=cacheObj$cachePaths[node])
  }
}

cachePaths <- function(pipeline,nodes=get_nodes(pipeline),cacheMethod=cacheMethodDigest,cachedir=tempdir(),run.preprocessor=TRUE, overrides=list(...),context=digest(list()),envir=globalenv(),...) {
  for (node in names(overrides)) {
      pipeline[node] <- overrides[node]
  }
  pipeline <- setLiveFlags(pipeline,names(overrides))
  if (run.preprocessor) {
    preprocessor(pipeline,envir)
  }
  cacheObj <- cacheMethod(pipeline,nodes=nodes,cachedir=cachedir,context=context,envir=envir)
  return(cacheObj$cachePaths)
}

setLiveFlag <- function(pipeline, node) {
  liveflags <- pipeline@live
  liveflags[[node]] <- TRUE 
  pipeline@live <- liveflags
  return(pipeline)
}

# these functions set the list of boolean live flags which determine whether a node has already been evaluated
# these flags are used by eval.Pipeline to signal to eval.PipelineNodes that a node should not be reevaluated
# on subsequent calls, until after resetLiveFlags has been called
setLiveFlags <- function(pipeline, nodes) {
  for(node in nodes) {
    pipeline <- setLiveFlag(pipeline,node)
  }
  return(pipeline)
}

getLiveFlag <- function(pipeline, node) {
  liveflags <- pipeline@live
  liveflags[[node]] 
}

resetLiveFlags <- function(pipeline) {
  liveflags <- lapply(nodes(pipeline),function(x) FALSE)
  names(liveflags) <- nodes(pipeline)
  pipeline@live <- liveflags
  return(pipeline)
}

saveCache <- function(cacheObj, node) {
  data <- cacheObj$pipeline@env[[node]]
  save(data,file=cacheObj$cachePaths[node])
}
