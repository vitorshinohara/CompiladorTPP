# -*- coding: utf-8 -*-

from Sintatica import Parser

# [DONE] Criando tabela de símbolos
# [DONE] Verificando inicialização de variáveis antes de utilizar
# [DONE] Verificando variáveis nunca utilizadas
# [DONE] Verificando existência da função principal
# [DONE] Verificando operador 'SE'
# [DONE] Verificar operações entre variáveis de tipos diferentes
# [DONE] Verificar retorno de Função
# [DONE] Obter argumentos de uma função
# [DONE] Validar argumentos de uma função
# [DONE] Verificar chamadas de funções inexistentes
# [DONE] Recursão da função principal
# [DONE] Verificar índices da função
# [TO DO] Verificar soma de estruturas diferentes (Vetor + variável)


class Function():
	"""Objeto Function"""
	def __init__(self, tipo, nome, parametros):
		self.tipo = tipo
		self.nome = nome
		self.parametros = parametros
		self.utilizada = 0 # Flag para ver se a função foi chamada no programa
		self.retorno = 0 # Flag para saber se a função foi chamada com os devidos argumentos
		
class Node():
	"""Objeto Node -> compõe a tabela de símbolos"""
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
		self.genFunctionTable(parser.ast)
		self.verificarEstruturas("global", parser.ast) 				# Gera a tabela de símbolos
		self.verificarPrincipal()								# Verifica se a função Principal foi declarada
		self.verificarUtilizacao()								# Verifica se as variáveis foram inicializadas e não utilizadas
		self.verificarRetornos()

## Início Geração da tabela de símbolos ##

	def criarSimb(self, escopo, node): # Gera a tabela de símbolos
		if node is not None:
			if node.type == "cabecalho": # Se o nó for um cabecalho, o escopo é o valor do nó
				escopo = node.value

			elif node.type == "declaracao_variaveis":
				self.genSymbolsTable_add(escopo, node) # Adiciona na tabela de símbolos

			for son in node.child:
				self.criarSimb(escopo, son)

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

## Fim funções Geração da tabela de símbolos ##


## Início função Geração da tabela de funções ##

	def genFunctionTable(self, node): # Monta a tabela de funções
		if node is not None:
			if node.type == "declaracao_funcao":
				args = []
				
				if len(node.child[0].child) > 0:
					if node.child[0].child[0] is not None:	
						if node.child[0].child[0].type == "lista_parametros": # Procura se a função tem uma lista de parâmetros
							args = self.lista_parametros(node.child[0].child[0], args) # Obtem a lista de tipos de parâmetro <inteiro/float>

				if len(node.child) == 2: 						# Caso da funções com return <inteiro nomedaFunc()>
					func = Function(node.child[0].type, node.child[1].value, args)
				else: 											# Caso de funções void <nomedaFunc()>
					func = Function("void", node.child[0].value, args)
				
				self.funcs.append(func)							# Adiciona o obj func na lista de funções

			for son in node.child:
				self.genFunctionTable(son)

## Fim função Geração da tabela de funções ##

