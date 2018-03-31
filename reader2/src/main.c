#include <stdio.h>
#include <math.h>
#include <string.h>

#include "graph.h"
#include "list.h"
#include "set.h"
#include "gdi.h"


extern int parse_graph(GraphDataInterface *gdi);

extern struct yyguts_t *yyg;
FILE *fh;
//FILE *yyin,*nul;

void readdot (char **fn, int *n, int *e, int *edges, char **attr_list, const int *maxbytes) {
  
  Graph graph;
  Vertex *vertex;
  Edge *edge;
  Attr *attr;
  int i=1; // node index
  int bytecount=0;
  char *index = "index";
  GraphDataInterface gdi;
  graph_init(&graph);
  gdi_init(&gdi, &graph);
//  yyset_in(fopen(*fn, "r"), scanner);
//  yyin = fopen(*fn,"r");
//  yyg->yyin_r = fopen(*fn,"r");
//  nul = fopen("/dev/null","w");
  fh = fopen(*fn,"r");
//  yy_scan_string(input);
  parse_graph(&gdi); // call function defined in yacc code

  *n = list_size(graph.vertices);
  *e = 0;

  ListElmt *vertex_elmt,*attr_elmt,*edge_elmt;
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {
    vertex = (Vertex *)list_data(vertex_elmt);
    bytecount += snprintf(*attr_list, *maxbytes-bytecount, "%s", vertex->id);
  }
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {
    vertex = (Vertex *)list_data(vertex_elmt);
    attr_elmt = list_head((List *)(vertex->data));
    attr = malloc(sizeof(Attr));
    attr->key = index;
    attr->value = malloc(sizeof(int));
    *(attr->value) = i++;
    for (attr_elmt = list_next(attr_elmt); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
      bytecount += snprintf(*attr_list, *maxbytes-bytecount, "%s=%s,", ((Attr *)attr_elmt->data)->key, ((Attr *)attr_elmt->data)->value);
    }
  }
  i=0;
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {
    vertex = (Vertex *)list_data(vertex_elmt);
    for (edge_elmt = list_head((List *)vertex->adjlist); edge_elmt != NULL; edge_elmt = list_next(edge_elmt)) {
      edge = (Edge *) list_data(edge_elmt);
      *(edges+2*i) = *(((Attr *)list_data(list_head((List *)(vertex->data))))->value);
      *(edges+2*i+1) = *(((Attr *)list_data(list_head((List *)(edge->tovertex->data))))->value);
//      printf("%s -> %s [", vertex->id, edge->tovertex->id);
      for (attr_elmt = list_head((List *)(edge->data)); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
//        printf("%s=%s,", ((Attr *)attr_elmt->data)->key, ((Attr *)attr_elmt->data)->value);
        bytecount += snprintf(*attr_list, *maxbytes-bytecount, "%s=%s,", ((Attr *)attr_elmt->data)->key, ((Attr *)attr_elmt->data)->value);
      }
    }
  }
  graph_rem_edge(&graph, edge);
  graph_destroy(&graph);
}

int main (int argc, char **argv) {
  Graph graph;
  Vertex *vertex;
  Edge *edge;
  GraphDataInterface gdi;
  graph_init(&graph);
  gdi_init(&gdi, &graph);
//  printf("0x%x\n",(int) gdi.g);

//  yyg->yyin_r = fopen(argv[1],"r");
//  yyin = fopen(argv[1],"r");
  fh = fopen(argv[1],"r");
//  yyset_in(fh, scanner);
//  nul = fopen("/dev/null","w");
  
  printf("\n");
  parse_graph(&gdi); // call function defined in yacc code
  char *preprocessor_line;

  printf("\n");
  ListElmt *vertex_elmt,*attr_elmt,*edge_elmt,*preprocessor_line_elmt;
  for (preprocessor_line_elmt = list_head(gdi.preprocessor_lines); preprocessor_line_elmt != NULL; preprocessor_line_elmt = list_next(preprocessor_line_elmt)) {
    preprocessor_line = (char *)list_data(preprocessor_line_elmt);
    printf("%s", preprocessor_line);
  }
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {
    vertex = (Vertex *)list_data(vertex_elmt);
    printf("%s [", vertex->id);
    for (attr_elmt = list_head((List *)(vertex->data)); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
      printf("%s=%s,", ((Attr *)attr_elmt->data)->key, ((Attr *)attr_elmt->data)->value);
    }
    printf("]\n");
    for (edge_elmt = list_head((List *)vertex->adjlist); edge_elmt != NULL; edge_elmt = list_next(edge_elmt)) {
      edge = (Edge *) list_data(edge_elmt);
//      printf("%s -> %s [", vertex->id, edge->tovertex->id);
      printf("%s -> %s [", edge->fromvertex->id, edge->tovertex->id);
      for (attr_elmt = list_head((List *)(edge->data)); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
        printf("%s=%s,", ((Attr *)attr_elmt->data)->key, ((Attr *)attr_elmt->data)->value);
      }
      printf("]\n");
      graph_rem_edge(&graph, edge);
    }
  }
  if(graph_rem_vertex(&graph,vertex)==-1) { printf("couldn't remove vertex\n"); }
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {
    vertex = (Vertex *)list_data(vertex_elmt);
    printf("%s [", vertex->id);
    for (attr_elmt = list_head((List *)(vertex->data)); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
      printf("%s=%s,", ((Attr *)attr_elmt->data)->key, ((Attr *)attr_elmt->data)->value);
    }
    printf("]\n");
    for (edge_elmt = list_head((List *)vertex->adjlist); edge_elmt != NULL; edge_elmt = list_next(edge_elmt)) {
      edge = (Edge *) list_data(edge_elmt);
//      printf("%s -> %s [", vertex->id, edge->tovertex->id);
      printf("%s -> %s [", edge->fromvertex->id, edge->tovertex->id);
      for (attr_elmt = list_head((List *)(edge->data)); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
        printf("%s=%s,", ((Attr *)attr_elmt->data)->key, ((Attr *)attr_elmt->data)->value);
      }
      printf("]\n");
    }
  }
  graph_destroy(&graph);
  return 0;
}
