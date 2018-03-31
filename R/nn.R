library(dotpipeR)
f <- function(x) {
  x <- as.logical(x);
  as.numeric(c( xor(x[1] && x[2], x[3] && x[4]),
                x[3] && x[5] || x[1],
                x[1] || x[4] || x[5],
                x[2] && x[4] || x[5],
                x[1]))}


fitness <- function(pipeline, inputs, f) {
  C <- 0
  for (input in inputs) {
    input <- sample(0:1,size=m,replace=TRUE)
    for (j in 1:m) {
      nodeData(pipeline, paste0("n",0,j), "expression") <- input[j]
    }
    pipeline <- eval.Pipeline(pipeline,save.cache=FALSE,load.cache=FALSE,silent=TRUE)
    output <- sapply(1:m,function(j) pipeline[paste0("n",n,j)])
    C <- C+sum(abs(f(input)-output))
  }
  return(exp(-C/length(inputs)))
}

select <- function(pipelines, inputs) {
  F <- lapply(pipelines, fitness, f=f, inputs=inputs)
  i <- FALSE
  while(sum(i)<2) {
    i <- as.logical(sapply(F,function(p) rbinom(1,1,p)))
  }
  list(fitness=mean(F),survivors=pipelines[i])
}

mate <- function(pipelineA, pipelineB, p) {
  pipelineC <- pipelineA
  crossoverToB <- FALSE
  for (node in nodes(pipelineB)) {
    crossoverToB = xor(crossoverToB,as.logical(rbinom(1,1,p)))
    if (crossoverToB) {
      edgesInC <- edges(reverseEdgeDirections(pipelineC))[[node]]
      edgesInB <- edges(reverseEdgeDirections(pipelineB))[[node]]
      for (from in edgesInC) {
        pipelineC <- removeEdge(from, node, pipelineC)
      }
      for (from in edgesInB) {
        pipelineC <- addEdge(from, node, pipelineC, edgeData(pipelineB, from, node)[[1]])
      }
    }
  }
  pipelineC
}
inputs <- as.list(as.data.frame(t(expand.grid(data.frame(matrix(rep(0:1,5),nrow=2))))))
sig <- function(...) { S <- exp(-sum(...)); 1/(1+S) }

pipelines <- list()
for (k in 1:10) {
  pipeline <- new("Pipeline")
  n <- 2
  m <- 5
  input <- c(1,1,1,1,1)
  for (j in 1:m) {
    pipeline <- addNode(paste0("n",0,j), pipeline, list("expression"=input[j]))
  }
  for (i in 1:n) {
    for (j in 1:m) {
      pipeline <- addNode(paste0("n",i,j), pipeline, list("function"="sig"))
      inputs <- paste0("n",i-1,sample(1:m,sample(m,1)))
      for (from in inputs) {
        pipeline <- addEdge(from, paste0("n",i,j), pipeline, list())
      }
    }
  } 
pipelines[[k]] <- pipeline
}
#pipeline <- eval.Pipeline(pipeline,save.cache=FALSE,load.cache=FALSE)

avgfitness <- c()
for (l in 1:2) {
  selection <- select(pipelines,inputs)
  pipelines <- selection$survivors
  print(selection$fitness)
  avgfitness <- c(avgfitness, selection$fitness)
  offspring <- list()
  for (k in 1:10) {
    i <- sample(1:length(pipelines),2,replace=TRUE)
    offspring[[k]] <- mate(pipelines[[i[1]]],pipelines[[i[2]]],0.1)
  }
  pipelines <- offspring
}