## Início funções de verificação da estrutura ##

	def verificarEstruturas(self, escopo, node): # Percorrer a árvore iterando sobre os nós
		if node is not None:
			if node.type == "cabecalho": # Caso o nó for um cabecalho, armazenamos o escopo
				escopo = node.value
			elif node.type == "se": # Caso o nó for um 'se'
				self.condicional(node, escopo) # Verifica condicional
			elif node.type == "atribuicao": # Caso o nó for uma atribuição
				self.atribuicao(node, escopo) # Obtem tipos das variáveis na expressão e verifica
			elif node.type == "retorna": 
				self.retorna(escopo, node) # Verifica o retorno de uma função
			elif node.type == "chamada_funcao":
				self.chamada_funcao(node, escopo)

			elif node.type == "var":
				if len(node.child) > 0:
					self.verificarIndiceVetor(node, escopo)

			for son in node.child:
				self.verificarEstruturas(escopo, son)

	def condicional(self, node, escopo): # Verifica operadores de uma condicional
		node = node.child[0]
		var1 = None
		var2 = None
		if len(node.child) == 1:
			node = node.child[0]
			var1 = self.descerTree(node.child[0])
			var2 = self.descerTree(node.child[2])

		if var1.type == 'var':
			tipo1 = self.searchSymbolsTable(var1.value, escopo)
		else:
			tipo1 = self.getTypeNum(float(var1.value))
		if var2.type == 'var':
			tipo2 = self.searchSymbolsTable(var2.value, escopo)
		else:
			tipo2 = self.getTypeNum(float(var2.value))
		if tipo1 != tipo2:
			print "Erro: Expressão SE incorreta. Esperado dois tipos " + tipo1
		if node.child[1].type != 'operador_relacional':
			print "Erro: Expressão se esperando operador lógico"
	# End função Se

	# Inicio função corpo
	def atribuicao(self, node, escopo):
		tipos = []

		leftVar = node.child[0]
		leftType = self.searchSymbolsTable(leftVar.value, escopo)
		tipos.append(leftType)

		right = self.descerTree(node.child[1])
		if right.type == 'var':
			tipo = self.searchSymbolsTable(right.value, escopo)			
			if tipo is None:
				print "Erro semântico: Variavel " +  right.child[0].value + " sendo utilizada, porém não declarada"
			else: tipos.append(tipo)

		elif right.type == 'numero':
			tipo = self.getTypeNum(float(right.value))
			tipos.append(tipo)
	
		if right.type == 'expressao_simples':
			tipo_expr = self.expressao_simples(right, escopo)
			tipos.append(tipo_expr)
	
		elif right.type == 'expressao_aditiva':
			tipo_expr = self.expressao_aditiva(right, escopo)
			tipos.append(tipo_expr)

		elif right.type == 'expressao_multiplicativa':
			tipo_expr = self.expressao_multiplicativa(right, escopo)
			tipos.append(tipo_expr)

		elif right.type == 'expressao_unaria':
			tipo_expr = self.expressao_unaria(right, escopo)
			tipos.append(tipo_expr)
	
		for i in range(0, len(tipos)):
			if tipos[0] != tipos[i]:
				if tipos[0] == False or tipos[0] is None:
					aux = tipos[i]
				else:
					aux = tipos[0]

				print "ERRO: Variáveis de tipos incompatíveis. Esperado tipo " + str(aux)

				break
	
	# Inicio função expressao_simples
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
				return False # Caso os tipos forem diferentes, retorna False
			else:
				return tipo1 # Retorna o tipo da variável em uma expressao simples

	# End função expressao_simples

	# Inicio função expressao_aditiva
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
	# Fim função expressao_aditiva

	# Inicio função expressao_multiplicativa
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
			tipo1 = self.expressao_aditiva(node.child[0], escopo)
			tipo2 = self.expressao_multiplicativa(node.child[2], escopo)

			if tipo1 != tipo2:
				return False
			else:
				return tipo1

	# Fim função expressao_multiplicativa


	# Inicio função expressao_unaria
	def expressao_unaria(self, node, escopo):
		if len(node.child) == 1:
			folha = self.descerTree(node)

			if folha.type == 'var':
					return self.searchSymbolsTable(folha.value, escopo)
			elif folha.type == 'numero':
					return self.getTypeNum(float(folha.value))
		else:
			tipo1 = self.descerTree(node.child[0])
			if tipo1.type == 'var':
				return self.searchSymbolsTable(tipo1.value, escopo)
			elif tipo1.type == 'numero':
				return self.getTypeNum(float(tipo1.value))
	# End função expressao_unaria

	# Inicio função verificarPrincipal
	def verificarPrincipal(self):
		flag = 0
		for function in self.funcs:
			if function.nome == "principal":
				flag = 1
		if flag == 0:
			print "ERRO: Função principal não declarada"
	# End função verificarPrincipal

	# Inicio função verificarUtilizacao
	def verificarUtilizacao(self):
		for simbolo in self.symbols:
			if simbolo.utilizada == 0:
				print "WARNING: Variável " + simbolo.valor + " declarada e não utilizada"
	# End função verificarUtilizacao

	def verificarRetornos(self):
		for function in self.funcs:
			if function.retorno == 0 and function.tipo != "void":
				print "ERRO: Função " + function.nome + " sem retorno. Esperado retornar " + function.tipo

	def searchSymbolsTable(self, var, escopo):
		for x in self.symbols:
			if str(x.valor) == str(var) and ( str(x.escopo) == str(escopo) or str(x.escopo) == "global" ):
				x.utilizada = 1
				return str(x.tipo)
		
		print "ERRO: Variável " + var + " sendo utilizada sem ser declarada."
		return False
	
	def retorna(self, escopo, node):
		y = self.descerTree(node) # Desce até uma bifurcação ou var / numero
		# Armazena o tipo da variavel da folha para a variavel tipo
		tipo = ''
		if y.type == "var":
			tipo = self.searchSymbolsTable(y.value, escopo)
		elif y.type == "numero":
			tipo = self.getTypeNum(float(y.value))
		elif y.type == "expressao_simples":
			tipo = self.expressao_simples
		elif y.type == "expressao_aditiva":
			tipo = self.expressao_aditiva
		elif y.type == "expressao_multiplicativa":
			tipo = self.expressao_multiplicativa
		elif y.type == "expressao_unaria":
			tipo = self.expressao_unaria

		for function in self.funcs:
			if function.tipo != tipo and function.nome == escopo: # Se o tipo da função é diferente do tipo retornado
				print "ERRO: Retorno da função " + escopo + " incorreto . Tipo " + function.tipo + " esperado"
				break
			if function.tipo == tipo and function.nome == escopo:
				function.retorno = 1
				break

	def chamada_funcao(self, node, escopo):

		if node.value == "principal" and escopo == "principal":
			print "ERRO: Recursão na função principal."
			return False

		for i in self.funcs: # Percorre a tabela de funções
			if i.nome == node.value:  # Se a função estiver na tabela de funções
				i.utilizada = 1 # Seta a função como utilizada
				args = self.args_chamadaFunc(node.child[0], [], escopo)

				if args is not None:
					if len(args) != len(i.parametros) :
						print "ERRO: " + str( len(i.parametros) ) + " esperados para a função " + i.nome + ". " + str(len(args)) + " passados"
						return False
					else:
						for j in range(0,len(args)):
							if args[j] != i.parametros[j]:
								print "ERRO: Tipos incompatíveis. Argumento " + str(j+1) + " deve ser um " + str(i.parametros[j]) + ". Função " + str(i.nome)
								return False
						return True


		print "ERRO: Função " + node.value + " sendo chamada sem ser declarada "


	def args_chamadaFunc(self, node, args, escopo):
		if node is None:
			return args

		if len(node.child) == 1:
			if node.child[0] is not None:
				folha = self.descerTree(node.child[0])
				
				if folha.type == "var":
					tipo = self.searchSymbolsTable(folha.value, escopo)

					if tipo is not None:
						return tipo		

				elif folha.type == "numero":
					tipo = self.getTypeNum(float(folha.value))
					return tipo
					
		else:
			for son in node.child:
				tipo = self.args_chamadaFunc(son, args, escopo)
				if tipo == 'inteiro' or tipo == 'flutuante':
					args.append(tipo)

			return args

			
	def lista_parametros(self, node, args): # Obtem os parâmetros de uma função
		for no in node.child:
			y = self.descerTree(no)
			if y.type != "lista_parametros":
				args.append(y.type)
			else:
				args = self.lista_parametros(y, args)
		return args # Retorna um vetor de tipos

	### Helpers ###

	def getTypeVar(self, var):
		for node in self.symbols:
			if node.valor == var.value:
				return node.tipo
		print "Erro: Variável " + var.value + " sendo utilizada sem ser declarada"

	def getTypeNum(self, num):
		if num % 1 == 0:
			return 'inteiro'
		else:
			return 'flutuante'

	def descerTree(self, node):
		while node is not None and len(node.child) == 1 and node.type != "var":
			node = node.child[0]
		return node
	
	
	def verificarIndiceVetor(self, node, escopo):
		y = self.descerTree(node.child[0])
		
		tipo = ""

		if y.type == "var":
			tipo = self.searchSymbolsTable(y.value, escopo)
		elif y.type == "numero":
			tipo = self.getTypeNum(float(y.value))
		elif y.type == "expressao_simples":
			tipo = self.expressao_simples(y, escopo)
		elif y.type == "expressao_aditiva":
			tipo = self.expressao_aditiva(y, escopo)
		elif y.type == "expressao_multiplicativa":
			tipo = self.expressao_multiplicativa(y, escopo)
		elif y.type == "expressao_unaria":
			tipo = self.expressao_unaria(y, escopo)

		if tipo == "flutuante":
			print "ERRO: Índice do vetor "+ node.value +" deve ser do tipo inteiro."



	### End Helpers ###


if __name__ == '__main__':
	from sys import argv
	
	try:
		f = open(argv[1])
		semantica = Semantica(f.read())
	except IOError:
		#raise Exception("Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto.")
		print "Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto."