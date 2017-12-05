# -*- coding: utf-8 -*-
from sys import argv, exit
from Semantica import Semantica
from llvmlite import ir


class GenCode(object):
	"""docstring for GenCode"""
	def __init__(self, code):
		self.semantica = Semantica(code)
		self.arvore = self.semantica.ast
		self.module = ir.Module('meu_modulo.bc')

		self.iterar(self.arvore)

		arquivo = open('vars.ll', 'w')
		arquivo.write(str(self.module))
		arquivo.close()
		print(self.module)



	def iterar(self, node):
		if node != None:
			if node.type == 'declaracao_funcao':
				self.declaracao_funcao(node)

			for son in node.child:
				self.iterar(son)


	def declaracao_funcao(self,node):

		if len(node.child) > 1:
			nome = node.child[1].value
			tipo = node.child[0].type

			if tipo == 'inteiro':
				# Cria um retorno de tipo inteiro
				t_func = ir.FunctionType(ir.IntType(32), ())
			else:
				# Cria um retorno de tipo float
				t_func = ir.FunctionType(ir.FloatType(), ())
		
		else:
			nome = node.child[0].value
			# Cria um retorno de tipo void
			t_func = ir.FunctionType(ir.VoidType(), ())

		# Cria a função
		func = ir.Function(self.module, t_func, nome) 
		# Cria o bloco de entrada e saida da função
		entryBlock = func.append_basic_block('entry'+nome)
		endBasicBlock = func.append_basic_block('exit'+nome)
		# Adiciona o bloco de entrada da função
		builder = ir.IRBuilder(entryBlock)

		self.iterar_corpo(node, builder)

		# Adiciona o bloco de saida
		builder.position_at_end(endBasicBlock)


	def iterar_corpo(self, node, builder):
		if node != None:
			if node.type == 'declaracao_variaveis':
				self.declaracao_variavel(node, builder)

			if node.type == 'atribuicao':
				self.atribuicao(node, builder)

			for son in node.child:
				self.iterar_corpo(son, builder)


	def declaracao_variavel(self, node, builder):
		tipo = node.child[0].type
		self.lista_variaveis(node.child[1], tipo, builder)

	def lista_variaveis(self, node, tipo, builder):

		if len(node.child) == 2: # Verifica se é um vetor
			if len(node.child[1].child) > 0:
				if node.child[1].child[0].type == "indice":
					estrutura = "array"				

			#no = Node(escopo, tipo, node.child[1].value, estrutura)

				
			self.lista_variaveis(node.child[0], tipo, builder)
		
		else:
			nome = node.child[0].value

			if tipo == 'inteiro':
				# Aloca uma variável inteira na memória
				var = builder.alloca(ir.IntType(32), name=nome)
				# Define o alinhamento dela
				var.align = 4
				#num0 = ir.Constant(ir.IntType(32),0)
				#builder.store(num0,var)

			elif tipo == 'flutuante':
				# Aloca uma variável inteira na memória
				var = builder.alloca(ir.FloatType(), name=nome)
				# Define o alinhamento dela
				var.align = 4
				#num0 = ir.Constant(ir.FloatType(),0)
				#builder.store(num0,var)
				
			return

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

		print arr
		print "---------"


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
		#raise Exception("Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto.")
		print "Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto."
		


