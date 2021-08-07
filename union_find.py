#!/usr/bin/env python3

"""Structure de données pour partition d'ensemble.
"""



class Node:
	"""Sommet (élément) de l'ensemble, avec pointeur sur parent.
	"""

	def __init__(self, parent):
		self.parent = parent #Racine de l'arbre
		self.size = 1 #Nombre de descendants (un noeud est son propre descendant)



class DisjointForest:
	"""Ensemble partitionné. Une table de hachage stocke tous les éléments distincts;
	une liste permet de relier les éléments à leur parent en utilisant leur indice
	dans la liste.
	"""

	def __init__(self):
		self.elements = {}
		self.node_list = []

	def create_set(self, elem):
		"""Création d'une partition avec un élément.
		"""
		self.elements[elem] = len(self.node_list) #Indice de l'élément dans la liste des sommets
		node = Node(self.elements[elem])
		self.node_list.append(node) #Son propre parent
		return node

	def find(self, elem):
		"""Etant donné un élément, trouver la partition à laquelle il appartient
		via la racine de l'arbre.
		"""
		root = self.elements[elem] #Indice de l'élément dans la liste
		while self.node_list[root].parent != root:
			root = self.node_list[root].parent
		node = self.elements[elem]
		#Compression de l'arbre pour améliorer la prochaine recherche.
		while self.node_list[node].parent != root:
			parent = self.node_list[node].parent
			self.node_list[node].parent = root
			node = parent
		return root

	def merge(self, elem_x, elem_y):
		"""Réunion de deux partitions. et retourne l'indice de node_list du parent du
		merge a gauche et la racine supprimé a droite.
		"""
		x, y = self.find(elem_x), self.find(elem_y)
		if x == y:
			return (x, y)
		if self.node_list[x].size < self.node_list[y].size:
			self.node_list[x].parent = y
			self.node_list[y].size += self.node_list[x].size
			return (y, x)
		else:
			self.node_list[y].parent = x
			self.node_list[x].size += self.node_list[y].size
			return (x, y)
