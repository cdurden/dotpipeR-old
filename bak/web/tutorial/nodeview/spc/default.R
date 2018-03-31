setMethod("view",
    signature(x = "spc", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),...)
        spc = data.frame(as(x,'spc'))
        plot(spc)
        dev.off()
        return(graphics_data)
    }
)
