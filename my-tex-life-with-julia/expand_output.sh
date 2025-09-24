cd manuscript/

latexpand -o output.tex main.tex

latexindent --output=output.tex output.tex

cp output.tex ../ref-output.tex

latexpand --keep-comments -o ../ref-output-wc.tex main.tex

cd ..

latexindent --output=ref-output-wc.tex ref-output-wc.tex
