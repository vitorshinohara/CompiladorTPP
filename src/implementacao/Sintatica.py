# -*- coding: utf-8 -*-

import ply.yacc as yacc
from Lexica import Lexica
from graphviz import Digraph


class Tree:

	def __init__(self, type_node, child=[], value=''):
		self.type = type_node
		self.child = child
		self.value = value

	def __str__(self):
		return self.type

########################
# Analisador Sintático #
########################


class Parser:

	def __init__(self, code):
		lexica = Lexica()
		self.tokens = lexica.tokens
		self.precedence = (
			('left', 'IGUALDADE', 'NEGACAO', 'MAIORIGUAL', 'MAIOR', 'MENORIGUAL', 'MENOR'),
			('left', 'SOMA', 'SUBTRACAO'),
			('left', 'MULTIPLICACAO', 'DIVISAO'),
		)
		parser = yacc.yacc(debug=False, module=self, optimize=False)

		self.ast = parser.parse(code)


	def p_programa(self, p):
		'''
		programa : lista_declaracoes
						'''
		p[0] = Tree('programa', [p[1]])


	def p_lista_declaracoes(self, p):
		'''
		lista_declaracoes : lista_declaracoes declaracao
							| declaracao		
		'''
		if (len(p) == 3):
			p[0] = Tree('lista_declaracoes', [p[1], p[2]])

		elif(len(p) == 2):
			p[0] = Tree('lista_declaracoes', [p[1]])


	def p_declaracao(self, p):
		'''
		declaracao : declaracao_variaveis
					| inicializacao_variaveis
					| declaracao_funcao
		'''
		p[0] = Tree('declaracao', [p[1]])

	
	def p_declaracao_variaveis(self, p):
		'''
		declaracao_variaveis : tipo DOISPONTOS lista_variaveis 	
		'''
		p[0] = Tree('declaracao_variaveis', [p[1], p[3]], p[2])


	def p_inicializacao_variaveis(self, p):
		'''
		inicializacao_variaveis : atribuicao
		'''
		p[0] = Tree('inicializacao_variaveis', [p[1]])

	
	def p_lista_variaveis(self, p):
		'''
		lista_variaveis : lista_variaveis VIRGULA var
						| var
		'''
		if (len(p) == 4):
			p[0] = Tree('lista_variaveis', [p[1], p[3]])

		elif(len(p) == 2):
			p[0] = Tree('lista_variaveis', [p[1]])

	def p_var(self, p):
		'''
		var : IDENTIFICADOR
				| IDENTIFICADOR indice
		'''

		if (len(p) == 2):
			p[0] = Tree('var', [], p[1])

		elif(len(p) == 3):
			p[0] = Tree('var', [p[2]], p[1])

	def p_indice(self, p):
		'''
		indice : indice ABRECOL expressao FECHACOL
						| ABRECOL expressao FECHACOL
		'''
		if(len(p) == 5):
			p[0] = Tree('indice', [p[1], p[3]])
		elif(len(p) == 4):
			p[0] = Tree('indice', [p[2]])

	def p_tipo(self, p):
		'''
		tipo : INTEIRO
		'''
		p[0] = Tree('inteiro', [])

	def p_tipo2(self, p):
		'''
		tipo : FLUTUANTE
		'''

		p[0] = Tree('flutuante', [])

	def p_declaracao_funcao(self, p):
		'''
		declaracao_funcao : tipo cabecalho
						| cabecalho
		'''

		if len(p) == 3:
			p[0] = Tree('declaracao_funcao', [p[1], p[2]])
		elif len(p) == 2:
			p[0] = Tree('declaracao_funcao', [p[1]])

	

	def p_cabecalho(self, p):
		'''
		cabecalho : IDENTIFICADOR ABREPAR lista_parametros FECHAPAR corpo FIM
		'''

		p[0] = Tree('cabecalho', [p[3], p[5]], p[1])



	def p_lista_parametros(self, p):
		'''
		lista_parametros : lista_parametros VIRGULA lista_parametros
							| parametro
		'''

		if len(p) == 4:
			p[0] = Tree('lista_parametros', [p[1], p[3]])
		elif len(p) == 2:
			p[0] = Tree('lista_parametros', [p[1]])

	def p_lista_parametros2(self, p):
		'''
		lista_parametros :  vazio
		'''
		# None


	def p_parametro1(self, p):
		'''
		parametro : tipo DOISPONTOS IDENTIFICADOR
		'''

		p[0] = Tree('parametro', [p[1]], p[3])

	def p_parametro1_error(self, p):
		'''
		parametro : error DOISPONTOS IDENTIFICADOR
		'''
		raise SyntaxError("Erro de parâmetro \n")

	def p_parametro2(self, p):
		'''
		parametro : parametro ABRECOL FECHACOL
		'''
		p[0] = Tree('parametro', [p[1]])


	def p_corpo(self, p):
		'''
		corpo : corpo acao

		'''

		if len(p) == 3:
			p[0] = Tree('corpo', [p[1], p[2]])
		elif len(p) == 2:
			p[0] = Tree('corpo', [p[1]])


	def p_corpo2(self, p):
		'''
		corpo : vazio
		'''

	def p_acao(self, p):
		'''
		acao : expressao
			| declaracao_variaveis
			| se
			| repita
			| leia
			| escreva
			| retorna

		'''

		p[0] = Tree('acao', [p[1]])

	def p_se(self, p):
		'''
		se : SE expressao ENTAO corpo FIM
				| SE expressao ENTAO corpo SENAO corpo FIM
		'''

		if len(p) == 6:
			p[0] = Tree('se', [p[2], p[4]])
		elif len(p) == 8:
			p[0] = Tree('se', [p[2], p[4], p[6]])

	def p_repita(self, p):
		'''
		repita : REPITA corpo ATE expressao
		'''
		p[0] = Tree('repita', [p[2], p[4]])


	def p_atribuicao(self, p):
		'''
		atribuicao : var ATRIBUICAO expressao
		'''
		if len(p):
			p[0] = Tree('atribuicao', [p[1], p[3]], p[2])

	
	def p_leia(self, p):
		'''
		leia : LEIA ABREPAR IDENTIFICADOR FECHAPAR
		'''
		if len(p):
			p[0] = Tree('leia', [], p[3])



	def p_escreva(self, p):
		'''
		escreva : ESCREVA ABREPAR expressao FECHAPAR
		'''
		p[0] = Tree('escreva', [p[3]])



	def p_retorna(self, p):
		'''
		retorna : RETORNA ABREPAR expressao FECHAPAR
		'''
		p[0] = Tree('retorna', [p[3]])

	def p_expressao(self, p):
		'''
		expressao : expressao_simples
				| atribuicao
		'''
		p[0] = Tree('expressao', [p[1]])

	
	def p_expressao_simples(self, p):
		'''
		expressao_simples : expressao_aditiva
						| expressao_simples operador_relacional expressao_aditiva
		'''
		if len(p) == 2:
			p[0] = Tree('expressao_simples', [p[1]])
		elif len(p) == 4:
			p[0] = Tree('expressao_simples', [p[1], p[2], p[3]])


	def p_expressao_aditiva(self, p):
		'''
		expressao_aditiva : expressao_multiplicativa
						| expressao_aditiva operador_multiplicacao expressao_unaria
		'''
		if len(p) == 2:
			p[0] = Tree('expressao_aditiva', [p[1]])
		elif len(p) == 4:
			p[0] = Tree('expressao_aditiva', [p[1], p[2], p[3]])


	def p_expressao_multiplicativa(self, p):
		'''
		expressao_multiplicativa : expressao_unaria
								| expressao_aditiva operador_soma expressao_multiplicativa

		'''
		if len(p) == 2:
			p[0] = Tree('expressao_multiplicativa', [p[1]])
		elif len(p) == 4:
			p[0] = Tree('expressao_multiplicativa', [p[1], p[2], p[3]])


	def p_expressao_unaria(self, p):
		'''
		expressao_unaria : fator
						| operador_soma fator

		'''

		if len(p) == 2:
			p[0] = Tree('expressao_unaria', [p[1]])
		else:
			p[0] = Tree('expressao_unaria', [p[1], p[2]])


	def p_operador_relacional(self, p):
		'''
		operador_relacional : MENOR
							| MAIOR
							| IGUALDADE
							| MENORIGUAL
							| MAIORIGUAL
							| NEGACAO
							| OULOGICO
							| ELOGICO
		'''

		p[0] = Tree('operador_relacional', [], str(p[1]))

	def p_operador_soma(self, p):
		'''
		operador_soma : SOMA
						| SUBTRACAO
		'''
		p[0] = Tree('operador_soma', [], str(p[1]))

	def p_operador_multiplicacao(self, p):
		'''
		operador_multiplicacao : MULTIPLICACAO
								| DIVISAO
		'''
		p[0] = Tree('operador_multiplicacao', [], str(p[1]))

	def p_fator(self, p):
		'''
		fator : ABRECOL  expressao FECHACOL
				| var
				| chamada_funcao
				| numero
		'''
		if len(p) == 4:
			p[0] = Tree('fator', [p[2]])
		else:
			p[0] = Tree('fator', [p[1]])

	def p_numero(self, p):
		'''
		numero : INTEIRO
				| FLUTUANTE

		'''
		p[0] = Tree('numero', [], str(p[1]))

	def p_chamada_funcao(self, p):
		'''
		chamada_funcao : IDENTIFICADOR ABREPAR lista_argumentos FECHAPAR
		'''
		p[0] = Tree('chamada_funcao', [p[3]], p[1])

	def p_lista_argumentos(self, p):
		'''
		lista_argumentos : lista_argumentos VIRGULA expressao
						| expressao
		'''
		if len(p) == 4:
			p[0] = Tree('lista_argumentos', [p[1], p[3]])
		else:
			p[0] = Tree('lista_argumentos', [p[1]])

	def p_lista_argumentos2(self, p):
		'''
		lista_argumentos : vazio
		'''

	def p_vazio(self, p):
		'''
		vazio :
		'''
	
	#################################################################################################################
	############################################### Mensagens de erro ###############################################
	#################################################################################################################
	

	def p_lista_declaracoes_error(self, p):
		'''
		lista_declaracoes : error error
							| error

		'''
		raise SyntaxError("Erro de declaração \n")

	def p_declaracao_error(self, p):
		'''
		declaracao : error
		'''
		raise SyntaxError("Erro de declaração \n")

	def p_declaracao_variaveis_error(self, p):
		'''
		declaracao_variaveis : error DOISPONTOS error 	
		'''
		raise SyntaxError("Erro na declaração de variaveis \n")

	def p_inicializacao_variaveis_error(self, p):
		'''
		inicializacao_variaveis : error
		'''
		raise SyntaxError("Erro na inicialização de variaveis \n")

	def p_lista_variaveis_error(self, p):
		'''
		lista_variaveis : error VIRGULA error
						| error
		'''

		raise SyntaxError("Erro de variável \n")

	def p_var_error(self, p):
		'''
		var : IDENTIFICADOR error
		'''
		raise SyntaxError("Erro de variavel \n")

	def p_indice_error(self, p):
		'''
		indice : indice ABRECOL error FECHACOL
				| ABRECOL error FECHACOL
		'''
		raise SyntaxError("Erro sintático de indexação \n")

	def p_tipo_error(self, p):
		'''
		tipo : error
		'''
		raise SyntaxError("Erro de tipo de variável \n")

	def p_declaracao_funcao_error(self, p):
		'''
		declaracao_funcao : error error
							| error
		'''
		raise SyntaxError("Erro na declaração de função \n")

	def p_cabecalho_error(self, p):
		'''
		cabecalho : IDENTIFICADOR ABREPAR error FECHAPAR error FIM
		'''
		raise SyntaxError("Erro no cabeçalho \n")

	def p_lista_parametros_error(self, p):
		'''
		lista_parametros : error VIRGULA error
		'''

		raise SyntaxError("Erro de parâmetro \n")

	def p_corpo_error(self, p):
		'''
		corpo : error error
				| error
		'''

		raise SyntaxError("Erro de corpo de função \n")

	def p_acao_error(self, p):
		'''
		acao : error

		'''
		raise SyntaxError("Erro na ação \n")

	def p_se_error(self, p):
		'''
		se : SE error ENTAO error FIM
				| SE error ENTAO error SENAO error FIM
		'''
		raise SyntaxError("Erro na expressão se \n")

	def p_repita_error(self, p):
		'''
		repita : REPITA error ATE error
		'''
		raise SyntaxError("Erro na expressão repita \n")

	def p_atribuicao_error(self, p):
		'''
		atribuicao : error ATRIBUICAO error
		'''
		raise SyntaxError("Erro de atribuição \n")

	def p_leia_error(self, p):
		'''
		leia : error error error error
		'''
		raise SyntaxError("Erro na expressão LEIA \n")

	def p_escreva_error(self, p):
		'''
		escreva : ESCREVA ABREPAR error FECHAPAR
		'''
		raise SyntaxError("Erro na expressão ESCREVA \n")

	def p_retorna_error(self, p):
		'''
		retorna : RETORNA ABREPAR error FECHAPAR
		'''
		raise SyntaxError("Erro na expressão RETORNA \n")

	def p_expressao_error(self, p):
		'''
		expressao : error
		'''
		raise SyntaxError("Erro de expressão \n")

	def p_expressao_simples_error(self, p):
		'''
		expressao_simples : error
						| error error error				
		'''
		raise SyntaxError("Erro de expressão simples \n")

	def p_expressao_aditiva_error(self, p):
		'''
		expressao_aditiva : error
						| error error error
		'''
		raise SyntaxError("Erro de expressão aditiva \n")



	def p_error(self, p):
		if p:
			raise SyntaxError(" '%s', linha %d" % (p.value, p.lineno))
			# exit(1)
		else:
			raise SyntaxError(" definições incompletas!")
			#print('Erro sintático: definições incompletas!')
			exit(1)

	##############################################################################
	########################### FIM MSG DE ERRO ##################################
	##############################################################################

	def printar(self):
		self.g.view()



class Imprimir():
	def __init__(self):
		self.j = 1
		
	def mostra_tree(self,node,strson, father, w, i):
		if node != None :
			i = i + 1
			father = str(node) + " " + str(i-1)+ " " + str(self.j-1)
			for son in node.child:
				strson = str(son) + " " + str(i) + " " + str(self.j)
				w.edge(father, strson)
				self.j = self.j + 1
				self.mostra_tree(son, strson, father, w, i)




if __name__ == '__main__':
	from sys import argv, exit
	f = open(argv[1])
	try:
		arvore = Parser(f.read())
		w = Digraph('G', filename='Saidas/Saida.gv')
		tree = Imprimir().mostra_tree(arvore.ast,'','', w, i=0)
		
		w.view()

	except SyntaxError, e:
		print "SyntaxError: " + str(e)
		#raise SyntaxError(e)
	
	except IOError:
		print "Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto."
		#raise IOError("Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto.") 
