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


addNode <- function(node, object, attrs) {
  object = as(object,"graphNEL")
  if (length(node)>1) {
    stop("addNode only adds one node at a time")
  } 
  object <- graph::addNode(node,object,list())
  for(attr in names(attrs)) {
    object <- tryCatch({graph::nodeDataDefaults(object, attr); object}, error = function(e) {graph::nodeDataDefaults(object, attr) <- NA; object})
    graph::nodeData(object, node, attr) <- attrs[[attr]]
  }
  object <- as(object,"Pipeline")
  object <- resetLiveFlags(object)
  return(object)
}

addEdge <- function(from, to, object, attrs) {
  object <- as(object,"graphNEL")
  if (length(from)>1) {
    stop("addEdge only adds one edge at a time")
  } 
  object <- graph::addEdge(from, to, object, rep(1,length(from)))
  for(attr in names(attrs)) {
    object <- tryCatch({graph::edgeDataDefaults(object, attr); object}, error = function(e) {graph::edgeDataDefaults(object, attr) <- NA; object})
    graph::edgeData(object, from, to, attr) <- attrs[[attr]]
  }
  object <- as(object,"Pipeline")
  object <- resetLiveFlags(object)
  return(object)
}
#setMethod("addNode",signature=c("character","Pipeline","list"),
#def = addNode)
#setMethod("addEdge",signature=c("character","character","Pipeline","list"),
#def = addEdge)


removeNode <- function(node, object, attrs) {
  object = as(object,"graphNEL")
  if (length(node)>1) {
    stop("addNode only adds one node at a time")
  } 
  graph::addNode(node,object,list())
  for(attr in names(attrs)) {
    graph::nodeData(object, node, attr) <- attrs[[attr]]
  }
  object <- as(object,"Pipeline")
  object <- resetLiveFlags(object)
  return(object)
}

removeNode <- function(node, object) {
  object <- as(object,"graphNEL")
  object <- graph::removeNode(node, object)
  object <- as(object,"Pipeline")
  object <- resetLiveFlags(object)
  return(object)
}
removeEdge <- function(from, to, object) {
  object <- as(object,"graphNEL")
  object <- graph::removeEdge(from, to, object)
  object <- as(object,"Pipeline")
  object <- resetLiveFlags(object)
  return(object)
}
#pipeline <- addNode("test",pipeline,list("function"="c"))
#pipeline <- addEdge("hello_world","test",pipeline,list("name"="a"))
#pipeline <- eval.Pipeline(pipeline)
#pipeline <- removeNode("test",pipeline)

