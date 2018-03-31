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

/*
    The code in this file is derived from the book "Mastering
    Algorithms with C"  by Kyle Loudon, published by O'Reilly & Associates. This
    code is under copyright and cannot be included in any other book, publication,
    or educational product without permission from  O'Reilly & Associates. No
    warranty is attached; we cannot take responsibility for errors or fitness for
    use.
*/

/*****************************************************************************
*                                                                            *
*  -------------------------------- graph.h -------------------------------  *
*                                                                            *
*****************************************************************************/
#ifndef GRAPH_H
#define GRAPH_H

#include <stdlib.h>

#include "list.h"
#include "set.h"

typedef struct {
  Set *adjlist;
  char *id;
  void *data;
  void (*destroy_data)(void *data);
} Vertex;

typedef struct Edge_ {
void               *data;
Vertex             *fromvertex;
Vertex             *tovertex;
void (*destroy_data)(void *data);
} Edge;

/*****************************************************************************
*                                                                            *
*  Define a structure for adjacency lists.                                   *
*                                                                            *
*****************************************************************************/

typedef struct AdjListElmt_ {

Vertex               *vertex;
Edge                 *edge;

} AdjListElmt;


/*****************************************************************************
*                                                                            *
*  Define a structure for graphs.                                            *
*                                                                            *
*****************************************************************************/

typedef struct Graph_ {

int                vcount;
int                ecount;

//int                (*match)(const void *key1, const void *key2);
//void               (*destroy_vertex)(Vertex *vertex);
//void               (*destroy_edge_data)(void *data);

List               *vertices;

} Graph;

/*****************************************************************************
*                                                                            *
*  Define colors for vertices in graphs.                                     *
*                                                                            *
*****************************************************************************/

typedef enum VertexColor_ {white, gray, black} VertexColor;

/*****************************************************************************
*                                                                            *
*  --------------------------- Public Interface ---------------------------  *
*                                                                            *
*****************************************************************************/

void edge_init(Edge *edge, Vertex *fromvertex, Vertex *tovertex, void *data, void (*edge_data_destroy)(void *data));

void vertex_init(Vertex *vertex, char *id, const void *data, void (*vertex_data_destroy)(void *data));

void graph_init(Graph *graph);

void graph_destroy(Graph *graph);

int graph_ins_vertex(Graph *graph, const Vertex *vertex);

int graph_ins_vertex_from_data(Graph *graph, char *id, const void *data, void (*vertex_data_destroy)(void *data));

int graph_ins_edge(Graph *graph, const Edge *edge);

int graph_rem_vertex(Graph *graph, Vertex *vertex);

int graph_rem_edge(Graph *graph, Edge *edge);

int graph_adjlist(const Graph *graph, const Vertex *vertex, List **adjlist);

int graph_is_adjacent(const Graph *graph, const Vertex *vertex1, const Vertex 
   *vertex2);

int fetch_vertex_by_id(Graph *graph, char *id, Vertex **vertex);


#define graph_vertices(graph) ((graph)->vertices)

#define graph_vcount(graph) ((graph)->vcount)

#define graph_ecount(graph) ((graph)->ecount)

#endif
