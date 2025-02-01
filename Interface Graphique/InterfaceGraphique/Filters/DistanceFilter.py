import numpy as np

class DistanceFilter:
    def distance_manhattan(self, vec_i, vec_j):
        """
        Calcule de la distance de Manhattan entre deux vecteurs.

        Arguments:
        vec_i -- premier vecteur
        vec_j -- deuxième vecteur

        Retourne:
        Distance de Manhattan arrondie à 4 décimales.
        """
        return round(np.sum(np.abs(vec_i - vec_j)), 4)

    def distance_euclidienne(self, vec_i, vec_j):
        """
        Calcule de la distance Euclidienne entre deux vecteurs.

        Arguments:
        vec_i -- premier vecteur
        vec_j -- deuxième vecteur

        Retourne:
        Distance Euclidienne arrondie à 4 décimales.
        """
        return round(np.sqrt(np.sum((vec_i - vec_j) ** 2)), 4)

    def distance_tchebychev(self, vec_i, vec_j):
        """
        Calcule de la distance de Tchebychev entre deux vecteurs.

        Arguments:
        vec_i -- premier vecteur
        vec_j -- deuxième vecteur

        Retourne:
        Distance de Tchebychev arrondie à 4 décimales.
        """
        return round(np.max(np.abs(vec_i - vec_j)), 4)

    def distance_intersection_histogrammes(self, vec_i, vec_j):
        """
        Calcule de l'intersection normalisée entre deux histogrammes.

        Arguments:
        vec_i -- premier vecteur (histogramme)
        vec_j -- deuxième vecteur (histogramme)

        Retourne:
        Intersection des histogrammes arrondie à 4 décimales.
        """
        total_sum = np.sum(vec_j)
        if total_sum == 0:
            return 0
        return round(np.sum(np.minimum(vec_i, vec_j)) / total_sum, 4)

    def distance_chi_2(self, vec_i, vec_j):
        """
        Calcule de la distance Chi-carré entre deux vecteurs.

        Arguments:
        vec_i -- premier vecteur
        vec_j -- deuxième vecteur

        Retourne:
        Distance Chi-carré arrondie à 4 décimales.
        """
        epsilon = 1e-10
        denominator = vec_i + vec_j + epsilon
        chi_square = np.sum(np.where(denominator != 0, (vec_i - vec_j)**2 / denominator, 0))
        return round(chi_square, 4)

    def distance_minkowshki(self, vec_i, vec_j, p=None):
        """
        Calcule de la distance de Minkowski entre deux vecteurs.

        Arguments:
        vec_i -- premier vecteur
        vec_j -- deuxième vecteur
        p -- paramètre de Minkowski, par défaut p=1/2

        Retourne:
        Distance de Minkowski arrondie à 4 décimales.
        """
        p = p if p else 1/2
        return round(np.sum(np.abs(vec_i - vec_j) ** (1/p)), 4)