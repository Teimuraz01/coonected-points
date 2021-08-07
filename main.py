#!/usr/bin/env python3
"""Calcul des composantes connexes.
"""

from sys import argv

from collections import defaultdict
from math import sqrt

from geo.point import Point
from union_find import DisjointForest



def load_instance(filename):
    """
    loads .pts file.
    returns distance limit and points.
    """
    with open(filename, "r") as instance_file:
        lines = iter(instance_file)
        distance = float(next(lines))
        points = [Point([float(f) for f in l.split(",")]) for l in lines]

    return distance, points



def distance_set(distance, points):
	"""Mesure des distances entre les points.
	Complexité: O(n^2)
	"""

	matrix = {}
	matrix[0] = [] #Pour le premier point

	for i, point in enumerate(points):
		j = i+1

		while j < len(points):
			if j not in matrix:
				matrix[j] = []
			calc = (points[j].coordinates[0] - point.coordinates[0])**2 \
			+ (points[j].coordinates[1] - point.coordinates[1])**2
			if calc <= distance**2:
				matrix[i].append(j) #La valeur est l'indice du point
				matrix[j].append(i)

			j += 1

	return matrix



def spanning_tree(matrix):
	"""Algorithme de construction des composantes.
	Complexité: O(n^2)
	"""

	completed_forest = []
	already_connected = set()
	next_comp = set()

	#Tant que la matrice de points n'est pas vide
	while len(matrix) > 0:
		next_points = {next(iter(matrix.keys()))}
		next_comp |= next_points #Union avec un élément, O(1)
		already_connected |= next_comp

		#Tant que la composante en cours n'est pas épuisée
		while len(next_points) > 0:
			current_v = next(iter(next_points))
			for neighbor in matrix[current_v]:
				if neighbor not in already_connected:
					already_connected.add(neighbor)
					next_points.add(neighbor)
					next_comp.add(neighbor)
			del matrix[current_v]

			next_points.remove(current_v)

		completed_forest.append(len(next_comp))
		next_comp.clear()

	return completed_forest


def naif(distance, points):
	matrix = distance_set(distance, points)
	forest = spanning_tree(matrix)
	forest.sort(reverse=True)
	return forest

###########
#autre algo
###########

def adjacent_squares(square, dico):
	"""Renvoie les carrés adjacents s'ils existent.
	"""

	if (square[0]+1, square[1]) in dico:
		yield (square[0]+1, square[1])
	if (square[0]+1, square[1]+1) in dico:
		yield (square[0]+1, square[1]+1)
	if (square[0]+1, square[1]-1) in dico:
		yield (square[0]+1, square[1]-1)
	if  (square[0]-1, square[1]) in dico:
		yield (square[0]-1, square[1])
	if (square[0]-1, square[1]+1) in dico:
		yield (square[0]-1, square[1]+1)
	if (square[0]-1, square[1]-1) in dico:
		yield (square[0]-1, square[1]-1)
	if (square[0], square[1]-1) in dico:
		yield (square[0], square[1]-1)
	if (square[0], square[1]+1) in dico:
		yield (square[0], square[1]+1)



def outer_adjacent_sq(square, dico):
	"""Renvoie les carrés adjacents+1 s'ils existent.
	"""

	if (square[0]+2, square[1]) in dico:
		yield (square[0]+2, square[1])
	if (square[0]+2, square[1]+1) in dico:
		yield (square[0]+2, square[1]+1)
	if (square[0]+2, square[1]-1) in dico:
		yield (square[0]+2, square[1]-1)
	if (square[0]-2, square[1]) in dico:
		yield (square[0]-2, square[1])
	if (square[0]-2, square[1]+1) in dico:
		yield (square[0]-2, square[1]+1)
	if (square[0]-2, square[1]-1) in dico:
		yield (square[0]-2, square[1]-1)

	if (square[0], square[1]+2) in dico:
		yield (square[0], square[1]+2)
	if (square[0]+1, square[1]+2) in dico:
		yield (square[0]+1, square[1]+2)
	if (square[0]-1, square[1]+2) in dico:
		yield (square[0]-1, square[1]+2)
	if (square[0], square[1]-2) in dico:
		yield (square[0], square[1]-2)
	if (square[0]+1, square[1]-2) in dico:
		yield (square[0]+1, square[1]-2)
	if (square[0]-1, square[1]-2) in dico:
		yield (square[0]-1, square[1]-2)



def merge_n_update(elem_x, elem_y, composantes, forest):
	"""Fusionne deux composantes et met à jour le dico de composantes.
	"""

	merge_parent, removed_root = forest.merge(elem_x, elem_y)

	#Si la fonction est appelée sur des points de la même composante
	if merge_parent == removed_root:
		return

	composantes[forest.node_list[merge_parent]] = forest.node_list[merge_parent].size
	del composantes[forest.node_list[removed_root]]



def lineaire(distance, points):
	"""
	Algorithme de construction de composantes connexes, utilisant la structure de
	données union-find. Range les points dans des carrés de côté distance/sqrt(2)
	puis mesure les distances entre les points de chaque carré et les points des
	carrés adjacents.
	"""

	composantes = {}
	squares = defaultdict(list)
	squares_comp = defaultdict(set)

	forest = DisjointForest()
	cote = distance/sqrt(2)

	for pt in points:
		square_x = pt.coordinates[0]//cote
		square_y = pt.coordinates[1]//cote

		node = forest.create_set(pt)
		composantes[node] = 1

		#Création du carré et fusion progressive des points en une composante
		squares[(square_x, square_y)].append(pt)
		merge_n_update(squares[(square_x, square_y)][0], pt, composantes, forest)

	for square, pts in squares.items():
		#Comparaison des points du carré courant aux points des carrés adjacents
		for adjacent in adjacent_squares(square, squares):
			merged = False
			#On ne compare que si les carrés n'ont pas déjà été comparés
			if adjacent not in squares_comp[square]:
				squares_comp[adjacent].add(square)
				for point in pts:
					for pt in squares[adjacent]:
						if point.distance_to(pt) <= distance:
							merge_n_update(point, pt, composantes, forest)
							merged = True
							break #car tous les points d'un carré sont dans la même composante
					if merged:
						break

		#Comparaison des points du carré courant aux points des carrés adjacents+1
		for adjacent in outer_adjacent_sq(square, squares):
			merged = False
			if adjacent not in squares_comp[square]:
				squares_comp[adjacent].add(square)
				for point in pts:
					for pt in squares[adjacent]:
						if point.distance_to(pt) <= distance:
							merge_n_update(point, pt, composantes, forest)
							merged = True
							break
					if merged:
						break

	#Retourner la liste triée des tailles des composantes
	comp_sizes = list(composantes.values())
	comp_sizes.sort(reverse=True)

	return comp_sizes



def print_components_sizes(distance, points):
	"""
	affichage des tailles triees de chaque composante
	"""

	print(lineaire(distance, points))
	#print(naif(distance, points))



def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)

#test
main()
