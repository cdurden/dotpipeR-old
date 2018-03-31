/*
    dotpipeR: R package for computational pipelines using the DOT grammar
    Copyright (C) 2013  Christopher L Durden <cdurden@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

#include <stdio.h>
#include <math.h>
#include <string.h>

#include "graph.h"
#include "list.h"
#include "set.h"
#include "gdi.h"
#include "R.h"
#include "Rdefines.h"


extern int parse_graph(GraphDataInterface *gdi);

FILE *fh;

SEXP readdot (SEXP fn) {
  if(!isString(fn) || length(fn) != 1)
    error("filename is not a single string");

  const char *file = CHAR(STRING_ELT(fn, 0));
  int maxbytes = 65536;

  SEXP nodes;
  SEXP node_attrs;
  SEXP edge_attrs;
  SEXP preprocessor_lines;
  SEXP graphdata;
  SEXP attrs,attr;
  SEXP edgemat;
  SEXP dim;
  
  List *edges;

  Graph graph;
  Vertex *vertex;
  Edge *edge;
//  Attr *index_attr;
//  char *index = "index";
  char *buf;
  int i,j; // node index
  GraphDataInterface gdi;
  graph_init(&graph);
  gdi_init(&gdi, &graph);

  if((fh = fopen(file,"r"))==NULL) {
//        printf("Cannot open file.\n");
        return R_NilValue;
  }
  parse_graph(&gdi); // call function defined in yacc code
  if(!gdi.complete) {
    return(R_NilValue);
  }

  if((buf = malloc(maxbytes*sizeof(char)))==NULL) {
//    printf("could not allocate character vector of length maxbytes=%d>0",maxbytes);
    return R_NilValue;
  }

  // generate R objects to store vertex information 
  PROTECT(graphdata = allocVector(VECSXP,5));
  PROTECT(nodes = allocVector(STRSXP,list_size(graph.vertices)));
  PROTECT(node_attrs = allocVector(VECSXP,list_size(graph.vertices)));
  PROTECT(preprocessor_lines = allocVector(STRSXP,list_size(gdi.preprocessor_lines)));

  ListElmt *vertex_elmt,*attr_elmt,*edge_elmt,*preprocessor_line_elmt;
  i=0;
  for (preprocessor_line_elmt = list_head(gdi.preprocessor_lines); preprocessor_line_elmt != NULL; preprocessor_line_elmt = list_next(preprocessor_line_elmt)) {
    buf = (char *)list_data(preprocessor_line_elmt);
    SET_STRING_ELT(preprocessor_lines, i++, mkChar(buf));
  }

  i=0;
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {
    vertex = (Vertex *)list_data(vertex_elmt);
    SET_STRING_ELT(nodes, i++, mkChar(vertex->id));
  }

  i=0;
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {

    vertex = (Vertex *)list_data(vertex_elmt);
    SET_VECTOR_ELT(node_attrs,i, allocVector( VECSXP,list_size((List *)(vertex->data)) ));
    attrs = VECTOR_ELT(node_attrs,i);

    j=0;
    for (attr_elmt = list_head((List *)(vertex->data)); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
      SET_VECTOR_ELT(attrs,j, allocVector( STRSXP,2));
      attr = VECTOR_ELT(attrs,j);
      SET_STRING_ELT(attr, 0, mkChar( ((Attr *)attr_elmt->data)->key ));
      SET_STRING_ELT(attr, 1, mkChar( ((Attr *)attr_elmt->data)->value ));
      j++;
    }
    i++;
  }
  edges = malloc(sizeof(List));
  list_init(edges, free);
  for (vertex_elmt = list_head(graph.vertices); vertex_elmt != NULL; vertex_elmt = list_next(vertex_elmt)) {
    vertex = (Vertex *)list_data(vertex_elmt);
    for (edge_elmt = list_head((List *)vertex->adjlist); edge_elmt != NULL; edge_elmt = list_next(edge_elmt)) {
      edge = (Edge *) list_data(edge_elmt);
      list_ins_next(edges, list_tail(edges), (void *) edge);
    }
  }
  PROTECT(edgemat = allocVector(STRSXP,2*list_size(edges))); 
  PROTECT(edge_attrs = allocVector(VECSXP,list_size(edges)));

  i=0;
  for (edge_elmt = list_head(edges); edge_elmt != NULL; edge_elmt = list_next(edge_elmt)) {
    edge = (Edge *) list_data(edge_elmt);
    SET_STRING_ELT(edgemat, 2*i, mkChar( ((Vertex *)edge->fromvertex)->id ));
    SET_STRING_ELT(edgemat, 2*i+1, mkChar( ((Vertex *)edge->tovertex)->id ));

    SET_VECTOR_ELT(edge_attrs,i, allocVector( VECSXP,list_size((List *)(edge->data)) ));
    attrs = VECTOR_ELT(edge_attrs,i);
    j=0;
    for (attr_elmt = list_head((List *)(edge->data)); attr_elmt != NULL; attr_elmt = list_next(attr_elmt)) {
      SET_VECTOR_ELT(attrs,j, allocVector( STRSXP,2));
      attr = VECTOR_ELT(attrs,j);
      SET_STRING_ELT(attr, 0, mkChar( ((Attr *)attr_elmt->data)->key ));
      SET_STRING_ELT(attr, 1, mkChar( ((Attr *)attr_elmt->data)->value ));
      j++;
    }
    i++;
  }
  PROTECT(dim = allocVector(INTSXP, 2));
  INTEGER(dim)[0] = 2;
  INTEGER(dim)[1] = list_size(edges);
  setAttrib(edgemat, R_DimSymbol, dim);

  graph_destroy(&graph);
  fclose(fh);
  SET_VECTOR_ELT(graphdata,0,nodes);
  SET_VECTOR_ELT(graphdata,1,node_attrs);
  SET_VECTOR_ELT(graphdata,2,edgemat);
  SET_VECTOR_ELT(graphdata,3,edge_attrs);
  SET_VECTOR_ELT(graphdata,4,preprocessor_lines);
  UNPROTECT(7);
  return(graphdata);
}

