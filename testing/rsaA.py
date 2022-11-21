import rsa

public, private = rsa.newkeys(32)
print(list(public))
message = "hel2323 akshais askans ksnaknsansaksas aosa soasjoajsoa sasa sa0siais0ai0sia0 hel2323 akshais askans ksnaknsansaksas aosa soasjoajsoa sasa sa0siais0ai0sia0 hel2323 akshais askans"
k = rsa.encrypt(message.encode(), public)
print(rsa.decrypt(k, private).decode())
# print(type(public))
# lst = [2,3,4,5,6] 
# privatekey = rsa.key.PrivateKey(lst)
# print(privatekey)
# print(type(privatekey))