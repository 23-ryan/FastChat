
numUsers=$1
username=$2
password=$3

# SIGN UP
# for i in {1..3}; do python3 -c "let=chr(96 + $i); print(f'2\n{let}\n{let}{let}\n6\n')" | python3 interface.py localhost 5000; done


# SIGN IN and MESSAGE SEND
echo 1 > addUsers.txt
var=$(printf "\x$(printf %x $(expr 96 + $username))")
echo -e "$var" >> addUsers.txt
echo -e "$password" >> addUsers.txt

for (( c=1; c<=$numUsers; c++ ))
do 
    letter=$(printf "\x$(printf %x $(expr 96 + $c))")
    if [ $username -ne $c ]
    then
        echo 3 >> addUsers.txt
        echo 1 >> addUsers.txt
        echo $letter >> addUsers.txt
        # ########
        # MESSAGES
        echo "hello there asa saisa siahsis aishaish asajsoajsoa aosao" >> addUsers.txt
        echo "hello there asa saisa siahsis aishaish asajsoajsoa aosao" >> addUsers.txt
        echo "SEND IMAGE" >> addUsers.txt
        echo "send.jpg" >> addUsers.txt
        echo "did u get the image" >> addUsers.txt
        # ########
        echo "BACK" >> addUsers.txt
    fi
done
echo 6 >> addUsers.txt
python3 interface.py localhost 5000 < addUsers.txt


# # ADD USERS
# numUsers=$1

# for i in {1..3}
# do
#     echo 1 > addUsers.txt
#     var=$(printf "\x$(printf %x $(expr 96 + $i))")
#     echo -e "$var" >> addUsers.txt
#     echo -e "$var$var" >> addUsers.txt

#     for (( c=1; c<=$numUsers; c++ ))
#     do 
#         letter=$(printf "\x$(printf %x $(expr 96 + $c))")
#         if [ $i -ne $c ]
#         then
#             echo 1 >> addUsers.txt
#             echo $letter >> addUsers.txt
#         fi
#     done
#     echo 6 >> addUsers.txt

#     python3 interface.py localhost 5000 < addUsers.txt

# done

# 

