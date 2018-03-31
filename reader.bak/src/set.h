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
*  -------------------------------- set.h ---------------------------------  *
*                                                                            *
*****************************************************************************/

#ifndef SET_H
#define SET_H

#include <stdlib.h>

#include "list.h"

/*****************************************************************************
*                                                                            *
*  Implement sets as linked lists.                                           *
*                                                                            *
*****************************************************************************/

typedef List Set;

/*****************************************************************************
*                                                                            *
*  --------------------------- Public Interface ---------------------------  *
*                                                                            *
*****************************************************************************/

void set_init(Set *set, int (*match)(const void *key1, const void *key2),
   void (*destroy)(void *data));

#define set_destroy list_destroy

int set_insert(Set *set, const void *data);

int set_remove(Set *set, void **data);

int set_union(Set *setu, const Set *set1, const Set *set2);

int set_intersection(Set *seti, const Set *set1, const Set *set2);

int set_difference(Set *setd, const Set *set1, const Set *set2);

int set_is_member(const Set *set, const void *data);

int set_is_subset(const Set *set1, const Set *set2);

int set_is_equal(const Set *set1, const Set *set2);

#define set_size(set) ((set)->size)

#endif
