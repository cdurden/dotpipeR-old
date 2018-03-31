view <- function(x, tmpdir=tempdir(),...)
        {
                UseMethod("view",x)
        }

view.bison <- function (x, tmpdir=tempdir(),...)
    {
        library(rbison)
        library(ggplot2)
        tmpfile <- tempfile(tmpdir=tmpdir)
        bisonmap(x)
        ggsave(tmpfile,device='png',height=12,width=12,dpi=100)
        print(class(x))
        print(paste0("bison object: ",tmpfile))
        return(tmpfile)
    }
