setMethod("view",
    signature(x = "data.frame", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),height=1200,width=1200,...)
        mat <- as.matrix(as.data.frame(lapply(x,function(x) { if(is.factor(x)) { return(as.numeric(levels(x)[x])) } else {return(as.numeric(x))} })))
        heatmap(mat)
        dev.off()
        return(graphics_data)
    }
)

unfactor <- function(x) {
  result <- c()
  for(i in 1:ncol(x)) {
    if(is.factor(x[,i])) {
      result = cbind(result,levels(x[,i])[x[,i]])
    } else {
      result = cbind(result,x[,i])
    }
  }
  result <- as.data.frame(result,stringsAsFactors=FALSE)
  dimnames(result) = dimnames(x)
  result
}
