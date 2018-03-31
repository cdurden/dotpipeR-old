\name{read.Pipeline}
\alias{read.Pipeline}
\title{Generate a Pipeline object from a DOT file}
\description{Generate a Pipeline object from a DOT file}
\usage{
read.Pipeline(dot_file)
}
\arguments{
  \item{dot_file}{A character object containing the filesystem path of the DOT file specifying the pipeline.}
}
\value{
  On success, a Pipeline object representing the DOT file is returned. If a syntax error occurs, the NULL value is returned. This function does not guarantee that the Pipeline object is in any way functional, such that execution of the pipeline will succeed.
}
\details{
  A DOT file must specify a directed graph, i.e. the graph definition must begin with the "digraph" keyword, NOT the "graph" keyword. The remainder of the syntax is described in 'The DOT Language' document, which can be found on the GraphViz website (See References).

  The parsing of DOT files has been implemented using Lex and Yacc, and is accessed by R through the .Call interface.
}
\references{ \href{The DOT Language}{http://www.graphviz.org/doc/info/lang.html} }
\author{Christopher Durden}
\keyword{pipeline}
\seealso{read.Pipeline, do.callInPipelineNode, cacheMatchDigest}
\examples{

dotfile <- system.file("extdata", "hello_world.dot", package="dotpipeR")
pipeline = read.Pipeline(dotfile)

}
