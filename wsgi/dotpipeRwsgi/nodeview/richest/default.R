setMethod("view",
    signature(x = "richest", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),height=1200,width=1200,...)
        plot(x)
        dev.off()
        return(graphics_data)
    }
)

setAs("richest","data.frame", function(from) data.frame(sample_size=from$sample_sizes,estimate=from$estimates))
