library(geosphere)
library(ggmap)
setMethod("view",
    signature(x = "SpatialPoints", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        distances <- distm(c(-78.692528,35.771155), x, fun = distHaversine)[1,]
        coords0 <- coordinates(x[which.min(distances)])
        coords0 <- c(-78.3697,35.7810)
        coords <- coordinates(x)[order(distances),]
        m <- get_map(coords0)
        colnames(coords) <- c('lon','lat')
        tmpfile <- tempfile(tmpdir=tmpdir)
        ggmap(m)+geom_point(data=data.frame(coords),shape=3)
        ggsave(tmpfile,device='png',height=1200,width=1200)
        return(tmpfile)
    }
)
