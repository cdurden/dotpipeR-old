setMethod("view",
    signature(x = "matrix", tmpdir = "ANY"),
    function (x, tmpdir=tempdir(),...)
    {
        graphics_data <- png(tempfile(tmpdir=tmpdir),height=1200,width=1200,...)

        library(colorspace)
        layout(matrix(c(1, 2), 1, 2), width = c(8, 2))
        par(mar = c(4, 4, 5, 3))
        col <- diverge_hcl(8, h = c(246, 40), c = 96, l = c(65, 90))
        image(x,axes=FALSE,col=col)
        axis(1,at=seq(0,1,length.out=nrow(x)),labels=rownames(x))
        axis(2,at=seq(0,1,length.out=ncol(x)),labels=colnames(x))
        par(mar = c(3, 0, 3, 3))
        sequence = seq(min(x),max(x),length.out=length(col))
        image(1,sequence,matrix(sequence,nrow=1,ncol=length(sequence)),col=col,axes=FALSE)
        axis(4,at=c(min(x),0,max(x)),labels=sprintf("%0.01f",c(min(x),0,max(x))))

        dev.off()
        return(graphics_data)
    }
)

