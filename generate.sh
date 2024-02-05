SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Default parameter
title="Dokumentasi"
images_path="images/"
output="$title.tex"


# how to run : ex. $ bash generate.sh "Event Documentation"

if [ -z "$1" ]
then
    if python $SCRIPT_DIR/script.py "$title" "$images_path" "$output"
    then
        if pdflatex "$output"
        then
            echo "Latex ($title) Generated"
        fi
    fi
else
    output="$1.tex"
    if python $SCRIPT_DIR/script.py "$1" "$images_path" "$output"
    then
        if pdflatex "$output"
        then
            echo "Latex ($1) Generated"
        fi
    fi
fi

# python $SCRIPT_DIR/script.py 'Dokumentasi Menari' 'images/' 'output.tex'