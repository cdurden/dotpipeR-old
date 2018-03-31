setMethod("view",
    signature(x = "graphNEL", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),...)
        plot(x)
        dev.off()
        return(graphics_data)
    }
)
