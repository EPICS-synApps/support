all: html pdf

pdf: mda2ascii.pdf mda-dump.pdf mda-info.pdf mda-ls.pdf mda-load.pdf mdatree2ascii.pdf
html: mda2ascii.html mda-dump.html mda-info.html mda-ls.html mdatree2ascii.html


mda2ascii.html : mda2ascii.1
	groff -man -Thtml mda2ascii.1 > mda2ascii.html

mda2ascii.pdf : mda2ascii.1
	groff -man -Tps mda2ascii.1 | ps2pdf - mda2ascii.pdf


mda-dump.html : mda-dump.1
	groff -man -Thtml mda-dump.1 > mda-dump.html

mda-dump.pdf : mda-dump.1
	groff -man -Tps mda-dump.1 | ps2pdf - mda-dump.pdf


mda-info.html : mda-info.1
	groff -man -Thtml mda-info.1 > mda-info.html

mda-info.pdf : mda-info.1
	groff -man -Tps mda-info.1 | ps2pdf - mda-info.pdf


mda-ls.html : mda-ls.1
	groff -man -Thtml mda-ls.1 > mda-ls.html

mda-ls.pdf : mda-ls.1
	groff -man -Tps mda-ls.1 | ps2pdf - mda-ls.pdf


mda-load.pdf : mda-load.tex
	latex mda-load.tex
	latex mda-load.tex
	dvipdfm -p letter -o mda-load.pdf mda-load.dvi

mdatree2ascii.html : mdatree2ascii.1
	groff -man -Thtml mdatree2ascii.1 > mdatree2ascii.html

mdatree2ascii.pdf : mdatree2ascii.1
	groff -man -Tps mdatree2ascii.1 | ps2pdf - mdatree2ascii.pdf


.PHONY : clean
clean:
	-rm *.pdf *.html *.dvi *.aux *.log

