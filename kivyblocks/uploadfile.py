import requests

url = "http://localhost:8080/uploadfile.dspy"

files = {
	"afile":("uploadfile.py",open("uploadfile.py","rb"),"application/python")
}

r = requests.post(url,files=files)
print(r.text)
