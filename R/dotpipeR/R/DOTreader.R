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


trim <- function (x) gsub("^\\s+|\\s+$", "", x)
unquote <- function (x) gsub('\"','', x)

read.DOT <- function(dot_file) {
  dot <- .Call("readdot",as.character(dot_file))
  if(is.null(dot)) { stop("Could not read DOT file"); }
  return(dot)
}

read.Pipeline <- function(dot_file) {
  dot <- tryCatch({read.DOT(path.expand(dot_file))},error=function(err) { return(NULL) })
  if(is.null(dot)) { stop("Could not read DOT file"); }
  nodes <- dot[[1]]
  edgemat <- dot[[3]]
  preprocessor_lines <- dot[[5]]
  edgeL <- lapply(nodes, function(x) { edgemat[2,edgemat[1,]==x] })
  names(edgeL) <- nodes

  g = new("graphNEL",nodes=nodes,edgeL=edgeL,edgemode="directed")
  
  names(dot[[2]]) <- nodes
  for(node in nodes) {
    for(kv in dot[[2]][[node]]) {
      key = trim(unquote(trim(kv[1])))
      if(class(try(nodeDataDefaults(g,key),silent=TRUE))=="try-error") {
        nodeDataDefaults(g,key) <- NA
      }
      nodeData(g,node,key) <- trim(kv[2])
    }
  }
  if(length(dot[[4]])>0) {
    for(i in 1:length(dot[[4]])) {
      for(kv in dot[[4]][[i]]) {
        if(class(try(edgeDataDefaults(g,trim(kv[1])),silent=TRUE))=="try-error") {
          edgeDataDefaults(g,trim(kv[1])) <- NA
        }
        edgeData(g,edgemat[1,i],edgemat[2,i],trim(kv[1])) <- trim(kv[2])
      }
    }
  }
  p = as(g,"Pipeline")
  p@preprocessor_lines <- preprocessor_lines
  p@dot <- dot
  attr(p,"dot_file") <- dot_file
  p <- resetLiveFlags(p)
#  attr(p,"dot_data") <- dot
  return(p)
}
