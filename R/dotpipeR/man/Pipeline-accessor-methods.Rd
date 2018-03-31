\name{Pipeline-accessor-methods}
\alias{[,Pipeline-method}
\alias{[<-,Pipeline-method}
\alias{[}
\alias{[<-}
\title{Pipeline node data accessor method}
\description{Methods for getting and setting Pipeline node data}
\section{Methods}{
\describe{
\item{\code{pipeline[nodes]}}{}
\item{\code{pipeline[nodes] <- values}}{}
}}
\arguments{
  \item{pipeline}{The Pipeline object to be accessed or modified}
  \item{nodes}{An atomic vector, or NULL, giving the names of the nodes to select.}
  \item{values}{A list of the same length as nodes giving the values to assign to the selected nodes, given in the corresponding order.}
}
\keyword{methods}
\keyword{Pipeline}
