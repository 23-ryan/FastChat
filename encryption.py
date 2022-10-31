import rsa
 
# generate public and private keys with
# rsa.newkeys method,this method accepts
# key length as its parameter
# key length should be atleast 16
publicKey, privateKey = rsa.newkeys(512)
publicKey2, privateKey2 = rsa.newkeys(512)
 
# this is the string that we will be encrypting
message = "hello user"
message2 = "hello user 2"
 
# rsa.encrypt method is used to encrypt
# string with public key string should be
# encode to byte string before encryption
# with encode method
# would only be able to decrypt with the private key corresponding to this public key
encMessage = rsa.encrypt(message.encode(),
                         publicKey)
# would only be able to decrypt with the private key corresponding to this public key
encMessage2 = rsa.encrypt(message2.encode(),publicKey2)
 
print("original string: ", message)
print("encrypted string: ", encMessage)
print("original string2: ", message2)
print("encrypted string2: ", encMessage2)
 
# the encrypted message can be decrypted
# with ras.decrypt method and private key
# decrypt method returns encoded byte string,
# use decode method to convert it to string
# public key cannot be used for decryption
decMessage = rsa.decrypt(encMessage, privateKey).decode()
decMessage2 = rsa.decrypt(encMessage2, privateKey2).decode()

# would not be able to decrypt as the message was encrypted using public key and
# hence must be decrypted using the corresponding private key
# decrypted = rsa.decrypt(encMessage, privateKey2).decode()

print("decrypted string: ", decMessage)
print("decrypted string2: ", decMessage2)