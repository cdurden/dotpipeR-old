CFLAGS := -g -lm -DYYDEBUG=1 -Wall
LFLAGS = --yylineno
YFLAGS = -v -d -t
CC = gcc
objects = main.o graph.o list.o set.o gdi.o
lexer = lex.yy.o
parser = y.tab.o

all: dotreader

src/lex.yy.c: src/dot.l
	lex ${LFLAGS} $<
	mv lex.yy.c src/

src/y.tab.c: src/dot.y
	yacc ${YFLAGS} $<
	mv y.tab.c y.tab.h src/

$(lexer): src/y.tab.c src/lex.yy.c
	$(CC) -c $(CFLAGS) src/lex.yy.c -o $(lexer)
	
$(parser): src/y.tab.c
	$(CC) -c $(CFLAGS) src/y.tab.c -o $(parser)

$(objects): %.o: src/%.c
	$(CC) -c $(CFLAGS) $< -o $@

dotreader: $(objects) $(lexer) $(parser)
	$(CC) $(CFLAGS) $(objects) $(lexer) $(parser) -o $@

clean: 
	rm -f dotreader $(objects) $(lexer) $(parser) src/y.tab.c src/y.tab.h src/lex.yy.c
