\name{Pipeline-class}
\Rdversion{1.1}
\docType{class}
\alias{Pipeline-class}
\alias{[,Pipeline,character-method}
\alias{[<-,Pipeline,character-method}
\alias{attach,Pipeline-method}

\title{Class \code{"Pipeline"}}
\description{
The Pipeline class is used to represent a computational pipeline data structure. The Pipeline class is a subclass of the GraphNEL class with a "directed" edgemode, with additional slots for preprocessor code and the DOT data associated with the pipeline.
%%  ~~ A concise (1-5 lines) description of what the class is. ~~
}
\section{Objects from the Class}{
Objects can be created by calls of the form \code{read.Pipeline(dotfile)}.
}
\section{Slots}{
  \describe{
    \item{\code{env}:}{Object of class \code{"environment"} ~~ }
    \item{\code{dot}:}{Object of class \code{"list"} ~~ }
    \item{\code{preprocessor_lines}:}{Object of class \code{"character"} ~~ }
    \item{\code{live}:}{Object of class \code{"list"} ~~ }
    \item{\code{nodes}:}{Object of class \code{"vector"} ~~ }
    \item{\code{edgeL}:}{Object of class \code{"list"} ~~ }
    \item{\code{edgeData}:}{Object of class \code{"attrData"} ~~ }
    \item{\code{nodeData}:}{Object of class \code{"attrData"} ~~ }
    \item{\code{renderInfo}:}{Object of class \code{"renderInfo"} ~~ }
    \item{\code{graphData}:}{Object of class \code{"list"} ~~ }
  }
}
\section{Extends}{
Class \code{"\linkS4class{graphNEL}"}, directly.
Class \code{"\linkS4class{graph}"}, by class "graphNEL", distance 2.
Class \code{"\linkS4class{graphBase}"}, by class "graphNEL", distance 3.
}
\section{Methods}{
  \describe{
    \item{[}{\code{signature(x = "Pipeline", i = "character")}: ... }
    \item{[<-}{\code{signature(x = "Pipeline", i = "character")}: ... }
    \item{attach}{\code{signature(what = "Pipeline")}: ... }
	 }
}
\author{
  Christopher Durden
}

\seealso{
read.Pipeline
eval.Pipeline
}
\examples{
showClass("Pipeline")

dotfile <- system.file("extdata", "hello_world.dot", package="dotpipeR")
pipeline = read.Pipeline(dotfile)
library(graph)
nodes(pipeline)

}
\keyword{classes}
