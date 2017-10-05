# -*- coding: utf-8 -*-

import ply.yacc as yacc
import sys
import Lexica as Lexica


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
class Sintatica:

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

	def p_programa(p):
	 	'''
	 	programa : lista_declaracoes
	 	'''
	 	p[0] = Tree('programa',[p[1]])

	def p_lista_declaracoes(p):
	 	'''
	 	lista_declaracoes : lista_declaracoes declaracao
	 						| declaracao		
	 	'''
	 	if (len(p) == 3):
	 		p[0] = Tree('lista_declaracoes',[p[1], p[2]])
	 	elif(len(p) == 2):
	 		p[0] = Tree('lista_declaracoes',[p[1]])

	def p_declaracao(p):
	 	'''
	 	declaracao : declaracao_variaveis
	 				| inicializacao_variaveis
					| declaracao_funcao
	 	'''
	 	p[0] = Tree('declaracao', [p[1]])

	def p_declaracao_variaveis(p):
	 	'''
		declaracao_variaveis : tipo ":" lista_variaveis 	
	 	'''
	 	p[0] = Tree('declaracao_variaveis',[p[1], p[3]], p[2])

	def p_inicializacao_variaveis(p):
	 	'''
	 	inicializacao_variaveis : atribuicao
	 	'''
	 	p[0] = Tree('inicializacao_variaveis', [p[1]])

	def p_lista_variaveis(p):
	 	'''
	 	lista_variaveis : lista_variaveis "," var
	 	 	 	 		| var
		'''
		if (len(p) == 4):
			p[0] = Tree('lista_variaveis',[p[1], p[3]])
		elif(len(p) == 2):
			p[0] = Tree('lista_variaveis',[p[1]])

	def p_var(p):
	 	'''
	    var : IDENTIFICADOR
	    	| IDENTIFICADOR indice
	    '''
	    if (len(p) == 2):
	    	p[0] = Tree('var', [], p[1])
	    elif(len(p) == 3):
	    	p[0] = Tree('var', [p[2]], p[1])


	def p_indice(p):
	 	'''
	 	indice : indice ABRECOL expressao FECHACOL
	 			| ABRECOL expressao FECHACOL
	 	'''
	 	if(len(p) == 5):
	 		p[0] = Tree('indice', [p[1], p[3]])
	 	elif(len(p) == 4):
	 		p[0] == Tree('indice',[p[2]])

	def p_tipo(p):
	 	'''
	 	tipo : inteiro
	 		| flutuante
	 	'''
