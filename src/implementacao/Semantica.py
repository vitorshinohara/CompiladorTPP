# -*- coding: utf-8 -*-

from Sintatica import Parser

# [DONE] Criando tabela de símbolos
# [DONE] Verificando inicialização de variáveis antes de utilizar
# [DONE] Verificando variáveis nunca utilizadas
# [DONE] Verificando existência da função principal 
# [DONE] Verificando operador 'SE' 
# [DONE] Verificar operações entre variáveis de tipos diferentes
# [TO DO] Verificar retorno de função
# [TO DO] Verificar chamadas de funções inexistentes
# [TO DO] Recursão da função principal


class Function():
	"""Objeto Function"""

	def __init__(self, tipo, nome, parametros):
		self.tipo = tipo
		self.nome = nome
		self.parametros = parametros
		

class Node():
	"""Objeto Node -> compõe a tabela de"""

	def __init__(self, escopo, tipo, valor, estrutura):
		self.escopo = escopo 					# Escopo da função: <Global/Principal/bubble_sort>
		self.tipo = tipo 						# Tipo da variável <inteiro/flutuante>
		self.valor = valor 						# Nome da variável <i/j/tam/temp>
		self.estrutura = estrutura 				# <array/var>
		self.utilizada = 0 						# Flag de utilização da variável <0/1>


