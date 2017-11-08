# -*- coding: utf-8 -*-

from Sintatica import Parser

class Node():
	"""docstring for Node"""

	def __init__(self, escopo, tipo, valor, estrutura, inicializada):
		self.escopo = escopo
		self.tipo = tipo
		self.valor = valor
		self.estrutura = estrutura
		self.inicializada = inicializada


class Semantica():
	"""Analisador sintático"""

	def __init__(self, code):
		self.symbols = []
		parser = Parser(code)
		self.genSymbolsTable("global", parser.ast)
		self.verificarInicializacao("global", parser.ast)
		#self.printarTabSimbolos()

	def printarTabSimbolos(self):
		print "---------------------------------------------------------"
		for x in self.symbols:
			print "Escopo: " + x.escopo + " Tipo: "+ x.tipo + " Valor: " + x.valor + " Estrutura: " + x.estrutura 


	def genSymbolsTable(self, escopo, node): # Percorrer a árvore iterando sobre os nós
		if node is not None:

			if node.type == "cabecalho":
				escopo = node.value

			elif node.type == "declaracao_variaveis":
				self.genSymbolsTable_add(escopo, node)
			
			for son in node.child:
				self.genSymbolsTable(escopo, son)

	def genSymbolsTable_add(self, escopo, node): # Gera a tabela de símbolos
		estrutura = "var"
		tipo = node.child[0].type # Tipo da variável <inteiro/flutuante>
		var = node.child[1]
		value = var.child[0].value # Nome da variável <i/j/tam>

		if var.child[0].child != []:
			if node.child[1].child[0].child[0].type == "indice":
				estrutura = "array"

		no = Node(escopo, tipo, value, estrutura, 1) # Cria o nó
		self.symbols.append(no)	# Adiciona o nó na tebela de símbolos
		#print "Escopo: " + escopo + " Tipo: "+ tipo + " Valor: " + value + " Estrutura: " + estrutura 


	def verificarInicializacao(self, escopo, node):
		if node is not None:
			variavel = ""
			if node.type == 'cabecalho': # Define o escopo da variável
				escopo = node.value

			elif node.type == "atribuicao":
				flag = 1
				valor = node.child[0].value

				for x in self.symbols:
					if x.valor == valor and (x.escopo == "global" or x.escopo == escopo):
						flag = 0

				if flag == 1:
					print "Erro semântico: Variavel "+  valor +" sendo utilizada, porém não inicializada"

			for son in node.child:
				self.verificarInicializacao(escopo, son)

if __name__ == '__main__':
	from sys import argv
	f = open(argv[1])
	semantica = Semantica(f.read())
