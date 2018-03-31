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
    Algorithms with C" by Kyle Loudon, published by O'Reilly & Associates. This
    code is under copyright and cannot be included in any other book, publication,
    or educational product without permission from O'Reilly & Associates. No
    warranty is attached; we cannot take responsibility for errors or fitness for
    use.
*/

/*****************************************************************************
*                                                                            *
*  -------------------------------- graph.c -------------------------------  *
*                                                                            *
*****************************************************************************/

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "graph.h"
#include "list.h"
#include "set.h"


int ptr_match (const void *key1, const void *key2) {
  return(key1 == key2);
}

void edge_init(Edge *edge, Vertex *fromvertex, Vertex *tovertex, void *data, void (*edge_data_destroy)(void *data)) {
  edge->destroy_data = edge_data_destroy;
  edge->fromvertex = fromvertex;
  edge->tovertex = tovertex;
  edge->data = (void *)data;
}

void edge_destroy(void *edge) {
  ((Edge *)edge)->destroy_data(((Edge *)edge)->data);
}

void vertex_init(Vertex *vertex, char *id, const void *data, void (*vertex_data_destroy)(void *data)) {
  vertex->id = (char *)malloc((strlen(id)+1)*sizeof(char));
  strcpy(vertex->id, id);
  vertex->data = (void *) data;
//  vertex->adjlist = malloc(sizeof(Set));
//  set_init(vertex->adjlist, ptr_match, edge_destroy);
  vertex->destroy_data = vertex_data_destroy;
}

void vertex_destroy(void *vertex) {
  free(((Vertex *)vertex)->id);
//  set_destroy(((Vertex *)vertex)->adjlist);
//  free(((Vertex *)vertex)->adjlist);
  ((Vertex *)vertex)->destroy_data(((Vertex *)vertex)->data);
}

int vertex_match (const void *vertex1, const void *vertex2) {
  if (vertex1 == NULL || vertex2 == NULL)
    return -1;
  if (strcmp(((Vertex *)vertex1)->id,((Vertex *)vertex2)->id)==0) {
//    printf("%s ~ %s\n", ((Vertex *)vertex1)->id, ((Vertex *)vertex2)->id);
    return 1;
  } else {
//    printf("%s !~ %s\n", ((Vertex *)vertex1)->id, ((Vertex *)vertex2)->id);
    return 0;
  }
}


int graph_vertex_insert_from_data(Graph *graph, char *id, const void *data, void (*vertex_data_destroy)(void *data)) {
  Vertex *vertex = malloc(sizeof(Vertex));
  vertex_init(vertex, id, data, vertex_data_destroy);
  if(graph_vertex_insert(graph, vertex)==0) {
    return 0;
  } else {
    return -1;
  }
}

Edge* edge_to_vertex_in_adjlist(List *adjlist, const Vertex *vertex) {

ListElmt           *element;

/*****************************************************************************
*                                                                            *
*  Determine if the data is a element of the set.                             *
*                                                                            *
*****************************************************************************/

for (element = list_head(adjlist); element != NULL; element = list_next(element)) {

   if (adjlist->match(vertex, ((Edge *)list_data(element))->tovertex))
      return((Edge *)list_data(element));

}
   return(NULL);
}

int vertex_in_adjlist(List *adjlist, const Vertex *vertex) {

ListElmt           *element;

/*****************************************************************************
*                                                                            *
*  Determine if the data is a element of the set.                             *
*                                                                            *
*****************************************************************************/

for (element = list_head(adjlist); element != NULL; element = list_next(element)) {

   if (adjlist->match(vertex, ((Edge *)list_data(element))->tovertex))
      return 1;

}

return 0;

}

/*****************************************************************************
*                                                                            *
*  ----------------------------- list_destroy -----------------------------  *
*                                                                            *
*****************************************************************************/


void adjlist_destroy(List *list) { // destroy the vertex's adjlist, primarily the edge data
// when the adjlist is constructed, pass a function to destroy edge data
Edge *edge;

/*****************************************************************************
*                                                                            *
*  Remove each element.                                                      *
*                                                                            *
*****************************************************************************/

while (list_size(list) > 0) {

   if (list_remove(list, NULL, (void **)&edge) == 0 && list->destroy !=
      NULL) {

     list->destroy(edge->data);
//     free(edge);
   }

}
//printf("adestroying adjlist\n");

/*****************************************************************************
*                                                                            *
*  No operations are allowed now, but clear the structure as a precaution.   *
*                                                                            *
*****************************************************************************/

memset(list, 0, sizeof(List));

return;

}


