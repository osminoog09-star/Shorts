import base64,sys
with open(sys.argv[1],'rb') as f:
 f.seek(int(sys.argv[2]));b=f.read(int(sys.argv[3]))
print(base64.b64encode(b).decode('ascii'))
