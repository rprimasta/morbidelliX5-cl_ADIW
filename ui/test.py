data = []

print ("first :")

data.append([1,0])
data.append([2,0])
data.append([3,0])

def is_exist(data=[],val=0):
	exist = False
	for x in data:
		if(x[0] == val):
			print ("data sudah ada")
			exist = True
	return exist

print(is_exist(data,2))
	


print (data)
print (len(data))

del data[:]
print(is_exist(data,2))

print ("result :")
print (data)
print (len(data))


data.append(1)
data.append(2)
data.append(3)

print (data)
print (len(data))


