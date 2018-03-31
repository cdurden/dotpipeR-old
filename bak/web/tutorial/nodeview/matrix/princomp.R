setMethod("view",
    signature(x = "matrix", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),h=1000,w=1000,...)
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

