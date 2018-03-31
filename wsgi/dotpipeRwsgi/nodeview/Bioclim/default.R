setMethod("view",
    signature(x = "Bioclim", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),height=1200,width=1200,...)
        plot(x)
        dev.off()
        return(graphics_data)
    }
)
        #library(maps)
        #library(mapdata)
        #data(countyMapEnv)
        #map('county', region=c('north carolina,wake','north carolina,franklin','north carolina,nash','north carolina,johnston'))
        #points(coordinates(spTransform(x,CRS("+proj=longlat"))),pch=".",cex=3)
