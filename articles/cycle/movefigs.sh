#!/bin/bash

paper="alps-cycle"

# rename figures
i=1
grep includegraphics $paper.tex | while read l
do
    fig=${l:27:-2}
    ii=$(printf '%02d' $i)

    # copy figure files
    cp -v ../../figures/$fig.pdf fig$ii.pdf

    # replace in the latex file
    sed -i "s/\includegraphics{$fig}/\includegraphics{fig$ii}/" $paper.tex

    ((++i))
done

# put them in zip archive
zip figures.zip fig??.pdf
rm fig??.pdf
