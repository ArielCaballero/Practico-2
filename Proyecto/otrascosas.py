from werkzeug.security import check_password_hash
import hashlib

b=hashlib.md5(bytes("anaestrada", encoding='utf-8'))
print (b)
b=b.hexdigest()
print (b)
c="0057addd02516db3d258fd14c56bab49"==b
print(c)