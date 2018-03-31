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

setClass("Pipeline", contains='graphNEL', representation("graphNEL", env='environment', dot='list',preprocessor_lines='character',live='list'), prototype=list(new("graphNEL",edgemode="directed"),env=environment(),preprocessor_lines=character(),live=list()))
setMethod("initialize", "Pipeline", function(.Object,env=new.env(),preprocessor_lines=character(),...) {
  .Object <- callNextMethod(.Object,edgemode="directed",...)
  .local <- function(.Object, env = new.env(), preprocessor_lines = character(), ...) {
    .Object@env = env 
    .Object@preprocessor_lines = preprocessor_lines
    .Object = resetLiveFlags(.Object)
    .Object
  }
  .local(.Object,env=env,preprocessor_lines=preprocessor_lines,...)
})

setMethod("[",signature=c("Pipeline","ANY"),
  def=function(x,i=TRUE,drop=FALSE) {
    if(length(i)==0) {
      return(NULL)
    } else {
      if(length(i)==1) {
        return(x@env[[i]])
      } else {
        return(sapply(i,function(j) { x@env[[j]] }))
      }
    }
  }
)
setMethod("[<-",signature=c("Pipeline","ANY","ANY"),
  def=function(x,i,value) {
    if(length(i)!=0) {
      if(length(i)==1) {
        x@env[[i]] <- value
      } else {
        for (j in 1:length(i)) {
          if(!(i[[j]] %in% nodes(x))) stop("There is no node named '",i[[j]],"' in pipeline")
          x@env[[i[[j]]]] <- value[[j]]
        }
      }
    }
    x
  }
)

setMethod("attach",
    signature(what = "Pipeline","ANY","ANY","ANY"),
    function (what, pos = 2, name = deparse(substitute(what)), warn.conflicts = TRUE)
    {
        attach(what@env, pos, name, warn.conflicts)
    }
)

setAs("Pipeline","environment", function(from, to) from@env)
