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

	def p_programa(self, p):
	 	'''
	 	programa : lista_declaracoes
	 	'''
	 	p[0] = Tree('programa',[p[1]])

	def p_lista_declaracoes(self, p):
	 	'''
	 	lista_declaracoes : lista_declaracoes declaracao
	 						| declaracao		
	 	'''
	 	if (len(p) == 3):
	 		p[0] = Tree('lista_declaracoes',[p[1], p[2]])
	 	elif(len(p) == 2):
	 		p[0] = Tree('lista_declaracoes',[p[1]])

	def p_declaracao(self, p):
	 	'''
	 	declaracao : declaracao_variaveis
	 				| inicializacao_variaveis
					| declaracao_funcao
	 	'''
	 	p[0] = Tree('declaracao', [p[1]])

	def p_declaracao_variaveis(self, p):
	 	'''
		declaracao_variaveis : tipo ":" lista_variaveis 	
	 	'''
	 	p[0] = Tree('declaracao_variaveis',[p[1], p[3]], p[2])

	def p_inicializacao_variaveis(self, p):
	 	'''
	 	inicializacao_variaveis : atribuicao
	 	'''
	 	p[0] = Tree('inicializacao_variaveis', [p[1]])

	def p_lista_variaveis(self, p):
	 	'''
	 	lista_variaveis : lista_variaveis "," var
	 	 	 	 		| var
		'''
		if (len(p) == 4):
			p[0] = Tree('lista_variaveis',[p[1], p[3]])
		elif(len(p) == 2):
			p[0] = Tree('lista_variaveis',[p[1]])

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
	 		p[0] = Tree('indice',[p[2]])

	def p_tipo(self, p):
	 	'''
	 	tipo : inteiro
	 		| flutuante
	 	'''
	 	p[0] = Tree('tipo', [p[1]])

	 def p_declaracao_funcao(self, p):
	 	'''
	 	declaracao_funcao : tipo cabecalho
	 						| cabecalho
	 	'''
	 	if len(p) == 3:
	 		p[0] = Tree('declaracao_funcao', [p[1],p[2]])
	 	elif len(p) == 2:
	 		p[0] = Tree('declaracao_funcao',[p[1]])

	 def p_cabecalho(self, p):
	 	'''
	 	cabecalho : IDENTIFICADOR ABREPAR lista_parametros FECHAPAR corpo FIM
	 	'''
	 	p[0] = Tree('cabecalho', [p[3],p[5]],p[1])

	 def p_lista_parametros(self, p):
	 	'''
	 	lista_parametros : lista_parametros "," lista_parametros
	 						| parametro
	 						| vazio
	 	'''
	 	if len(p) == 4:
	 		p[0] = Tree('lista_parametros',[p[1],p[3]])
	 	elif len(p) == 2:
	 		p[0] = Tree('lista_parametros',[p[1]])

	 def p_parametro1(self, p):
	 	'''
	 	parametro : tipo ":" IDENTIFICADOR
	 	'''
 		p[0] = Tree('parametro', [p[1]], p[3])

 	def p_parametro2(self, p):
 		'''
 		parametro : parametro ABRECOL FECHACOL
 		'''
 		p[0] = Tree('parametro', [p[1]])

 	def p_corpo(self, p):
 		'''
 		corpo : corpo acao
 				| vazio
 		'''
 		if len(p) == 3:
 			p[0] = Tree('corpo', [p[1],p[2]])
 		elif len(p) == 2:
 			p[0] = Tree('corpo',[p[1]])

 	def p_acao(self, p):
 		'''
 		acao : expressao
 				| declaracao_variaveis
 				| se
 				| repita
 				| leia
 				| escreva
 				| retorna
 				| escreva
 				| retorna
 				|erro

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
 			p[0] = Tree('se',[p[2], p[4], p[6]])

 	def p_repita(self, p):
 		'''
 		repita : REPITA corpo ATE expressa
 		'''
		p[0] = Tree('repita', [p[2], p[4]])
 	
 	def p_atribuicao(self, p):
 		'''
 		atribuicao : var ":=" expressao
 		'''
 		if len(p):
 			p[0] = Tree('atribuicao', [p[1], p[3]])
 			

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
 		escreva : RETORNA ABREPAR expressao FECHAPAR
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
 							| expressao simples operador_relacional expressao_aditiva
 		'''
 		if len(p) == 2:
			p[0] = Tree('expressao_simples', [p[1]])
		elif len(p) = 4:
			p[0] = Tree('expressao_simples', [p[1], p[2], p[3]])

	def p_expressao_aditiva(self, p):
 		'''
 		expressao_aditiva : expressao_multiplicativa
 							| expressao_aditiva operador_multiplicacao expressao_unaria
 		'''
 		if len(p) == 2:
			p[0] = Tree('expressao_aditiva', [p[1]])
		elif len(p) = 4:
			p[0] = Tree('expressao_aditiva', [p[1], p[2], p[3]])


 	def p_expressao_multiplicativa(self, p):
 		'''
		expressao_multiplicativa : expressao_unaria
						| expressao_multiplicativa operador_multiplicacao expressao_unaria

 		'''
 		if len(p) == 2:
			p[0] = Tree('expressao_multiplicativa', [p[1]])
		elif len(p) = 4:
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
		'''

		p[0] = Tree('operador_relacional', [ ])

	def p_operador_soma(self, p):
		'''
		soma : SOMA
				| SUBTRACAO
		'''
		p[0] = Tree('operador_soma', [ ])

	def p_operador_multiplicacao(self, p):
		'''
		operador_multiplicacao : MULTIPLICACAO
								| DIVISAO
		'''

		p[0] = Tree('operador_multiplicacao', [ ])

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
		numero : NUM_INTEIRO
				| NUM_PONTO_FLUTUANTE
				| NUM_NOTACAO_CIENTIFICA

		'''

		p[0] = Tree('numero', [ ])

	def p_chamada_funcao(self, p):
		'''
		chamada_funcao : IDENTIFICADOR ABREPAR lista_argumentos FECHAPAR
		'''
		p[0] = Tree('chamada_funcao', [p[2]], p[1])

	def p_lista_argumentos(self, p):
		'''
		lista_argumentos : lista_argumentos "," expressao
						| expressao
						| vazio
		'''
		if len(p) == 4:
			p[0] = Tree('lista_argumentos', [p[1],p[3]])
		else:
			p[0] = Tree('lista_argumentos',[p[1]])

