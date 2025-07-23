from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
from django.contrib.auth import logout
from .models import Matiere, Serie, UserProfile, Chapitre, Cours


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        identifiant = request.POST['identifiant']
        password = request.POST['password']
        tentative_key = f"tentative_{identifiant}"

        # Vérifie le nombre de tentatives
        nb_tentatives = cache.get(tentative_key, 0)
        if nb_tentatives >= 3:
            messages.warning(request, "Trop de tentatives. Inscrivez-vous.")
            return redirect('register')

        try:
            # Cherche par username, email ou téléphone
            user = User.objects.filter(username=identifiant).first()

            if not user:
                user = User.objects.filter(email=identifiant).first()

            if not user:
                profile = UserProfile.objects.filter(telephone=identifiant).first()
                user = profile.user if profile else None

            if not user:
                cache.set(tentative_key, nb_tentatives + 1, timeout=300)  # expire après 5 minutes
                messages.error(request, "Aucun utilisateur avec ces identifiants.")
                return redirect('login')

            # Vérifie le mot de passe
            user_auth = authenticate(username=user.username, password=password)
            if user_auth:
                login(request, user_auth)
                cache.delete(tentative_key)  # Réinitialise les tentatives
                return redirect('dashboard')
            else:
                cache.set(tentative_key, nb_tentatives + 1, timeout=300)
                messages.error(request, "Mot de passe incorrect.")
                return redirect('login')

        except Exception as e:
            messages.error(request, "Une erreur est survenue.")
            return redirect('login')

    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        serie_id = request.POST.get('serie')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Nom d'utilisateur déjà utilisé.")
            return redirect('register')

        try:
            serie = Serie.objects.get(id=serie_id)
        except Serie.DoesNotExist:
            messages.error(request, "Série invalide.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Vérifier si un UserProfile existe déjà pour cet utilisateur
        if not hasattr(user, 'userprofile'):
            UserProfile.objects.create(user=user, serie=serie, telephone=telephone)
        else:
            # Mettre à jour le profil existant si nécessaire
            user.userprofile.serie = serie
            user.userprofile.telephone = telephone
            user.userprofile.save()

        login(request, user)
        return redirect('dashboard')

    series = Serie.objects.all()
    return render(request, 'register.html', {'series': series})

@login_required
def dashboard(request): 
    user_profile = request.user.userprofile
    matieres = Matiere.objects.filter(series_autorisees=user_profile.serie)

    return render(request, 'dashboard.html', {
        'user_profile': user_profile,
        'matieres': matieres
    })

@login_required
def chapitres_par_matiere(request, matiere_id):
    matiere = get_object_or_404(Matiere, id=matiere_id)
    chapitres = matiere.chapitres.all()

    return render(request, 'chapitres.html', {
        'matiere': matiere,
        'chapitres': chapitres
    })

@login_required
def cours_detail(request, chapitre_id):
    chapitre = get_object_or_404(Chapitre, id=chapitre_id)
    cours = get_object_or_404(Cours, chapitre=chapitre)

    return render(request, 'cours_detail.html', {
        'chapitre': chapitre,
        'cours': cours
    })

def logout_view(request):
    logout(request)
    return redirect('index')


