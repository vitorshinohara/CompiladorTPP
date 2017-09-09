# -*- coding: utf-8 -*-

import ply.lex as lex

reserved = {
	'se' : 'SE',
	'então' : 'ENTAO',
	'senão' : 'SENAO',
	'fim' : 'FIM',
	'repita' : 'REPITA',
	'flutuante' : 'FLUTUANTE',
	'retorna' : 'RETORNA',
	'leia' : 'LEIA',
	'até' : 'ATE',
	'escreva' : 'ESCREVA',
	'inteiro' : 'INTEIRO',
	'principal' : 'PRINCIPAL'
}

tokens = [
	'SOMA',
	'SUBTRACAO',
	'MULTIPLICACAO',
	'DIVISAO',
	'IGUALDADE',
	'VIRGULA',
	'ATRIBUICAO',
	'MENOR',
	'MAIOR',
	'MENORIGUAL',
	'MAIORIGUAL',
	'ABREPAR',
	'FECHAPAR',
	'DOISPONTOS',
	'ABRECOL',
	'FECHACOL',
	'ELOGICO',
	'NEGACAO',
	'IDENTIFICADOR',
	'COMENTARIO',
] + reserved.values()


t_SOMA = r'\+'
t_SUBTRACAO = r'\-'
t_MULTIPLICACAO = r'\*'
t_DIVISAO = r'/'
t_IGUALDADE = r'\='
t_VIRGULA = r'\,'
t_ATRIBUICAO = r'\:\='
t_MENOR = r'\<'
t_MAIOR = r'\>'
t_MENORIGUAL = r'\<\='
t_MAIORIGUAL = r'\>\='
t_ABREPAR = r'\('
t_FECHAPAR = r'\)'
t_DOISPONTOS = r'\:'
t_ABRECOL = r'\['
t_FECHACOL = r'\]'
t_ELOGICO = r'\&\&'
t_NEGACAO = r'\!'


def t_FLUTUANTE(t):
	r'[+-]?\d+\.\d+'
	t.value = int(t.value)
	return t

def t_INTEIRO(t):
	r'[+-]?\d+'
	t.value = int(t.value)
	return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z][a-zA-Z_0-9à-ú]*'
    t.type = reserved.get(t.value,'IDENTIFICADOR')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = '\t'

def t_error(t):
    # print("Caractere não reconhecido '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

data = '''
inteiro principal()
	inteiro: digitado
	inteiro: i
	i := 1
	repita
		flutuante: f
		inteiro: int
		flutuante: resultado
		f := i/2.
		int := i/2
		resultado := f - int
		
		se  resultado > 0
			escreva (i)
		fim
		i := i+1
	até i <= digitado
fim
'''

lexer.input(data)

while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    print(tok)