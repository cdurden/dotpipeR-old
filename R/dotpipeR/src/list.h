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
*  -------------------------------- list.h --------------------------------  *
*                                                                            *
*****************************************************************************/

#ifndef LIST_H
#define LIST_H

#include <stdlib.h>

/*****************************************************************************
*                                                                            *
*  Define a structure for linked list elements.                              *
*                                                                            *
*****************************************************************************/

typedef struct ListElmt_ {

void               *data;
struct ListElmt_   *next;

} ListElmt;

/*****************************************************************************
*                                                                            *
*  Define a structure for linked lists.                                      *
*                                                                            *
*****************************************************************************/

typedef struct List_ {

int                size;

int                (*match)(const void *key1, const void *key2);
void               (*destroy)(void *data);

ListElmt           *head;
ListElmt           *tail;

} List;

/*****************************************************************************
*                                                                            *
*  --------------------------- Public Interface ---------------------------  *
*                                                                            *
*****************************************************************************/

void list_init(List *list, void (*destroy)(void *data));

void list_destroy(List *list); // remove each element of the list, and call list->destroy callback on its data

int list_ins_next(List *list, ListElmt *element, const void *data);

int list_rem_next(List *list, ListElmt *element, void **data);

#define list_size(list) ((list)->size)

#define list_head(list) ((list)->head)

#define list_tail(list) ((list)->tail)

#define list_is_head(list, element) ((element) == (list)->head ? 1 : 0)

#define list_is_tail(element) ((element)->next == NULL ? 1 : 0)

#define list_data(element) ((element)->data)

#define list_next(element) ((element)->next)

#endif
