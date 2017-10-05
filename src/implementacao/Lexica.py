# -*- coding: utf-8 -*-

import ply.lex as lex
import sys

class Lexica:

    def __init__(self):
        self.lexer = lex.lex(debug=False, module=self, optimize=False)

	reserved = { # Hashmap de palavras reservados
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

	tokens = [ # Vetor de tokens
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
		'OULOGICO',
		'NEGACAO',
		'IDENTIFICADOR',
		'COMENTARIO',
	] + reserved.values()


	t_SOMA = r'\+'								# +
	t_SUBTRACAO = r'\-'							# -
	t_MULTIPLICACAO = r'\*'						# *
	t_DIVISAO = r'/'							# /
	t_IGUALDADE = r'\='							# =
	t_VIRGULA = r'\,'							# ,
	t_ATRIBUICAO = r'\:\='						# :=
	t_MENOR = r'\<'								# <
	t_MAIOR = r'\>'								# >
	t_MENORIGUAL = r'\<\='						# <=
	t_MAIORIGUAL = r'\>\='						# >=
	t_ABREPAR = r'\('							# (
	t_FECHAPAR = r'\)'							# )
	t_DOISPONTOS = r'\:'						# :
	t_ABRECOL = r'\['							# [
	t_FECHACOL = r'\]'							# ]
	t_ELOGICO = r'\&\&'							# &&
	t_OULOGICO = r'\|\|'						# ||
	t_NEGACAO = r'\!'							# !


	def t_FLUTUANTE(t): # Números flutuantes (0.2, 1.7, 9.1)
		r'\d+\.\d+'
		t.value = float(t.value)
		return t

	def t_INTEIRO(t): # Números inteiros (1, 54, 12)
		r'\d+'
		t.value = int(t.value)
		return t

	def t_COMENTARIO(t): # Comentários (reconhecimento de \n)
		r'\{[^}]*[^{]*\}'
		for x in xrange(1,len(t.value)):
			if t.value[x] == "\n":
				t.lexer.lineno+= 1
		return t;

	def t_IDENTIFICADOR(t): # Identificadores e palavras reservadas
	    r'[a-zA-Z][a-zA-Z_0-9à-ú]*'
	    t.type = reserved.get(t.value,'IDENTIFICADOR') # Verifica na tabela hash se a PR está presente
	    return t

	def t_newline(t): # Contagem de linhas do código
	    r'\n+'
	    t.lexer.lineno += len(t.value)

	t_ignore = '\t '

	def t_error(t): # Tratamento de caracteres não reconhecidos
	    print("Caractere não reconhecido '%s'" % t.value[0])
	    t.lexer.skip(1)


	def main():
		lexer = lex.lex()

		try:
			arquivoEntrada = open(sys.argv[1],'r') # Arquivo passado como argumento na execução
		except IOError: # Tratamento de erro
			print "Arquivo não existe. Cheque se o caminho digitado é válido"
			return 0
		
		data = arquivoEntrada.read() # Variável data recebe o conteúdo do arquivo

		lexer.input(data)
		nome = sys.argv[1].replace(".tpp","") # Remove a extensão do arquivo para gravar a saida em outro arquivo
		arquivo = open(nome+'_Tokens.txt', 'w') # Saida é escrita em um arquivo

		while True:
			tok = lexer.token()
		    
			if not tok: 
				break# No more input

			token = "<"+str(tok.type)+",'"+str(tok.value)+"'> : " + str(tok.lineno) # Mostra o token
																					# no formato <token, lexema> : linha
		    
			print token
			arquivo.write(token + "\n") # Escrita do token no formato  <token, lexema> : linha
			
		arquivo.close() # Fechamento do arquivo

if __name__ == '__main__':
    lexica = Lexica()
    

	# Comentário > alerta para fechamento
	# Principal não precisa ser caractere reservado
