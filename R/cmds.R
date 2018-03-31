library(dotpipeR)
linkCaches <- function(pipeline,overrides=list(...),overwrite=TRUE,...) {
  cache_files = cachePaths(pipeline,cachedir=cachedir,overrides=overrides)
  link_files = cachePaths(pipeline,nodes=names(cache_files),cachedir=cachedir,cacheMethod=cacheMethodPipelineDigest)
  if(overwrite) { file.remove(link_files[file.exists(link_files)]) }
  mapply(file.symlink,cache_files,link_files)
}

homedir <- Sys.getenv('HOME')
cachedir = file.path(homedir,'tmp/dotpipeR')
dotdir <- file.path(homedir,'dotpipeR/dot')
setwd(tempdir())
pipeline <- eval.Pipeline(file.path(dotdir,'dimova_regression.dot'),cachedir=cachedir)
linkCaches(pipeline)
#pipeline <- eval.Pipeline(file.path(dotdir,'hello_world.dot'),cachedir=cachedir)
#pipeline <- eval.Pipeline(file.path(dotdir,'dimova_regression.dot'),cachedir=cachedir,overrides=list(datadir=file.path(homedir,'GSE19029')))
#linkCaches(pipeline,overrides=list(datadir=file.path(homedir,'GSE19029')))
#linkCaches(pipeline)
#pipeline <- eval.Pipeline(file.path(dotdir,'richest.dot'),cachedir=cachedir)
#linkCaches(pipeline)

















#pipeline <- eval.Pipeline(file.path(dotdir,'csc_mousemodel.dot'),cachedir=cachedir)


