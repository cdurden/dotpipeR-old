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

#include "graph.h"
#include "list.h"

typedef struct Attr {
  char *key;
  char *value;
} Attr;

typedef struct GraphDataInterface_ {
/*  void *(*vertex_data_destroy)(void *data);
  void *(*edge_data_destroy)(void *data);
  Vertex *(*mkvertex)(char *id, List *attr_list);
  Edge *(*mkedge)(List *attr_list);
  void *(*fetch_edge_data)(Graph *graph, char *id);
  int (*fetch_vertex_by_id)(Graph *graph, char *id, Vertex **vertex);
*/
  List *preprocessor_lines;
  int complete;
  Graph *g;
} GraphDataInterface;

void gdi_init(GraphDataInterface *gdi, Graph *graph);
