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
  vertex->adjlist = malloc(sizeof(Set));
  set_init(vertex->adjlist, ptr_match, edge_destroy);
  vertex->destroy_data = vertex_data_destroy;
}

void vertex_destroy(void *vertex) {
  free(((Vertex *)vertex)->id);
  set_destroy(((Vertex *)vertex)->adjlist);
  free(((Vertex *)vertex)->adjlist);
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


int graph_ins_vertex_from_data(Graph *graph, char *id, const void *data, void (*vertex_data_destroy)(void *data)) {
  Vertex *vertex = malloc(sizeof(Vertex));
  vertex_init(vertex, id, data, vertex_data_destroy);
  if(graph_ins_vertex(graph, vertex)==0) {
    return 0;
  } else {
    return -1;
  }
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

   if (list_rem_next(list, NULL, (void **)&edge) == 0 && list->destroy !=
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

graph->vcount = 0;
graph->ecount = 0;
graph->vertices = malloc(sizeof(List));

/*****************************************************************************
*                                                                            *
*  Initialize the list of adjacency-list structures.                         *
*                                                                            *
*****************************************************************************/

list_init(graph->vertices, vertex_destroy);


return;

}

int fetch_vertex_by_id(Graph *graph, char *id, Vertex **vertex) {
  ListElmt *element;
  for (element = list_head(graph->vertices); element != NULL; element = list_next(element)) {
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

void graph_destroy(Graph *graph) {

/*****************************************************************************
*                                                                            *
*  Destroy the list of vertices. This will call vertex_destroy on each       *
*  Vertex, which will call vertex->destroy_data and set_destroy on each 
*  vertex->adjlist, which will call edge_destroy on each Edge, which will    
*  call edge->destroy_data, then free the Edge memory, then free the Vertex
*  memory.
*                                                                            *
*****************************************************************************/

list_destroy(graph->vertices);
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
*  --------------------------- graph_ins_vertex ---------------------------  *
*                                                                            *
*****************************************************************************/

int graph_ins_vertex(Graph *graph, const Vertex *vertex) {

ListElmt           *element;

int                retval;

/*****************************************************************************
*                                                                            *
*  Do not allow the insertion of duplicate vertices.                         *
*                                                                            *
*****************************************************************************/

for (element = list_head(graph->vertices); element != NULL; element =
   list_next(element)) {

   if (vertex_match(vertex, (Vertex *) list_data(element)))
      return 1;

}

/*****************************************************************************
*                                                                            *
*  Insert the vertex.                                                        *
*                                                                            *
*****************************************************************************/

if ((retval = list_ins_next(graph->vertices, list_tail(graph->vertices),
   vertex)) != 0) {

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
*  ---------------------------- graph_ins_edge ----------------------------  *
*                                                                            *
*****************************************************************************/

int graph_ins_edge(Graph *graph, const Edge *edge) { // need to add a way to add data to an edge

ListElmt           *element;

int                retval;

/*****************************************************************************
*                                                                            *
*  Do not allow insertion of an edge without both its vertices in the graph. *
*                                                                            *
*****************************************************************************/

for (element = list_head(graph->vertices); element != NULL; element =
   list_next(element)) {

   if (vertex_match(edge->tovertex, list_data(element)))
      break;

}

if (element == NULL)
   return -1;

for (element = list_head(graph->vertices); element != NULL; element =
   list_next(element)) {

   if (vertex_match(edge->fromvertex, list_data(element)))
      break;

}

if (element == NULL)
   return -1;

/*****************************************************************************
*                                                                            *
*  Insert the second vertex into the adjacency list of the first vertex.     *
*                                                                            *
*****************************************************************************/

if ((retval = list_ins_next(edge->fromvertex->adjlist, NULL, (void *) edge))
   != 0) {

   return retval;

}

/*****************************************************************************
*                                                                            *
*  Adjust the edge count to account for the inserted edge.                   *
*                                                                            *
*****************************************************************************/

graph->ecount++;

return 0;

}


/*****************************************************************************
*                                                                            *
*  --------------------------- graph_rem_vertex ---------------------------  *
*                                                                            *
*****************************************************************************/

int graph_rem_vertex(Graph *graph, Vertex *vertex) {

ListElmt           *element,
                   *temp,
                   *prev;

List            *adjlist;
Vertex          *removed;


/*****************************************************************************
*                                                                            *
*  Traverse each adjacency list and the vertices it contains.                *
*                                                                            *
*****************************************************************************/

prev = NULL;
temp = NULL;

for (element = list_head(graph->vertices); element != NULL; element =
   list_next(element)) {

   /**************************************************************************
   *                                                                         *
   *  Do not allow removal of the vertex if it is in an adjacency list.      *
   *                                                                         *
   **************************************************************************/

   
   if (vertex_in_adjlist(((Vertex *)list_data(element))->adjlist, vertex))
      return -1;

   /**************************************************************************
   *                                                                         *
   *  Keep a pointer to the vertex to be removed.                            *
   *                                                                         *
   **************************************************************************/

   if (vertex_match(vertex, (Vertex *)list_data(element))) {
 
      temp = element;

   }

   /**************************************************************************
   *                                                                         *
   *  Keep a pointer to the vertex before the vertex to be removed.          *
   *                                                                         *
   **************************************************************************/

   if (temp == NULL)
      prev = element;

}
 
/*****************************************************************************
*                                                                            *
*  Return if the vertex was not found.                                       *
*                                                                            *
*****************************************************************************/

if (temp == NULL)
   return -1;

/*****************************************************************************
*                                                                            *
*  Do not allow removal of the vertex if its adjacency list is not empty.    *
*                                                                            *
*****************************************************************************/

adjlist = ((Vertex *)list_data(temp))->adjlist;
if (list_size(adjlist) > 0)
   return -1;

/*****************************************************************************
*                                                                            *
*  Remove the vertex.                                                        *
*                                                                            *
*****************************************************************************/

if (list_rem_next(graph->vertices, prev, (void **) &removed) != 0)
   return -1;

/*****************************************************************************
*                                                                            *
*  Free the storage allocated by the abstract data type.                     *
*                                                                            *
*****************************************************************************/

free(adjlist);

/*****************************************************************************
*                                                                            *
*  Adjust the vertex count to account for the removed vertex.                *
*                                                                            *
*****************************************************************************/

graph->vcount--;

return 0;

}

/*****************************************************************************
*                                                                            *
*  ---------------------------- graph_rem_edge ----------------------------  *
*                                                                            *
*****************************************************************************/

int graph_rem_edge(Graph *graph, Edge *edge) {

ListElmt           *element;

/*****************************************************************************
*                                                                            *
*  Locate the adjacency list for the first vertex.                           *
*                                                                            *
*****************************************************************************/

for (element = list_head(graph->vertices); element != NULL; element =
   list_next(element)) {

   if (set_is_member(((Vertex *)list_data(element))->adjlist,edge))
      break;

}

if (element == NULL)
   return -1;

/*****************************************************************************
*                                                                            *
*  Remove the second vertex from the adjacency list of the first vertex.     *
*                                                                            *
*****************************************************************************/

if (set_remove(((Vertex *)list_data(element))->adjlist,(void **) &edge) != 0)
   return -1;

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

for (element = list_head(graph->vertices); element != NULL; element =
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
