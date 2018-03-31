SWEAVE_INCLUDE_DIR=${HOME}
DATA_DIR=${HOME}/data/
TEX_INPUTS=${TEXINPUTS}:.:${HOME}/.tex:${R_HOME}/share/texmf/tex/latex/
BUILDDIR=`pwd`

all: report.pdf
clean:
	if [ -e include ]; then rm -rf include; fi
	if [ -e tables ]; then rm -rf tables; fi
	rm *.pdf *.dvi *.tex *.aux *.log *.bbl *.blg
%.tex: %.Rnw
	if [ -e include ]; then rm -rf include; fi
	if [! -e tables ]; then mkdir tables; fi
	mkdir include
	R CMD Sweave $<
%.pdf: %.tex
	TEXINPUTS=${TEX_INPUTS} pdflatex $*
	rm *.log *.aux
