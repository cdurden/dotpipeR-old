setMethod("view",
    signature(x = "RasterBrick", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),height=1200,width=1200,...)
        plot(x)
        dev.off()
        return(graphics_data)
    }
)