#dotfile="/home/cld/projects/dotpipelines/diet_analysis.dot"
#dotfile="/home/cld/projects/dotpipelines/gse19029.dot"
#dotfile="/home/cld/projects/dotpipelines/csc_mousemodel.dot"
#dotfile="/home/cld/projects/dotpipeR/examples/income.dot"
#dotfile="/home/cld/projects/dotpipelines/morelpatterns.dot"
#setwd("/home/cld/projects/richest/examples/data/")
#dotfile="/home/cld/projects/dotpipelines/out/richest.dot"
#dotfile="/home/cld/projects/dotpipelines/hello_world.dot"
#dotfile="/home/cld/projects/dotpipelines/superpipe.dot"
#dotfile="/home/cld/projects/dotpipelines/dimova_regression_refactored.dot"
#dotfile="/tmp/syntaxerror.dot"
#pipeline = eval.Pipeline(dotfile,cachedir=cachedir,envir=globalenv(),linkWithCacheMethods=c(cacheMethodPipelineDigest))
#
##source("http://bioconductor.org/biocLite.R")
##pkgs = c("affy","sva","limma","GEOquery","graph","AnnotationDbi","marray","Rgraphviz")
##for(pkg in pkgs) { biocLite(pkg) }
##install.packages("maps")
##install.packages("mapdata")
##install.packages("ggmap")
#
##cache_files = cachePaths(pipeline,cacheMethod=cacheMethodDigest,cachedir=cachedir)
##setwd(unique(dirname(cache_files)))
##val = tar("csc_mousemodel_Rdata.tar.gz",files=basename(cache_files),compression="gzip",tar="/bin/tar")
##mapply(file.symlink,cache_files,cachePaths(pipeline,cacheMethod=cacheMethodPipelineDigest,cachedir=cachedir))
#
#
#gse41717_genes <- extractGeneSymbols(fData(pipeline['gse41717'][[1]]))
#gse10327_genes <- fData(pipeline['gse10327'][[1]])[,"Gene Symbol"]
#leading_edge_genes <- rownames(pipeline['leading_combined']$combined.expr)
#map <- mapVectors(leading_edge_genes,gse41717_genes)
#z <- unfactor(mergeByMap(pipeline['leading_combined']$combined.expr,pipeline['gse41717_exprs'],map))
#plot(log(as.numeric(z[,201])),as.numeric(z[,222]))
#cor(apply(z[,201:210],2,as.numeric),apply(z[,211:220],2,as.numeric))
#
#map <- mapVectors(gse41717_genes,leading_edge_genes)
#pipeline['gse41717_exprs'][map$CXCR4,]
#pipeline['leading_combined']$combined.expr['CXCR4',]
#
#extractGeneSymbol(fData(pipeline['gse41717'][[1]][20000:20050,]))
#to <- fData(pipeline['gse10327'][[1]])[,"Gene Symbol"]
#
#"ACP2" %in% fData(pipeline['gse10327'][[1]])[,"Gene Symbol"]
#map <- sapply(extractGeneSymbol(fData(pipeline['gse41717'][[1]][20000:20050,])),function(from_elmt) {
#  if(is.factor(to)) {
#    to = levels(to)[to]
#  }
#  which(grepl(paste0("^",from_elmt,"$"),to,ignore.case=TRUE))
#})
#  
#
#
#
#head(fData(pipeline['gse41717'][[1]]))
#index = with(fData(pipeline['gse41717'][[1]]), SPOT_ID!="control" & SPOT_ID!="Not currently mapped to latest genome")
#head(fData(pipeline['gse41717'][[1]])[index,],n=10)
#"PLCL1" %in% fData(pipeline['gse10327'][[1]])[,"Gene Symbol"]
#extractGeneSymbol(fData(pipeline['gse41717'][[1]])
#head(fData(pipeline['gse10327'][[1]]))
#
#cacheMatchDigest(pipeline,"gse41717_design",cachedir=getwd(),fn=NULL)
#digest(genNodeArgs(pipeline,'gse41717_design'))
#
#pipeline['gse41717_eBayes']
#hist(pipeline['gse41717_eBayes']$F.p.value)
#
#
#setwd("/home/cld/projects/biology/genereg/data")
#dotfile="/home/cld/projects/dotpipelines/58b920e7-e5f4-473f-8580-48ffae7539fb.dot"
#dotfile="/home/cld/projects/dotpipelines/sim_ecoli_gmrf.dot"
#
#
#
#exprs(pipeline['gse41717'][[1]][1,])
#pipeline['gse41717_eBayes']
#
#
#pData(pipeline['gse41717'][[1]])
#levels(fData(pipeline['gse41717'][[1]])$SPOT_ID)
#
#names(fData(pipeline['gse41717'][[1]])[index,])
#
#model.matrix(~characteristics_ch1,pData(pipeline['gse41717'][[1]]))
#index = which(is.numeric(fData(pipeline['gse41717'][[1]])$total_probes))
#index = which(fData(pipeline['gse41717'][[1]])$total_probes!='')
#pData(pipeline['gse41717'][[1]])
#
#dim(exprs(pipeline['gse41717'][[1]]))
#rownames(exprs(pipeline['gse41717'][[1]]))
#fData(pipeline['gse41717'][[1]])
#featureData(pipeline['gse41717'][[1]])
#
#
#cacheMatchDigest(pipeline,"gmrf",cachedir=getwd(),fn=NULL)
#A = as(pipeline['gmrf'],"matrix")
#which(rownames(A) %in% pipeline['gmrf']@parameters[[9]]$nodes)
#
#pipeline['gmrf']
#
#i <- 2
#i <- 9 
#i <- 20
#i <- 30
#pipeline['gmrf']@parameters[[i]]$covariance
#L <- pipeline['regparams'][rownames(pipeline['gmrf']@parameters[[i]]$covariance),rownames(pipeline['gmrf']@parameters[[i]]$covariance)]
#t(L)%*%L
#max(abs(pipeline['gmrf']@parameters[[i]]$covariance - t(L)%*%L))
#sapply(1:length(pipeline['gmrf']@parameters),function(i) {
#  nrow(pipeline['gmrf']@parameters[[i]]$covariance)
#}
#
#hist(pipeline['gmrf']@parameters[[i]]$covariance)
#hist(pipeline['gmrf']@parameters[[i]]$covariance - t(L)%*%L)
#
#max(pipeline['gmrf']@parameters[[i]]$covariance)
#
#run.PipelinePreprocessor(pipeline)
#cacheMatchDigest(pipeline,"doc",cachedir=getwd(),fn=NULL)
#pipeline <- eval.PipelineNode(pipeline,"doc",do.call=TRUE)
#cacheMatchDigest(pipeline,"text",cachedir=getwd(),fn=NULL)
#
#nodeargs <- genNodeArgs(pipeline,"doc")
#fn <- getNodeCall(pipeline, "doc")
#doc = do.callInPipelineNode(fn, nodeargs, pipeline, "doc",envir=globalenv())
#
#path = cacheMatchDigest(pipeline,"doc",cachedir=getwd(),fn=NULL)
#cache(pipeline, "doc", path)
#
#data = pipeline@env[['doc']]
#save(data, file=path)
#
#ls(pos="package:XML")
#
#library(richest)
#cps = read.cps("/home/cld/projects/richest/examples/data/sargassoSeaOTU_CPS_unique.txt")
#spc = as(cps,"spc")
#BayesNP(cps,seq(0,5000,100))
#gt(cps,seq(0,5000,100))
#r = richest(spc,'PNPMLE',0,5000,100)
#plot(r)
#library.dynam.unload("richest",libpath=path.package("richest"))
#detach("package:richest",unload=TRUE)
#
#
#pipeline = read.Pipeline(dotfile)
#pipeline <- eval.PipelineNode("c",pipeline,do.call=TRUE)
#pipeline <- exec.Pipeline(pipeline)
#cacheMatchDigest(pipeline,"location",cachedir=getwd(),fn=NULL)
#cacheMatchDigest(pipeline,"latlon",cachedir=getwd(),fn=NULL)
#cacheMatchDigest(pipeline,"maleTotals",cachedir=getwd(),fn=NULL)
#
#node = "latlon"
#load(cacheMatchDigest(pipeline,node,cachedir=getwd(),fn=NULL))
#data = tmpenv$data
#save(data,file=cacheMatchDigest(pipeline,node,cachedir=getwd(),fn=NULL))
#
#pipeline <- exec.pipe(pipeline,cacheMatch=cacheMatchPipelineDigest)
#
#library(arraydata)
#source("/home/cld/projects/biology/src/microarray/R/mafn.R")
#dotfile="/home/cld/projects/dotpipeR/examples/gse19029.dot"
#pipeline = read.Pipeline(dotfile)
#pipeline <- eval.PipelineNode(pipeline,"MA")
#pipeline <- eval.PipelineNode(pipeline,"dimovaRegression")
#pipeline <- exec.Pipeline(pipeline)
#pipeline <- linkCaches.Pipeline(pipeline,cacheMatchSource=cacheMatchDigest,cacheMatchDest=cacheMatchPipelineDigest,cachedir=getwd(),overwrite=TRUE)
#pipeline <- eval.PipelineNode(pipeline,"dimovaRegression",cacheMatch=cacheMatchPipelineDigest)
#pipeline <- eval.PipelineNode(pipeline,"'dimovaRegression'",cacheMatch=cacheMatchPipelineDigest)
#
#p = read.Pipeline("/home/cld/projects/dotpipeR/examples/income.dot")
#p = exec.Pipeline(p)
#
#
#system.time(pipeline <- eval.PipelineNodeAncestors(pipeline,"dimovaRegression"))
##   user  system elapsed 
##185.144  14.328 224.821 
#system.time(pipeline <- eval.PipelineNode(pipeline,"dimovaRegression"))
#
#
#dot <- read.dot(dotfile)
#
#dotfile="/home/cld/projects/dotreader/dot/ex4.dot"
#dotfile="/home/cld/projects/dotreader/dot/ex3.dot"
#dotfile="/home/cld/projects/dotreader/dot/ex1.dot"
#dot = read.dot(dotfile)
#dot[[5]]
#
#
#dot[[5]][1]
#
#trim <- function (x) gsub("^\\s+|\\s+$", "", x)
#
#attrs = strsplit(dot[[5]][1],";")[[1]]
#nodes = strsplit(attrs[1],",")[[1]]
#edgemat = matrix(dot[[4]][1:(2*dot[[3]])],nrow=2)
#lapply(1:dot[[2]],function(x) { edgemat[2,edgemat[1,]==x] })
#edgeL = lapply(1:dot[[2]],function(x) { nodes[edgemat[2,edgemat[1,]==x]] })
#names(edgeL) <- nodes
#g = graphNEL(nodes, edgeL,edgemode="directed")
#
##node_attrs = list()
##edge_attrs = list()
#for(i in 1:dot[[2]]) {
#  node_attr = strsplit(attrs[i+1],",")[[1]]
##  node_attrs[[i]] = strsplit(attrs[i+1],",")[[1]]
#  for(kv in strsplit(node_attr,"=")) {
#    if(class(try(nodeDataDefaults(g,trim(kv[1])),silent=TRUE))=="try-error") {
#      nodeDataDefaults(g,trim(kv[1])) <- NA
#    }
#    nodeData(g,nodes(g)[i],trim(kv[1])) <- trim(kv[2])
#  }
##  nodeData(g,nodes(g)[i],
##  print(node_attrs)
#}
#for(i in 1:dot[[3]]) {
#  edge_attr = strsplit(attrs[i+2+dot[[2]]],",")[[1]]
#  for(kv in strsplit(edge_attr,"=")) {
#    if(class(try(edgeDataDefaults(g,trim(kv[1])),silent=TRUE))=="try-error") {
#      edgeDataDefaults(g,trim(kv[1])) <- NA
#    }
#    edgeData(g,nodes(g)[edgemat[1,i]],nodes(g)[edgemat[2,i]],trim(kv[1])) <- trim(kv[2])
#  }
##  edge_attrs[[i]] = strsplit(attrs[i+2+dot[[2]]],",")[[1]]
##  print(edge_attrs)
#}
#
#names(node_attrs) <- nodes
#
#p = new("Pipeline",nodes, edgeL,data=node_attrs)
#p = as(g,"Pipeline")
#p@data = node_attrs
#
#
#p = new("Pipeline")
#attr(p,"filepath") <- dot[[1]]
#p = read.dotpipeR(dotfile)
#g. <- function(a,b) { a+b}
#f <- function(a,b) { a*b}
#p@calls['c'] = "f"
#p@calls['d'] = "g"
#
#eval.pipeNode("c",p, envir=globalenv())
