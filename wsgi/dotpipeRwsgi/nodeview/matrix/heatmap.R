setMethod("view",
    signature(x = "matrix", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),h=1000,w=1000,...)
        z <- matrix(as.numeric(x),nrow=nrow(x))
        rownames(z) <- rownames(x)
        colnames(z) <- colnames(x)
        heatmap(z,nrow=nrow(z))
        dev.off()
        return(graphics_data)
    }
)