/*****************************************************************************
*                                                                            *
*  ------------------------------ graph_init ------------------------------  *
*                                                                            *
*****************************************************************************/

void graph_init(Graph *graph) {

/*****************************************************************************
*                                                                            *
*  Initialize the graph.                                                     *
*                                                                            *
*****************************************************************************/

graph->parent = NULL;
graph->vcount = 0;
graph->ecount = 0;
graph->vertices = (Set *)malloc(sizeof(Set));
graph->edges = (Set *)malloc(sizeof(Set));
graph->subgraphs = (Set *)malloc(sizeof(Set));

/*****************************************************************************
*                                                                            *
*  Initialize the list of edges and vertices.                         *
*                                                                            *
*****************************************************************************/

set_init(graph->vertices, vertex_match, vertex_destroy);
set_init(graph->edges, ptr_match, edge_destroy);
set_init(graph->subgraphs, ptr_match, graph_destroy);


return;

}

int fetch_vertex_by_id(Graph *graph, char *id, Vertex **vertex) {
  ListElmt *element;
  List *vertices = (List *)graph->vertices;
  for (element = list_head(vertices); element != NULL; element = list_next(element)) {
    if(strcmp(((Vertex *) list_data(element))->id, id)==0) {
      *vertex = ((Vertex *) list_data(element));
      break;
    }
  }
  if (element == NULL) {
    return(-1);
  } else {
    return 0;
  }
}


/*****************************************************************************
*                                                                            *
*  ----------------------------- graph_destroy ----------------------------  *
*                                                                            *
*****************************************************************************/

void graph_destroy(void *data) {

/*****************************************************************************
*                                                                            *
*  Destroy the list of vertices. This will call vertex_destroy on each       *
*  Vertex, which will call vertex->destroy_data and set_destroy on each 
*  vertex->adjlist, which will call edge_destroy on each Edge, which will    
*  call edge->destroy_data, then free the Edge memory, then free the Vertex
*  memory.
*                                                                            *
*****************************************************************************/

Graph *graph = (Graph *)data;
set_destroy(graph->vertices);
free(graph->vertices);

/*****************************************************************************
*                                                                            *
*  No operations are allowed now, but clear the structure as a precaution.   *
*                                                                            *
*****************************************************************************/

memset(graph, 0, sizeof(Graph));

return;

}

/*****************************************************************************
*                                                                            *
*  --------------------------- graph_vertex_insert ---------------------------  *
*                                                                            *
*****************************************************************************/

int graph_vertex_insert(Graph *graph, const Vertex *vertex) {

int                retval;

Graph *parent = graph->parent;
if (parent != NULL) {
    graph_vertex_insert(parent, vertex);
}

if ((retval = set_insert(graph->vertices, vertex)) != 0) {
   return retval;
}

/*****************************************************************************
*                                                                            *
*  Adjust the vertex count to account for the inserted vertex.               *
*                                                                            *
*****************************************************************************/

graph->vcount++;

return 0;

}

/*****************************************************************************
*                                                                            *
*  ---------------------------- graph_edge_insert ----------------------------  *
*                                                                            *
*****************************************************************************/

int graph_edge_insert(Graph *graph, const Edge *edge) { // need to add a way to add data to an edge

int                retval;

Graph *parent = graph->parent;
if (parent != NULL) {
    graph_edge_insert(parent, edge);
}

if ((retval = set_insert(graph->edges, edge)) != 0) {
   return retval;
}

/*****************************************************************************
*                                                                            *
*  Adjust the edge count to account for the inserted edge.               *
*                                                                            *
*****************************************************************************/

graph->ecount++;

return 0;

}


/*****************************************************************************
*                                                                            *
*  --------------------------- graph_vertex_remove ---------------------------  *
*                                                                            *
*****************************************************************************/

int graph_vertex_remove(Graph *graph, Vertex *vertex) {

int retval;
ListElmt *element;
Graph *subgraph;

Set *adjacent_set = (Set *)malloc(sizeof(Set));
set_init(adjacent_set, ptr_match, NULL);
adjacents(adjacent_set, graph, vertex);
if (set_size(adjacent_set) > 0) {
   set_destroy(adjacent_set);
   return -1;
}

List *subgraphs = (List *)graph->subgraphs;
for (element = list_head(subgraphs); element != NULL; element = list_next(element)) {
    subgraph = (Graph *) list_data(element);
    graph_vertex_remove(subgraph, vertex);
}

if ((retval = set_remove(graph->vertices,(void *)vertex)) != 0) {
   return retval;
}

/*****************************************************************************
*                                                                            *
*  Adjust the vertex count to account for the inserted vertex.               *
*                                                                            *
*****************************************************************************/

graph->vcount--;

return 0;

}

