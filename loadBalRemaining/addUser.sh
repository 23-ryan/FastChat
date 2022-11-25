for i in {1..2}
do
    # python3 interface.py localhost 5000
    var=$(printf "\x$(printf %x $(expr 96 + $i))")
    echo $var

done