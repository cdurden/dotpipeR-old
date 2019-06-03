setMethod("view",
    signature(x = "cps", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),height=1200,width=1200,...)
        spc = data.frame(as(x,'spc'))
        plot(spc)
        dev.off()
        return(graphics_data)
    }
)
