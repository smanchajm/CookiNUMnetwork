"""
Module de gestion des tags.
Contient les classes et fonctions pour gérer les tags dans l'application.
"""

import time


class TagService:
    """
    Gestionnaire de tags qui encapsule la logique de gestion des tags.
    """

    def __init__(self):
        self.tags = []

    def add_tag(self, tag_name, timestamp=None):
        """
        Ajoute un tag à la liste des tags.
        """
        print(f"Adding tag: {tag_name} at timestamp: {timestamp}")
        if timestamp is None:
            tag_time = time.time()
        else:
            tag_time = timestamp

        # Stocker le timestamp en secondes et le format MM:SS pour l'affichage
        display_time = time.strftime("%M:%S", time.gmtime(tag_time))
        tag = (str(tag_time), tag_name, display_time)
        self.tags.append(tag)
        return tag

    def get_tags(self):
        return self.tags

    def set_tags(self, tags):
        self.tags = tags

    def clear_tags(self):
        self.tags = []
