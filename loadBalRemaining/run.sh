for i in {1..3}
do
# var=$(printf "\x$(printf %x $(expr 96 + $i))")
# password="$var$var"
# bash addUser.sh 3 $i $password &
    python3 interface.py localhost 5000 &
# wait
done