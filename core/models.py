from django.db import models
from django.contrib.auth.models import User

# Série (S1 à S8)
class Serie(models.Model):
    code = models.CharField(max_length=2, unique=True)  # Ex: 'S1', 'S2', etc.
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} ||| {self.description}"

# Profil utilisateur avec la série
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    serie = models.ForeignKey(Serie, on_delete=models.SET_NULL, null=True)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        if self.serie:
            return f"{self.user.username} - ({self.serie.code})"
        else:
            return f"{self.user.username} (Aucune série)"



# Matière : Physique, Chimie, etc.
class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    series_autorisees = models.ManyToManyField(Serie, related_name='matieres')

    def __str__(self):
        return f"{self.nom}"

# Chapitre dans une matière
class Chapitre(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='chapitres')
    titre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.matiere.nom} - {self.titre}"

# Cours PDF et tutoriel
class Cours(models.Model):
    chapitre = models.ForeignKey(Chapitre, on_delete=models.CASCADE, related_name='cours')
    pdf_cours = models.FileField(upload_to='cours_pdfs/')
    tutoriel = models.FileField(upload_to='tutoriels/', null=True, blank=True)

    def __str__(self):
        return f"Cours: {self.chapitre.titre}"
    
    class Meta:
        verbose_name_plural = "Cours"
