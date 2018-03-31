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
*  -------------------------------- list.c --------------------------------  * 
*                                                                            * 
*****************************************************************************/ 
 
#include <stdlib.h> 
#include <string.h> 
//#include <stdio.h> 
 
#include "list.h" 
 
/***************************************************************************** 
*                                                                            * 
*  ------------------------------- list_init ------------------------------  * 
*                                                                            * 
*****************************************************************************/ 
 
void list_init(List *list, void (*destroy)(void *data)) { 
 
/***************************************************************************** 
*                                                                            * 
*  Initialize the list.                                                      * 
*                                                                            * 
*****************************************************************************/ 
 
list->size = 0; 
list->destroy = destroy; 
list->head = NULL; 
list->tail = NULL; 
 
return; 
 
} 
 
/***************************************************************************** 
*                                                                            * 
*  ----------------------------- list_destroy -----------------------------  * 
*                                                                            * 
*****************************************************************************/ 
 
void list_destroy(List *list) { 
 
void               *data; 
 
/***************************************************************************** 
*                                                                            * 
*  Remove each element.                                                      * 
*                                                                            * 
*****************************************************************************/ 
 
while (list_size(list) > 0) { 
 
   if (list_rem_next(list, NULL, (void **)&data) == 0 && list->destroy != 
      NULL) { 
 
      /*********************************************************************** 
      *                                                                      * 
      *  Call a user-defined function to free dynamically allocated data.    * 
      *                                                                      * 
      ***********************************************************************/ 
 
      list->destroy(data); 
 
   } 
 
} 
 
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
*  ----------------------------- list_ins_next ----------------------------  * 
*                                                                            * 
*****************************************************************************/ 
 
int list_ins_next(List *list, ListElmt *element, const void *data) { 
 
ListElmt           *new_element; 
 
//printf("list_ins_next: 0x%x\n", (int) data); 
/***************************************************************************** 
*                                                                            * 
*  Allocate storage for the element.                                         * 
*                                                                            * 
*****************************************************************************/ 
 
if ((new_element = (ListElmt *)malloc(sizeof(ListElmt))) == NULL) 
   return -1; 
 
/***************************************************************************** 
*                                                                            * 
*  Insert the element into the list.                                         * 
*                                                                            * 
*****************************************************************************/ 
 
new_element->data = (void *)data; 
 
if (element == NULL) { 
 
   /************************************************************************** 
   *                                                                         * 
   *  Handle insertion at the head of the list.                              * 
   *                                                                         * 
   **************************************************************************/ 
 
   if (list_size(list) == 0) 
      list->tail = new_element; 
 
   new_element->next = list->head; 
   list->head = new_element; 
 
   } 
 
else { 
 
   /************************************************************************** 
   *                                                                         * 
   *  Handle insertion somewhere other than at the head.                     * 
   *                                                                         * 
   **************************************************************************/ 
 
   if (element->next == NULL) 
      list->tail = new_element; 
 
   new_element->next = element->next; 
   element->next = new_element; 
 
} 
 
/***************************************************************************** 
*                                                                            * 
*  Adjust the size of the list to account for the inserted element.          * 
*                                                                            * 
*****************************************************************************/ 
 
list->size++; 
 
return 0; 
 
} 
 
/***************************************************************************** 
*                                                                            * 
*  ----------------------------- list_rem_next ----------------------------  * 
*                                                                            * 
*****************************************************************************/ 
 
int list_rem_next(List *list, ListElmt *element, void **data) { 
 
ListElmt           *old_element; 
 
/***************************************************************************** 
*                                                                            * 
*  Do not allow removal from an empty list.                                  * 
*                                                                            * 
*****************************************************************************/ 
 
if (list_size(list) == 0) 
   return -1; 
 
/***************************************************************************** 
*                                                                            * 
*  Remove the element from the list.                                         * 
*                                                                            * 
*****************************************************************************/ 
 
if (element == NULL) { 
 
   /************************************************************************** 
   *                                                                         * 
   *  Handle removal from the head of the list.                              * 
   *                                                                         * 
   **************************************************************************/ 
 
   *data = list->head->data; 
   old_element = list->head; 
   list->head = list->head->next; 
 
   if (list_size(list) == 1) 
      list->tail = NULL; 
 
   } 
 
else { 
 
   /************************************************************************** 
   *                                                                         * 
   *  Handle removal from somewhere other than the head.                     * 
   *                                                                         * 
   **************************************************************************/ 
 
   if (element->next == NULL) 
      return -1; 
 
   *data = element->next->data; 
   old_element = element->next; 
   element->next = element->next->next; 
 
   if (element->next == NULL) 
      list->tail = element; 
 
} 
 
/***************************************************************************** 
*                                                                            * 
*  Free the storage allocated by the abstract data type.                     * 
*                                                                            * 
*****************************************************************************/ 
 
free(old_element); 
 
/***************************************************************************** 
*                                                                            * 
*  Adjust the size of the list to account for the removed element.           * 
*                                                                            * 
*****************************************************************************/ 
 
list->size--; 
 
return 0; 
 
} 
 
const List empty_list; 
