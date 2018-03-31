setMethod("view",
    signature(x = "matrix", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),h=1000,w=1000,...)
        heatmap(x)
        dev.off()
        return(graphics_data)
    }
)

