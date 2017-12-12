# -*- coding: utf-8 -*-
from sys import argv
from Semantica import Semantica
from llvmlite import ir


class GenCode(object):
	"""docstring for GenCode"""
	def __init__(self, code):
		self.semantica = Semantica(code)
		self.arvore = self.semantica.ast
		self.module = ir.Module('meu_modulo.bc')
		self.variaveis = []
		self.variaveisGlobais = []
		self.escopo = "global"
		self.iterar(self.arvore)
		self.funcllvm = ''

		arquivo = open('vars.ll', 'w')
		arquivo.write(str(self.module))
		arquivo.close()
		print(self.module)


	def iterar(self, node):
		if node != None:
			if node.type == 'declaracao_variaveis' and self.escopo == 'global':
				self.variavelGlobal(node)

			if node.type == 'declaracao_funcao':
				self.declaracao_funcao(node)

			for son in node.child:
				self.iterar(son)


	def declaracao_funcao(self,node): # Declaração de uma função

		self.variaveis = self.variaveisGlobais # Zera a tabela de variaveis da função, deixa só variraveis globais

		if len(node.child) > 1: # Função com retorno
			nome = node.child[1].value
			self.escopo = nome # Escopo recebe o nome da função
			tipo = node.child[0].type # Tipo da função <inteiro\float>

			if tipo == 'inteiro':
				# Cria um retorno de tipo inteiro
				t_func = ir.FunctionType(ir.IntType(32), ())
			else:
				# Cria um retorno de tipo float
				t_func = ir.FunctionType(ir.FloatType(), ())
		
		else:
			nome = node.child[0].value # Função void
			# Cria um retorno de tipo void
			t_func = ir.FunctionType(ir.VoidType(), ())

		# Cria a função
		func = ir.Function(self.module, t_func, nome)
		self.funcllvm = func
		# Cria o bloco de entrada e saida da função
		entryBlock = func.append_basic_block('entry' + nome)
		# Adiciona o bloco de entrada da função
		builder = ir.IRBuilder(entryBlock)
		# Itera sobre o corpo da função
		self.iterar_corpo(node, builder)
		# Adiciona o bloco de saida
		endBasicBlock = func.append_basic_block('exit' + nome)
		# Cria um salto para o bloco de saída
		builder.branch(endBasicBlock)
		# Adiciona bloco de saída no final da função
		builder.position_at_end(endBasicBlock)


	def variavelGlobal(self, node): # Define variáveis globais
		tipo = node.child[0].type   # Armazena o tipo da var
		nome = node.child[1].child[0].value # Armazena o nome
		if tipo == 'inteiro': # Declara caso seja inteiro
			globalVar = ir.GlobalVariable(self.module, ir.IntType(32), nome)
			# Reailiza inicialização da variavel global = 0
			globalVar.initializer = ir.Constant(ir.IntType(32), 0)
			# Define o linkage para common > variavel global
			globalVar.linkage = 'common'
			# Alinhamento
			globalVar.align = 4

		elif tipo == 'flutuante': # Declara caso seja flutuante
			globalVar = ir.GlobalVariable(self.module, ir.FloatType(), nome)
			# Reailiza inicialização da variavel global = 0
			globalVar.initializer = ir.Constant(ir.FloatType(), 0)
			# Define o linkage para common > variavel global
			globalVar.linkage = 'common'
			# Alinhamento
			globalVar.align = 4
		# Adiciona var global na lista de var globais
		self.variaveisGlobais.append(globalVar) # Adiciona var global na lista de var globais


	def iterar_corpo(self, node, builder): # Itera o corpo de uma função
		if node is not None:
			# Se o nó for do tipo declaracao_variaveis
			if node.type == 'declaracao_variaveis':
				# Função que aloca na memória as variaveis
				self.declaracao_variavel(node, builder)

			# Se o nó for do tipo atribuição
			if node.type == 'atribuicao':
				# Aloca variáveis na memória e faz atribuições
				self.atribuicao(node, builder)

			# Se o nó for do tipo se [DEVE SER TESTADO]
			if node.type == 'se':
				# Adiciona o se no código llvm
				self.se(node, builder)

			# Se o nó for do tipo repita [DEVE SER TESTADO]
			if node.type == 'repita':
				# Adiciona as operações para se realizar um loop
				self.repita(node, builder)

			for son in node.child:
				self.iterar_corpo(son, builder)



	def repita(self, node, builder):
		# Declara o bloco do predicado (verificação do laço)
		predicate = self.funcllvm.append_basic_block('predicate')
		# Declara o bloco do corpo
		body = self.funcllvm.append_basic_block('body')
		# Declara o bloco do fim do loop
		endloop = self.funcllvm.append_basic_block('endloop')
				
		# Salta para o bloco body
		builder.branch(body)
		# Coloca o bloco do corpo
		builder.position_at_end(body)

		# Itera dentro do corpo repita
		self.iterar_corpo(node, builder)
		# Salta para o bloco do predicado
		builder.branch(predicate)
		# Coloca o bloco do predicado
		builder.position_at_end(predicate)
		# Faz a comparação

		# Filho contém a expressão do predicado
		filho = node.child[1]
		
		# Obtem o array da expressao
		# Ex: [a,<,100]
		arr = self.expressao(filho, [])

		if len(arr) == 3:
			# Obtem a referencia da var
			var_cmp = self.searchVarTable(arr[0])
			var_cmp2 = self.searchVarTable(arr[2])
			# Aloca na memória
			var_cmp = self.genCodeTypes(var_cmp, builder)
			var_cmp2 = self.genCodeTypes(var_cmp2, builder)
			# Compara var_cmp e var_cmp2
			cmp = builder.icmp_unsigned(arr[1], var_cmp, var_cmp2, 'cmp')
			# Realiza o salto para determinado bloco
			builder.select(cmp, body, endloop)

		builder.position_at_end(endloop)
			

	def declaracao_variavel(self, node, builder):
		tipo = node.child[0].type
		self.lista_variaveis(node.child[1], tipo, builder)

	def lista_variaveis(self, node, tipo, builder):

		if len(node.child) == 2: # Verifica se é um vetor
			# if len(node.child[1].child) > 0:
				# if node.child[1].child[0].type == "indice":
					# estrutura = "array"
			
			# no = Node(escopo, tipo, node.child[1].value, estrutura)
			# self.lista_variaveis(node.child[0], tipo, builder)
			pass
		
		else:
			nome = node.child[0].value
			if tipo == 'inteiro':
				# Aloca uma variável inteira na memória
				var = builder.alloca(ir.IntType(32), name=nome)
				# Define o alinhamento dela
				var.align = 4
				# num0 = ir.Constant(ir.IntType(32),0)
				# builder.store(num0,var)
				self.variaveis.append(var)

			elif tipo == 'flutuante':
				# Aloca uma variável inteira na memória
				var = builder.alloca(ir.FloatType(), name=nome)
				# Define o alinhamento dela
				var.align = 4
				self.variaveis.append(var)


	def atribuicao(self, node, builder):
		arr = []
		var = node.child[0].value
		arr.append(var)


		if node.child[1].type == 'expressao':
			arr = self.expressao(node.child[1], arr)
		if node.child[1].type == 'expressao_simples':
			arr = self.expressao_simples(node.child[1], arr)
		if node.child[1].type == 'expressao_aditiva':
			arr = self.expressao_aditiva(node.child[1], arr)
		if node.child[1].type == 'expressao_multiplicativa':
			arr = self.expressao_multiplicativa(node.child[1], arr)
		if node.child[1].type == 'expressao_unaria':
			arr = self.expressao_unaria(node.child[1], arr)

		# Retorna um array de operalções [a,a,+,b] > a = a + b


		if len(arr) == 2:								# variavel = 1
			x = self.searchVarTable(arr[0])				# ^          ^
			builder.load(x, "")							# x         var
			arr.pop(0)
			var = self.searchVarTable(arr[0])
			var = self.genCodeTypes(var, builder)
			builder.store(var, x)


		elif len(arr) >= 3: # Se o vetor tiver 3 elementos (i+2)
			
			x = self.searchVarTable(arr[0]) # Procura pela variável a ser atribuida
			arr.pop(1)
			temp = self.resolverArray(builder, arr)
			
			builder.store(temp, x) # Armazena o resultado da operação no x
		


	def resolverArray(self, builder, arr):
		# Inicializa variável temporária
		temp = None
		if len(arr) >= 3:
			#  w + 1
			#    ^
			operador = arr[1]
			busca = self.searchVarTable(arr[0])
			if str(busca.type) == ('i32*'):
				#  w  +  1
				#  ^   	 ^
				# var1  var2
				var1 = self.searchVarTable(arr[0]) # Procura pela variável
				var2 = self.searchVarTable(arr[2])

				var1 = self.genCodeTypes(var1, builder) # Faz o load ou cria constante
				var2 = self.genCodeTypes(var2, builder)	# builder.load(var,'') ou ir.Constant

				if operador == '+':
					# Operação de soma
					temp = builder.add(var1, var2, name='tempadd', flags=())
				elif operador == '-':
					# Operação de subtração
					temp = builder.sub(var1, var2, name='tempsub', flags=())

				elif operador == '/':
					# Operação de divisão
					temp = builder.udiv(var1, var2, name='tempdiv', flags=())
				elif operador == '*':
					# Operação de multiplicação
					temp = builder.mul(var1, var2, name='tempmul', flags=())
				
				return temp

	def se(self, node, builder):

		# 2 SE expressao ENTÃO corpo
		#			^			^
		#			child[0]	child[1]

		# SE expressao ENTAO corpo SENAO corpo
		#		^				^			^
		#	child[0]		child[1]	child[2]

		arr = self.expressao(node.child[0], [])

		if len(node.child) == 2:
			
			predicate = self.funcllvm.append_basic_block('predicate')
			then = self.funcllvm.append_basic_block('then')
			merge = self.funcllvm.append_basic_block('merge')

			# Predicate block > verificacao condicao if
			builder.position_at_end(predicate)
			# Obtem a referencia da var
			var_cmp = self.searchVarTable(arr[0])
			var_cmp2 = self.searchVarTable(arr[2])
			# Aloca na memória
			var_cmp = self.genCodeTypes(var_cmp, builder)
			var_cmp2 = self.genCodeTypes(var_cmp2, builder)
			# Compara var_cmp e var_cmp2
			cmp = builder.icmp_unsigned( arr[1] ,var_cmp, var_cmp2, 'cmp')
			# Realiza o salto para determinado bloco
			builder.select(cmp, then, merge)

			# Bloco then
			builder.position_at_end(then)
			self.iterar_corpo(node.child[1], builder)
			builder.branch(merge)
			builder.position_at_end(merge)
		
		# SE expressao ENTAO corpo SENAO corpo
		#		^				^			^
		#	child[0]		child[1]	child[2]

		else: # 
			predicate = self.funcllvm.append_basic_block('predicate')
			then = self.funcllvm.append_basic_block('then')
			elsee = self.funcllvm.append_basic_block('else')
			merge = self.funcllvm.append_basic_block('merge')

			# Predicate block > verificacao condicao if
			builder.position_at_end(predicate)
			# Obtem a referencia da var
			var_cmp = self.searchVarTable(arr[0])
			var_cmp2 = self.searchVarTable(arr[0])
			# Aloca na memória
			var_cmp = self.genCodeTypes(var_cmp, builder)
			var_cmp2 = self.genCodeTypes(var_cmp2, builder)
			# Compara var_cmp e var_cmp2
			cmp = builder.icmp_unsigned( arr[1] ,var_cmp, var_cmp2, 'cmp')
			# Realiza o salto para determinado bloco
			builder.cbranch(cmp, then, elsee)

			# Bloco then
			builder.position_at_end(then)
			self.iterar_corpo(node.child[1], builder)
			builder.branch(merge)
			
			builder.position_at_end(elsee)
			self.iterar_corpo(node.child[2], builder)
			builder.branch(merge)

			# Fim do if
			builder.position_at_end(merge)		


	def searchVarTable(self, var): # Procura a variável na tabela ou faz conversões
		for x in self.variaveis:
			if x.name == str(var):
				return x

		try:
			var = int(var)
			return var
		except Exception as e:
			try:
				var = float(var)
				return var
			except Exception as e:
				pass

	def genCodeTypes(self, var, builder): # Faz o load ou cria constantes
		if type(var) == int:
			num = ir.Constant(ir.IntType(32), var)
			return num
		elif type(var) == float:
			num = ir.Constant(ir.FloatType(), var)
			return num
		else:
			load = builder.load(var, '')
			return load

	def stringToNumber(self, x):
		try:
			x = int(x)
			return x
		except Exception as e:
			try:
				x = float(x)
				return x
			except Exception as e:
				pass

	def getType(self, var):
		for x in self.variaveis:
			if var == x.name:
				return x.type
		


	def expressao(self, node, arr):
		if node.child[0].type == 'expressao_simples':
			self.expressao_simples(node.child[0], arr)
			return arr
		else:
			pass

	def expressao_simples(self, node, arr):
		if len(node.child) == 1:
			self.expressao_aditiva(node.child[0],arr)
			return arr
		else:
			arr = self.expressao_simples(node.child[0], arr)
			arr = self.operador_relacional(node.child[1], arr)
			arr = self.expressao_aditiva(node.child[2], arr)
			return arr

	def expressao_aditiva(self, node, arr):
		if len(node.child) == 1:
			self.expressao_multiplicativa(node.child[0], arr)
			return arr
		else:
			arr = self.expressao_aditiva(node.child[0], arr)
			arr  = self.operador_multiplicacao(node.child[1], arr)
			arr = self.expressao_unaria(node.child[2], arr)
			return arr


	def expressao_multiplicativa(self, node,arr):
		if len(node.child) == 1:
			arr = self.expressao_unaria(node.child[0], arr)			
			return arr
		else:
			arr = self.expressao_aditiva(node.child[0], arr)
			arr = self.operador_soma(node.child[1], arr)
			arr = self.expressao_multiplicativa(node.child[2], arr)
			return arr

	def expressao_unaria(self, node, arr):
		if len(node.child) == 1:
			arr = self.fator(node.child[0], arr)
			return arr
		else:
			arr = self.operador_soma(node.child[0], arr)
			arr = self.fator(node.child[1], arr)
			return arr
			
	def operador_relacional(self, node, arr):
		arr.append(node.value)
		return arr

	def operador_soma(self, node, arr):
		arr.append(node.value)
		return arr

	def operador_multiplicacao(self, node, arr):
		arr.append(node.value)
		return arr

	def fator(self,node, arr):
		if len(node.child) == 1:

			if node.child[0].type == 'var':
				arr.append(node.child[0].value)
			elif node.child[0].type == 'numero':
				arr.append(node.child[0].value)	
			return arr

if __name__ == '__main__':
	try:
		f = open(argv[1])
		genCode = GenCode(f.read())
	except IOError:
		# raise Exception("Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto.")
		print "Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto."
		


