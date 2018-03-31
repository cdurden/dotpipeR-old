library(maptools)
data(wrld_simpl)
getlatlon <- function(x) {
  lon = unlist(lapply(x[,"decimalLongitude"], as.numeric))
  lat = unlist(lapply(x[,"decimalLatitude"], as.numeric))
  latlon = cbind(lon,lat)
  colnames(latlon) <- c("lon","lat")
  return(as.data.frame(latlon))
}

setMethod("view",
    signature(x = "gbif_data", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),height=1200,width=1200,...)
        latlon <- getlatlon(as.data.frame(x$data))
        plot(wrld_simpl, border='dark grey', xlim=range(latlon['lon']), ylim=range(latlon['lat']))
        points(latlon)
        dev.off()
        return(graphics_data)
    }
)
