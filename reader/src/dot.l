%{
#include <stdio.h>
#include "gdi.h"
#define YYSTYPE char*
//#define YYDEBUG 1

#define YY_FATAL_ERROR(msg) graceful_yy_fatal_error( msg )
#define YYFPRINTF nullfprintf

static void graceful_yy_fatal_error (yyconst char* msg ) {      
  /* Make a bogus use of yy_fatal_error to avoid spurious warning */
  (void) &yy_fatal_error;
  return;
}

#include "y.tab.h"

//extern FILE *nul;
//extern FILE *yyin;
typedef enum { FALSE=0, TRUE=1} BOOL;

%}
%option nounput
%option noinput
%option reentrant bison-bridge
%option noyywrap

%%
\/\*[^\*\/]*\*\/            /* ignore comments */;
\/\/[^\n]*\n                /* ignore comments */;
^#[^\n]*\n               *yylval=strdup(yytext+1); return PREPROCESSORLINE;   /* ignore preprocessor directives */;
strict                   /* ignore strict directive */;
graph                    return GRAPH;
digraph                  return GRAPH;
subgraph                 return SUBGRAPH;
node                     return NODE;
edge                     return EDGE;
\{                       return OBRACE;
\}                       return EBRACE;
->                       return EDGEOP;
=                        return EQUALS;
,                        return COMMA;
\]                       return RSBRACKET;
\[                       return LSBRACKET;
\;                       return SEMICOLON;
:                        return COLON;
[ \t\n]+                   /* ignore whitespace */;
[a-zA-Z\200-\377|_][0-9a-zA-Z\200-\377|_]*    *yylval=strdup(yytext); return ID;
[-]?(\.[0-9]+|[0-9]+(\.[0-9]*)?)    *yylval=strdup(yytext); return ID;
\"([^\"]|\\\")*\"                *yylval=strdup(yytext); return ID; // FIXME: need to allow escaping of double-quotes to conform to dot language specification
.                        return UNMATCHED;
%%
//<<EOF>>                  { printf("EOF\n");return END; }
