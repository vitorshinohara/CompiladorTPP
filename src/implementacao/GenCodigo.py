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
		self.funcs = []
		self.iterar(self.arvore)
		self.funcllvm = ''
		self.endBlock = ''
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
		# Verifica por argumentos da função

		self.variaveis = self.variaveisGlobais # Zera a tabela de variaveis da função, deixa só variraveis globais
		args = []
		nomes = []
		if len(node.child) > 1: # Função com retorno
			nome = node.child[1].value
			self.escopo = nome # Escopo recebe o nome da função
			if node.child[1].child[0] is not None:
				# Passa o nó da lista de argumentos
				args = self.getArgsFunc(node.child[1].child[0], [])
				nomes = self.getArgsFuncName(node.child[1].child[0], [])
			tipo = node.child[0].type # Tipo da função <inteiro\float>

			if tipo == 'inteiro':
				# Cria um retorno de tipo inteiro
				t_func = ir.FunctionType(ir.IntType(32), (args))
			else:
				# Cria um retorno de tipo float
				t_func = ir.FunctionType(ir.FloatType(), (args))
		
		else:
			nome = node.child[0].value # Função void
			self.escopo = nome

			# Verifica se existe argumentos na função
			if node.child[0].child[0] is not None:
				# Obtem os argumentos
				args = self.getArgsFunc(node.child[0].child[0], [])
				nomes = self.getArgsFuncName(node.child[0].child[0], [])
			# Cria um retorno de tipo void
			t_func = ir.FunctionType(ir.VoidType(), (args))

		# Cria a função
		func = ir.Function(self.module, t_func, nome)
		# Adiciona a função na lista de funções llvm
		self.funcs.append(func)
		# Obtem os argumentos da função
		argumentos_llvm = func.args

		# Define qual função o código vai utilizar na iteração do corpo
		self.funcllvm = func
		# Cria o bloco de entrada e saida da função
		entryBlock = func.append_basic_block('entry' + nome)
		# Adiciona o bloco de entrada da função
		builder = ir.IRBuilder(entryBlock)
		# Percorre a lista de parâmetros do tipo args llvm
		for x in range(0,len(argumentos_llvm)):
			# Se o argumento for do tipo inteiro
			if str(argumentos_llvm[x].type) == 'i32':
				#  Aloca a variável inteira com o nome do argumento referente ao mesmo
				var = builder.alloca(ir.IntType(32), name=str(nomes[x]))
				var.align = 4
				self.variaveis.append(var)

			# Se o argumento for do tipo flutuante
			elif str(argumentos_llvm[x].type) == 'float':
				#  Aloca a variável float com o nome do argumento referente ao mesmo
				var = builder.alloca(ir.FloatType(), name=str(nomes[x]))
				var.align = 4
				self.variaveis.append(var)
		
		# Adiciona o bloco de saida
		# Itera sobre o corpo da função
		self.iterar_corpo(node, builder)
		# Depois de iterar e adicionar todas estruturas, adiciona o return
		endBasicBlock = func.append_basic_block('exit' + nome)
		self.endBlock = endBasicBlock
		self.retorna(node, builder)
		
	def getArgsFunc(self, node, args):
		# Recursão para os filhos
		if len(node.child) > 1:
			for son in node.child:
				args = self.getArgsFunc(son, args)
				
		else:
			tipo = node.child[0].child[0].type
			if tipo == 'inteiro':
				args.append(ir.IntType(32))
			elif tipo == 'flutuante':
				args.append(ir.FloatType())
		return args

	def getArgsFuncName(self, node, args):
		aux = []
		if len(node.child) > 1:
			for son in node.child:
				args = self.getArgsFuncName(son, args)
			return args
				
		else:
			if node.type == 'lista_parametros':
				args.append(node.child[0].value)
				return args

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

			if node.type == 'chamada_funcao':
				self.chamada_funcao(node, builder)

			if node.type == 'escreva':
				self.escreva(node, builder) # Função escreva

			if node.type == 'leia':
				self.leia(node, builder)

			else:
				for son in node.child:
					self.iterar_corpo(son, builder)

	def retorna(self, node, builder):
		if node is not None:
			pass
			if node.type == 'retorna':

				if node.child[0].type == 'expressao':
					arr = self.expressao(node.child[0], [])
					if len(arr) == 1:
						var = self.searchVarTable(arr[0])
						print type(var)
						if type(var) == int or type(var) == float:
							var = self.genCodeTypes(var, builder)

						builder.branch(self.endBlock)
						builder.position_at_end(self.endBlock)
						builder.ret(var)
					elif len(arr) == 3:
						var = self.resolverArray(arr)
						builder.branch(self.endBlock)
						builder.position_at_end(self.endBlock)
						builder.ret(var)
			else:
				for son in node.child:
					self.retorna(son, builder)

	def leia(self, node, builder):
		try:
			# Ler inteiro
			args_int = [ir.PointerType(ir.IntType(32), 0)]
			leia_int_t = ir.FunctionType(ir.IntType(32), args_int)
			leia_int = ir.Function(self.module, leia_int_t, 'leia_int')
			self.funcs.append(leia_int)

			# Ler flutuante
			args_float = [ir.PointerType(ir.FloatType(), 0)]

			leia_float_t = ir.FunctionType(ir.FloatType(), args_float)
			leia_float = ir.Function(self.module, leia_float_t, 'leia_float')
			self.funcs.append(leia_float)

		# Caso as funções leia já foram declaradas, faz a chamada das mesmas
		except Exception as e:
			pass

		var = self.searchVarTable(node.value)
		args = []
		args.append(var)

		if str(var.type) == 'i32*':

			# Se o parâmetro passado é inteiro chama a função leia_int
			builder.call(self.searchFunc('leia_int'), args)

		elif var.type == 'float':
			builder.call(self.searchFunc('leia_float'), args)

		else:
			print 'erro'

	def escreva(self, node, builder):
		# Tenta criar uma função com nome repita
		try:
			# Define o argumento da função como um ponteiro
			args = [ir.PointerType(ir.IntType(8), 0)]
			# Cria a função printf
			func_t = ir.FunctionType(ir.IntType(32), args, True)
			func = ir.Function(self.module, func_t, 'printf')
		
		except Exception:
			# Se já existe, não faz nada
			pass
		#expressao = self.expressao(node.child[0], [])
		
		# LLVMValueRef formatint = LLVMBuildGlobalStringPtr(
        # builder,
        # "%d\n",
        # "formatint"
  		# );

		#arg = expressao[0]
		#vet = []
		#var = self.searchVarTable(arg)
		#print type(var)

		#if type(var) == int:
		# 	aux = ir.Constant(ir.IntType(32), var)
		# 	vet.append(aux)
		#if type(var) == float: 
		# 	aux = ir.Constant(ir.FloatType(), var)
		# 	vet.append(aux)
		# 	print 'aa'
		#print vet
		#print "ue"
		#builder.call(func, vet, 'escreva')

	def chamada_funcao(self, node, builder):
		if node.child[0] is None:
			# Faz a chamada da função sem argumentos
			builder.call(self.searchFunc(node.value), (), node.value)
			# IRBuilder.call(fn, args, name='')
			#				 ^	  ^		^
			#	function name     args  nome

		else:
			# Função com argumentos
			if node.child[0] is not None:
				args_str = []
				args_str = self.lista_argumentos(node.child[0], [])

			args_llvm = []
			
			for arg in args_str:
				# Transforma os argumentos searchVarTablestr em llvm
				args_llvm.append(builder.load(self.searchVarTable(arg), "temp_" + arg))
			# Faz a chamada da função, passa os argumentos e define o nome	
			builder.call(self.searchFunc(node.value), args_llvm, node.value)

	def lista_argumentos(self, node, arr):
		if len(node.child) > 1:
			for son in node.child:
				arr = self.lista_argumentos(son, arr)
			return arr

		else:
			aux = []
			if node.type == 'lista_argumentos':
				aux = self.expressao(node.child[0], aux)

			elif node.type == 'expressao':
				aux = self.expressao(node, aux)

			for x in aux:
				arr.append(x)
			return arr

	def repita(self, node, builder):
		# Declara o bloco do predicado (verificação do laço)
		predicate = self.funcllvm.append_basic_block('predicate_repita')
		# Declara o bloco do corpo
		body = self.funcllvm.append_basic_block('body_repita')
		# Declara o bloco do fim do loop
		endloop = self.funcllvm.append_basic_block('endloop')
				
		# Salta para o bloco body
		builder.branch(body)
		# Coloca o bloco do corpo
		builder.position_at_end(body)

		# Itera dentro do corpo repita
		self.iterar_corpo(node.child[0], builder)
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
			if arr[1] == '=':
				arr[1] = '=='

			cmp = builder.icmp_unsigned(arr[1], var_cmp, var_cmp2, 'cmp')

			# Realiza o salto para determinado bloco
			builder.cbranch(cmp, body, endloop)

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
			arr.pop(0)									# x         var
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
			
			else:
				#  w  +  1
				#  ^   	 ^
				# var1  var2
				var1 = self.searchVarTable(arr[0]) # Procura pela variável
				var2 = self.searchVarTable(arr[2])

				var1 = self.genCodeTypes(var1, builder) # Faz o load ou cria constante
				var2 = self.genCodeTypes(var2, builder)	# builder.load(var,'') ou ir.Constant

				if operador == '+':
					# Operação de soma
					temp = builder.fadd(var1, var2, name='tempadd', flags=())
				elif operador == '-':
					# Operação de subtração
					temp = builder.fsub(var1, var2, name='tempsub', flags=())

				elif operador == '/':
					# Operação de divisão
					temp = builder.fdiv(var1, var2, name='tempdiv', flags=())
				elif operador == '*':
					# Operação de multiplicação
					temp = builder.fmul(var1, var2, name='tempmul', flags=())
				
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
			
			predicate = self.funcllvm.append_basic_block('predicate_se')
			then = self.funcllvm.append_basic_block('then_se')
			merge = self.funcllvm.append_basic_block('merge_se')

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
			predicate = self.funcllvm.append_basic_block('predicate_se')
			then = self.funcllvm.append_basic_block('then_se')
			elsee = self.funcllvm.append_basic_block('else_se')
			merge = self.funcllvm.append_basic_block('merge_se')

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

	def searchFunc(self, nome):
		for function in self.funcs:
			if function.name == nome:
				return function

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
				return arr
			elif node.child[0].type == 'numero':
				arr.append(node.child[0].value)	
				return arr
			# elif node.child[0].type == 'chamada_funcao':
			# 	self.chamada_funcao(node.child[0])
			# 	return arr

if __name__ == '__main__':
	try:
		f = open(argv[1])
		genCode = GenCode(f.read())
	except IOError:
		# raise Exception("Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto.")
		print "Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto."
		


