from os import listdir
from os.path import isfile, join
import os

onlyfiles = [f for f in listdir("/home/yudi/CompiladorTPP/src/implementacao/Testes/semantica-testes/") if isfile(join ("/home/yudi/CompiladorTPP/src/implementacao/Testes/semantica-testes/",f))]
file = open("SaidasSemanticas.txt","w")

for x in sorted(onlyfiles):
	if str(x) == "script.py" or str(x) == "SaidasSemanticas.txt":
		pass

	os.system("echo Executando: "+ str(x))
	os.system("python Semantica.py Testes/semantica-testes/" + str(x))
	os.system("echo \n")
