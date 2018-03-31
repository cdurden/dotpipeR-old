setMethod("view",
    signature(x = "matrix", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),height=1200,width=1200,...)
        if(ncol(x)>nrow(x)) {
            pc <- princomp(t(x))
        } else {
            pc <- princomp(x)
        }
        biplot(pc)
        dev.off()
        return(graphics_data)
    }
)

