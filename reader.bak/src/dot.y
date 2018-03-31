%{
#include <stdio.h>
#include <string.h>
#include "list.h" // for attr_lists
#include "graph.h"
#include "gdi.h"
#define yyscan_t void*

//#define YYPARSE_PARAM gdi

#define YYSTYPE void*

extern char *yytext;
void yyset_in  ( FILE * in_str , yyscan_t scanner );
int yyget_lineno (yyscan_t scanner);
int yylex_init( yyscan_t* );
int yylex_destroy (yyscan_t );
int yylex (YYSTYPE *yylval, yyscan_t scannner);
int yyparse (yyscan_t scanner, GraphDataInterface *gdi);
//extern int yylex (void);
//extern int yyparse (void *YYPARSE_PARAM);
//extern int yyget_lineno (void);
//extern int yyparse (yyscan_t scanner, void *YYPARSE_PARAM);
extern FILE *fh;

#define YYDEBUG_LEXER_TEXT yytext

void attr_destroy(void *data) {
  free(((Attr *)data)->key);
  free(((Attr *)data)->value);
  free(data);
}
void voidlist_destroy(void *list) {
  list_destroy((List *)list);
}
void yyerror(void *scanner, GraphDataInterface *gdi, const char *err) {
    fprintf(stderr, "%s at %d\n", err, yyget_lineno(scanner) );
}
 
int yywrap()
{
        return 1;
} 

int parse_graph(GraphDataInterface *gdi)
{
        
        yyscan_t scanner;
        if (yylex_init(&scanner)) return(1);
        yyset_in(fh, scanner);
        yyparse(scanner, gdi);
        yylex_destroy(scanner);
	return 1;
}

%}

%pure-parser
%lex-param {void * scanner}
%parse-param { void * scanner }
%parse-param { GraphDataInterface *gdi }

%token ID GRAPH NODE EDGE SUBGRAPH OBRACE EBRACE EDGEOP COMMA COLON SEMICOLON EQUALS LSBRACKET RSBRACKET PREPROCESSORLINE UNMATCHED;

%%

graph : preprocessor_lines GRAPH ID OBRACE stmt_list EBRACE preprocessor_lines
{
  ((GraphDataInterface *)gdi)->complete=1;
};

subgraph_begin : SUBGRAPH ID /* This rule and the next change the graph pointer so that subgraphs are ignored. If we want to implement reading subgraphs, we could use graphs of graphs, setting the graph pointer to a graph created as a child node, and setting the pointer back to the parent node when done 
{
  Graph *g = (Graph*)graph;
  Graph h;
  graph_init(&h, g->match, g->destroy_vertex, g->destroy_edge_data);
  graph = &h;
  $$ = g;
}*/;

subgraph : subgraph_begin OBRACE stmt_list EBRACE
/*{
  graph = $1;
}*/;

stmt_list : /* empty */ | stmt SEMICOLON stmt_list | stmt stmt_list;

stmt : edge_stmt | node_stmt | attr_stmt | subgraph | ID EQUALS ID;

attr_stmt : GRAPH | NODE | EDGE attr_list;

edge_stmt: node_stmt edgeRHS attr_list
{
  Edge *edge;
  Vertex *vertex1 = $1;
  Vertex *vertex2 = $2;
  edge = malloc(sizeof(Edge));

  edge_init(edge, vertex1, vertex2, (void *)$3, voidlist_destroy);
  if(graph_ins_edge(((GraphDataInterface *)gdi)->g,edge)==0) {
//    printf("inserted edge between %s (0x%x) and %s (0x%x)\n", vertex1->id, (int) vertex1, vertex2->id, (int) vertex2);
  }
  
}
;

edgeRHS: EDGEOP node_id
{
  $$ = $2;
};

node_stmt: node_id attr_list
{
  Vertex *vertex;
  List *attr_list;
  ListElmt *attr_elmt;
  vertex = (Vertex *)$1;
  attr_list = (List *)$2;
  for(attr_elmt = list_head(attr_list); attr_elmt!=NULL; attr_elmt=list_next(attr_elmt)) {
    list_ins_next(vertex->data, NULL, list_data(attr_elmt));
  }
  $$ = vertex;
}
;

port: /* empty */ | COLON ID | COLON ID COLON ID;

node_id: ID port
{
  Vertex *vertex = NULL;
  List *attr_list;

  if(fetch_vertex_by_id(((GraphDataInterface *)gdi)->g, (char *)$1, &vertex)!=0) {
//    printf("creating vertex %s\n",(char *)$1);
    vertex = malloc(sizeof(Vertex));
    attr_list = (List *)malloc(sizeof(List));
    list_init(attr_list, attr_destroy);
    vertex_init(vertex,(char *)$1, attr_list, voidlist_destroy);
    graph_ins_vertex(((GraphDataInterface *)gdi)->g,vertex);
//  } else {
//    printf("found vertex by id %s: returned vertex %s\n",(char *)$1,vertex->id);
  }
  $$ = vertex;
};

attr_list: /* empty */
{
  List *attr_list;
  attr_list = (List *)malloc(sizeof(List));
//  printf("initializing attributes list\n");
  list_init(attr_list, attr_destroy);
  $$ = attr_list;
}
attr_list: LSBRACKET a_list RSBRACKET
{
//  printf("attr_list size: %d\n", list_size((List *)$2));
  $$ = $2;
};

a_list: /* empty */ 
{
  List *attr_list;
  attr_list = (List *)malloc(sizeof(List));
//  printf("initializing attributes list\n");
  list_init(attr_list, attr_destroy);
  $$ = attr_list;
};

a_list: a_list COMMA attr
{
  List *attr_list;
  attr_list = $1;
//  printf("inserting attribute\n");
  list_ins_next(attr_list, NULL, $3);
  $$ = attr_list;
};

a_list: a_list attr
{
  List *attr_list;
  attr_list = $1;
//  printf("inserting attribute\n");
  list_ins_next(attr_list, NULL, $2);
  $$ = attr_list;
};

attr: ID EQUALS ID
{
  Attr *attr;
  attr = (Attr *)malloc(sizeof(Attr));
  attr->key = $1;
  attr->value = $3;
  $$ = attr;
};

preprocessor_lines: /* empty */
preprocessor_lines: preprocessor_lines PREPROCESSORLINE
{
  list_ins_next(((GraphDataInterface *)gdi)->preprocessor_lines, list_tail(((GraphDataInterface *)gdi)->preprocessor_lines), $2);
};