class Semantica():
	"""Analisador sintático"""

	def __init__(self, code):
		self.symbols = []
		self.funcs = []
		parser = Parser(code)
		self.criarSimb("global", parser.ast)
		self.verificarEstruturas("global", parser.ast) 				# Gera a tabela de símbolos
		self.genFunctionTable(parser.ast)						
		self.verificarPrincipal()								# Verifica se a função Principal foi declarada
		self.verificarUtilizacao()								# Verifica se as variáveis foram inicializadas e não utilizadas


	def searchSymbolsTable(self,var,escopo):
		for x in self.symbols:
			if str(x.valor) == str(var) and str(x.escopo) == str(escopo):
				x.utilizada = 1
				return str(x.tipo)

	def verificarPrincipal(self):
		flag = 0
		for function in self.funcs:
			if function.nome == "principal":
				flag = 1
		if flag == 0:
			print "ERRO: Função principal não declarada"

	def verificarUtilizacao(self):
		for simbolo in self.symbols:
			if simbolo.utilizada == 0:
				print "WARNING: Variável " + simbolo.valor + " declarada e não utilizada"

	def descerTree(self, node):
		while node is not None and len(node.child) == 1:
			node = node.child[0]
		return node

	def criarSimb(self, escopo, node):
		if node is not None:
			if node.type == "cabecalho":
				escopo = node.value

			elif node.type == "declaracao_variaveis":
				self.genSymbolsTable_add(escopo, node)

			for son in node.child:
				self.criarSimb(escopo, son)


	def verificarEstruturas(self, escopo, node): 					# Percorrer a árvore iterando sobre os nós
		if node is not None:
			#print "Nó atual: " + node.type
			if node.type == "cabecalho":
				escopo = node.value

			elif node.type == "se":
				self.condicional(node)

			elif node.type == "corpo":
				self.corpo(node, escopo)

			for son in node.child:
				self.verificarEstruturas(escopo, son)


	def corpo(self, node, escopo):
		tipos = []
		if len(node.child) < 2 or node.child[0] is None or node.child[1] is None:
			return False

		left = node.child[0]

		if left is None or len(left.child) == 0:
			return False

		y = self.descerTree(left.child[1])

		if y is None:
			return False

		if y.type == 'atribuicao':
			
			tipo = self.searchSymbolsTable(y.child[0].value, escopo) 		# Pega o tipo do símbolo que ta recebendo atribuição
			tipos.append(tipo)
			
			right = self.descerTree(y.child[1])

			if right.type == 'var':
				tipo = self.searchSymbolsTable(right.value, escopo)
				tipos.append(tipo)
			elif right.type == 'numero':
				tipo = self.getTypeNum(float(right.value))
				tipos.append(tipo)
			elif right.type == 'expressao_simples':
				tipo_expr = self.expressao_simples(y, escopo)
				tipos.append(tipo_expr)

			elif right.type == 'expressao_aditiva':
				tipo_expr = self.expressao_simples(y, escopo)
				tipos.append(tipo_expr)

			elif right.type == 'expressao_multiplicativa':
				tipo_expr = self.expressao_simples(y, escopo)
				tipos.append(tipo_expr)

			elif right.type == 'expressao_unaria':
				tipo_expr = self.expressao_unaria(y, escopo)
				tipos.append(tipo_expr)

			# Outros nós filhos do corpo

		for i in xrange(1,len(y.child)):
			y = self.descerTree(node.child[i])
				#if tipo is None:
				#		print "Erro semântico: Variavel " +  y.child[0].value + " sendo utilizada, porém não declarada"
			
			if y.type == 'var':
				tipo = self.searchSymbolsTable(folha.value, escopo)
				tipos.append(tipo)
			elif y.type == 'numero':
				tipo = self.getTypeNum(float(folha.value))
				tipos.append(tipo)

			if y.type == 'expressao_simples':
				tipo_expr = self.expressao_simples(y, escopo)
				tipos.append(tipo_expr)

			elif y.type == 'expressao_aditiva':
				tipo_expr = self.expressao_simples(y, escopo)
				tipos.append(tipo_expr)

			elif y.type == 'expressao_multiplicativa':
				tipo_expr = self.expressao_simples(y, escopo)
				tipos.append(tipo_expr)

			elif y.type == 'expressao_unaria':
				tipo_expr = self.expressao_unaria(y, escopo)
				tipos.append(tipo_expr)

		for i in xrange(0,len(tipos) - 1):
			if tipos[i] != tipos[i+1]:
				print "Erro: Operação com variáveis não permitidas. Tipo " + tipos[0] + " esperado"




	def genSymbolsTable_add(self, escopo, node): 				# Gera a tabela de símbolos
		estrutura = "var"
		tipo = node.child[0].type 								# Tipo da variável <inteiro/flutuante>
		var = node.child[1]
		value = var.child[0].value 								# Nome da variável <i/j/tam>

		if var.child[0].child != []:
			if node.child[1].child[0].child[0].type == "indice":
				estrutura = "array"
		no = Node(escopo, tipo, value, estrutura) 				# Cria o nó
		self.symbols.append(no)									# Adiciona o nó na tebela de símbolos


	def expressao_simples(self, node, escopo):
		if len(node.child) == 1:
			folha = self.descerTree(node)
			if folha.type == 'var':
				return self.searchSymbolsTable(folha.value, escopo)
			elif folha.type == 'numero':
				return self.getTypeNum(float(folha.value))
			elif folha.type == 'expressao_aditiva':
				return self.expressao_aditiva(folha, escopo)
			elif folha.type == 'expressao_multiplicativa':
				return self.expressao_multiplicativa(folha, escopo)
			elif folha.type == 'expressao_unaria':
				return self.expressao_unaria(folha, escopo)
		else:
			tipo1 = self.expressao_simples(node.child[0], escopo)
			tipo2 = self.expressao_aditiva(node.child[2], escopo)
			if tipo1 != tipo2:
				return False

			else:
				return tipo1



	def expressao_aditiva(self, node, escopo):
		if len(node.child) == 1:
			folha = self.descerTree(node)

			if folha.type == 'var':
				return self.searchSymbolsTable(folha.value, escopo)
			elif folha.type == 'numero':
				return self.getTypeNum(float(folha.value))
			elif folha.type == 'expressao_multiplicativa':
				return self.expressao_multiplicativa(folha, escopo)
			elif folha.type == 'expressao_unaria':
				return self.expressao_unaria(folha, escopo)

		else:
			tipo1 = self.expressao_aditiva(node.child[0], escopo)
			tipo2 = self.expressao_unaria(node.child[2], escopo)
			if tipo1 != tipo2:
				return False
			else:
				return tipo1


	def expressao_multiplicativa(self, node, escopo):
		if len(node.child) == 1:
			folha = self.descerTree(node)

			if folha.type == 'var':
				return self.searchSymbolsTable(folha.value, escopo)
			elif folha.type == 'numero':
				return self.getTypeNum(float(folha.value))
			elif folha.type == 'expressao_unaria':
				return self.expressao_unaria(folha, escopo)

		else:
			tipo1 = self.expressao_multiplicativa(node.child[0], escopo)
			tipo2 = self.expressao_unaria(node.child[2], escopo)

			if tipo1 != tipo2:
				return False
			else:
				return tipo1		

	def expressao_unaria(self, node, escopo):
		if len(node.child) == 1:
			folha = self.descerTree(node)

			if folha.type == 'var':
					return self.searchSymbolsTable(folha.value, escopo)
			elif folha.type == 'numero':
					return self.getTypeNum(float(folha.value))
		else:
			tipo1 = self.descerTree(node.child[1])
			if tipo1.type == 'var':
				return self.searchSymbolsTable(tipo1.value, escopo)
			elif tipo1.type == 'numero':
				return self.getTypeNum(float(tipo1.value))

			
	def condicional(self, node): # Verifica operadores de uma condicional
		node = node.child[0]
		var1 = None
		var2 = None
		if len(node.child) == 1:
			node = node.child[0]
			var1 = self.lastNode(node.child[0])
			var2 = self.lastNode(node.child[2])

		if var1.type == 'var':
			tipo1 = self.getTypeVar(var1)
		else:
			tipo1 = self.getTypeNum(float(var1.value))

		if var2.type == 'var':
			tipo2 = self.getTypeVar(var2)
		else:
			tipo2 = self.getTypeNum(float(var2.value))

		if tipo1 != tipo2:
			print "Erro: Expressão SE incorreta. Esperado dois tipos " + tipo1

		if node.child[1].type != 'operador_relacional':
			print "Erro: Expressão se esperando operador lógico"
			
	def lastNode(self, node):
		while len(node.child) == 1:
			node = node.child[0]
		return node


	def genFunctionTable(self, node):
		if node is not None:
			if node.type == "declaracao_funcao":

				if len(node.child) == 2: 						# Caso da funções com return
					func = Function(node.child[0].type, node.child[1].value, [])
				else: 											# Caso de funções void
					func = Function("void", node.child[0].value, [])
				
				self.funcs.append(func)							# Adiciona o obj func na lista de funções

			for son in node.child:
				self.genFunctionTable(son)


	### Helpers ###

	def getTypeVar(self, var):
		for node in self.symbols:
			if node.valor == var.value:
				return node.tipo

	def getTypeNum(self, num):
		if num % 1 == 0:
			return 'inteiro'
		else:
			return 'flutuante'

	### End Helpers ###


if __name__ == '__main__':
	from sys import argv
	
	try:
		f = open(argv[1])
		semantica = Semantica(f.read())
	except IOError:
		#raise Exception("Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto.")
		print "Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto."
