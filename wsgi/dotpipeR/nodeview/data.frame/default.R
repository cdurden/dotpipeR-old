setMethod("view",
    signature(x = "data.frame", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
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