/*****************************************************************************
*                                                                            *
*  ---------------------------- graph_edge_remove ----------------------------  *
*                                                                            *
*****************************************************************************/

int graph_edge_remove(Graph *graph, Edge *edge) {

int retval;
Graph *subgraph;
ListElmt *element;
for (element = list_head(graph->subgraphs); element != NULL; element = list_next(element)) {
    subgraph = (Graph *) list_data(element);
    graph_edge_remove(subgraph, edge);
}

if ((retval = set_remove(graph->edges,(void *) edge)) != 0) {
   return retval;
}

/*****************************************************************************
*                                                                            *
*  Adjust the edge count to account for the removed edge.                    *
*                                                                            *
*****************************************************************************/

graph->ecount--;

return 0;

}

/*****************************************************************************
*                                                                            *
*  --------------------------- graph_is_adjacent --------------------------  *
*                                                                            *
*****************************************************************************/

int graph_is_adjacent(const Graph *graph, const Vertex *vertex1, const Vertex
   *vertex2) {

ListElmt           *element;

/*****************************************************************************
*                                                                            *
*  Locate the adjacency list of the first vertex.                            *
*                                                                            *
*****************************************************************************/

List *vertices = (List *)graph->vertices;
for (element = list_head(vertices); element != NULL; element =
   list_next(element)) {

   if (vertex_match(vertex1, (Vertex *)list_data(element)))
      break;

}

/*****************************************************************************
*                                                                            *
*  Return if the first vertex was not found.                                 *
*                                                                            *
*****************************************************************************/

if (element == NULL)
   return 0;

/*****************************************************************************
*                                                                            *
*  Return whether the second vertex is in the adjacency list of the first.   *
*                                                                            *
*****************************************************************************/

  return vertex_in_adjlist(vertex1->adjlist, vertex2);

}

int incoming_edges(Set *setp, Graph *graph, Vertex *vertex) {
ListElmt *element;
Edge *edge;
set_init(setp, ptr_match, NULL);
List *edges = (List *)graph->edges;
for (element = list_head(edges); element != NULL; element = list_next(element)) {
    edge = (Edge *) list_data(element);
    if (edge->tovertex == vertex) {
        set_insert(setp, edge);
    }
}
return 0;
}

int outgoing_edges(Set *setp, Graph *graph, Vertex *vertex) {
ListElmt *element;
Edge *edge;
set_init(setp, ptr_match, NULL);
List *edges = (List *)graph->edges;
for (element = list_head(edges); element != NULL; element = list_next(element)) {
    edge = (Edge *) list_data(element);
    if (edge->fromvertex == vertex) {
        set_insert(setp, edge);
    }
}
return 0;
}

int connecting_edges(Set *setp, Graph *graph, Vertex *vertex) {
ListElmt *element;
Edge *edge;
set_init(setp, ptr_match, NULL);
List *edges = (List *)graph->edges;
for (element = list_head(edges); element != NULL; element = list_next(element)) {
    edge = (Edge *) list_data(element);
    if (edge->fromvertex == vertex) {
        set_insert(setp, edge);
    }
    if (edge->tovertex == vertex) {
        set_insert(setp, edge);
    }
}
return 0;
}

int predecessors(Set *setp, Graph *graph, Vertex *vertex) {
ListElmt *element;
Edge *edge;
set_init(setp, ptr_match, NULL);
List *edges = (List *)graph->edges;
for (element = list_head(edges); element != NULL; element = list_next(element)) {
    edge = (Edge *) list_data(element);
    if (edge->tovertex == vertex) {
        set_insert(setp, edge->fromvertex);
    }
}
return 0;
}

int successors(Set *setp, Graph *graph, Vertex *vertex) {
ListElmt *element;
Edge *edge;
set_init(setp, ptr_match, NULL);
List *edges = (List *)graph->edges;
for (element = list_head(edges); element != NULL; element = list_next(element)) {
    edge = (Edge *) list_data(element);
    if (edge->fromvertex == vertex) {
        set_insert(setp, edge->tovertex);
    }
}
return 0;
}

int adjacents(Set *setp, Graph *graph, Vertex *vertex) {
ListElmt *element;
Edge *edge;
set_init(setp, ptr_match, NULL);
List *edges = (List *)graph->edges;
for (element = list_head(edges); element != NULL; element = list_next(element)) {
    edge = (Edge *) list_data(element);
    if (edge->fromvertex == vertex) {
        set_insert(setp, edge->tovertex);
    }
    if (edge->tovertex == vertex) {
        set_insert(setp, edge->fromvertex);
    }
}
return 0;
}
