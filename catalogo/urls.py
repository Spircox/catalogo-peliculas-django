from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('buscar/', views.buscar, name='buscar'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('agregar/<int:tmdb_id>/<str:tipo>/', views.agregar, name='agregar'),
    path('titulo/<int:pk>/', views.detalle, name='detalle'),
    path('titulo/<int:pk>/eliminar/', views.eliminar, name='eliminar'),
    path('titulo/<int:pk>/favorito/', views.favorito, name='favorito'),
    path('exportar/', views.exportar_csv, name='exportar'),
    path('ruleta/', views.ruleta_datos, name='ruleta'),
]