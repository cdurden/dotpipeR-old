setGeneric(name="view",def=function(x,method,tmpdir,...) standardGeneric("view"))

png <- function(filename,...) {
  fn <- get("png",pos="package:grDevices")
  graphics_data <- list()
  fn(filename=filename,...)
  graphics_data[[length(graphics_data)+1]] <- list(format="png",file=filename) 
  graphics_data
}

setMethod("view",
    signature(x = "matrix", method = "character", tmpdir = "ANY"),
    function (x, method=c("heatmap","default"),tmpdir=tempdir(),...)
    {
        if(method=="heatmap") {
            graphics_data <- png(tempfile(tmpdir=tmpdir),...)
            heatmap(x)
            dev.off()
            return(graphics_data)
        }
    }
)

