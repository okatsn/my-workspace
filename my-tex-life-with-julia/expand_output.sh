cd manuscript/

latexpand -o manuscript.tex main.tex

latexindent --output=manuscript.tex manuscript.tex

cp manuscript.tex ../ref-manuscript.tex

latexpand --keep-comments -o ../ref-manuscript-wc.tex main.tex

cd ..

latexindent --output=ref-manuscript-wc.tex ref-manuscript-wc.tex
