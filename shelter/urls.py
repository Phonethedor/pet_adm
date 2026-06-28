from django.urls import path
from .api_views import (
    PetListCreateAPIView, 
    PetDetailAPIView, 
    SpeciesListAPIView, 
    RaceListAPIView,
    AdoptionApplicationAPIView, 
    ApplicationReviewAPIView
)

urlpatterns = [
    path('species/', SpeciesListAPIView.as_view(), name='api_species_list'),
    path('races/', RaceListAPIView.as_view(), name='api_race_list'),
    path('pets/', PetListCreateAPIView.as_view(), name='api_pet_list_create'),
    path('pets/<int:pk>/', PetDetailAPIView.as_view(), name='api_pet_detail'),
    path('applications/', AdoptionApplicationAPIView.as_view(), name='api_adoption_applications'),
    path('applications/<int:pk>/review/', ApplicationReviewAPIView.as_view(), name='api_application_review'),
]