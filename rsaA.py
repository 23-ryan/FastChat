import rsa

public, private = rsa.newkeys(64)
print(type(public))