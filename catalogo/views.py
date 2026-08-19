import csv
import json
from collections import Counter

from django.contrib import messages
from django.db.models import Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import tmdb
from .forms import ValoracionForm
from .models import Titulo


def inicio(request):
    titulos = Titulo.objects.all()
    vistas = titulos.filter(estado='vista')
    promedio = titulos.exclude(mi_nota=None).aggregate(avg=Avg('mi_nota'))['avg']
    total_min = sum(vistas.values_list('duracion_min', flat=True))

    datos = {
        'total': titulos.count(),
        'pendientes': titulos.filter(estado='pendiente').count(),
        'viendo': titulos.filter(estado='viendo').count(),
        'vistas': vistas.count(),
        'nota_media': round(promedio, 1) if promedio else None,
        'horas': total_min // 60,
        'favoritas': titulos.filter(favorito=True).count(),
    }

    contador = Counter()
    for g in titulos.values_list('generos', flat=True):
        for nombre in (g or '').split(', '):
            if nombre:
                contador[nombre] += 1

    nombres = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
    hoy = timezone.localdate()
    labels, counts = [], []
    for i in range(5, -1, -1):
        m, y = hoy.month - i, hoy.year
        while m < 1:
            m += 12
            y -= 1
        labels.append(nombres[m - 1])
        counts.append(vistas.filter(fecha_vista__year=y, fecha_vista__month=m).count())

    tendencias, top, generos_tmdb = [], [], []
    try:
        tendencias = tmdb.tendencias()
        top = tmdb.top_valoradas()
        for r in tendencias + top:
            r['en_catalogo'] = Titulo.objects.filter(tmdb_id=r['id'], tipo=r['tipo']).exists()
        generos_tmdb = tmdb.generos_peliculas()
    except Exception:
        pass

    return render(request, 'catalogo/inicio.html', {
        'datos': datos,
        'generos_top': contador.most_common(6),
        'recientes': titulos[:8],
        'grafica': json.dumps({'labels': labels, 'datos': counts}),
        'tendencias': tendencias,
        'top': top,
        'generos_tmdb': generos_tmdb,
    })

def ruleta_datos(request):
    genero = request.GET.get('genero', '')
    error = None
    try:
        candidatos = tmdb.descubrir(genero)
    except Exception as e:
        candidatos = []
        error = str(e)

    en_catalogo = set(Titulo.objects.filter(tipo='pelicula').values_list('tmdb_id', flat=True))
    lista = [
        {'id': c['id'], 'nombre': c['nombre'], 'poster': c['poster_url'], 'anio': c['anio'], 'voto': c['voto']}
        for c in candidatos if c['id'] not in en_catalogo
    ]
    return HttpResponse(json.dumps({'candidatos': lista, 'error': error}), content_type='application/json')


def buscar(request):
    query = request.GET.get('q', '').strip()
    resultados, error = [], None
    if query:
        try:
            resultados = tmdb.buscar(query)
            for r in resultados:
                r['en_catalogo'] = Titulo.objects.filter(tmdb_id=r['id'], tipo=r['tipo']).exists()
        except Exception:
            error = 'No se pudo contactar a TMDB. Revisa tu API key en settings.py o tu conexión.'
    return render(request, 'catalogo/buscar.html', {'q': query, 'resultados': resultados, 'error': error})


@require_POST
def agregar(request, tmdb_id, tipo):
    if tipo not in ('pelicula', 'serie'):
        return redirect('catalogo:buscar')
    if Titulo.objects.filter(tmdb_id=tmdb_id, tipo=tipo).exists():
        messages.info(request, 'Ese título ya está en tu catálogo.')
    else:
        try:
            data = tmdb.obtener(tmdb_id, tipo)
            Titulo.objects.create(**data)
            messages.success(request, f'"{data["nombre"]}" añadido a tu catálogo.')
        except Exception:
            messages.error(request, 'Error al obtener datos de TMDB.')
    return redirect(request.META.get('HTTP_REFERER', '/buscar/'))


def catalogo(request):
    titulos = Titulo.objects.all()
    estado = request.GET.get('estado', '')
    tipo = request.GET.get('tipo', '')
    q = request.GET.get('q', '').strip()
    fav = request.GET.get('fav', '')
    if estado:
        titulos = titulos.filter(estado=estado)
    if tipo:
        titulos = titulos.filter(tipo=tipo)
    if q:
        titulos = titulos.filter(nombre__icontains=q)
    if fav:
        titulos = titulos.filter(favorito=True)
    return render(request, 'catalogo/catalogo.html', {
        'titulos': titulos, 'estado': estado, 'tipo': tipo, 'q': q, 'fav': fav,
        'estados': Titulo.ESTADO_CHOICES, 'tipos': Titulo.TIPO_CHOICES,
    })


def detalle(request, pk):
    titulo = get_object_or_404(Titulo, pk=pk)
    form = ValoracionForm(request.POST or None, instance=titulo)
    if request.method == 'POST' and form.is_valid():
        t = form.save()
        if t.estado == 'vista' and not t.fecha_vista:
            t.fecha_vista = timezone.localdate()
            t.save()
        messages.success(request, 'Valoración guardada ✔')
        return redirect('catalogo:detalle', pk=pk)

    trailer_key, similares = None, []
    try:
        trailer_key = tmdb.trailer(titulo.tmdb_id, titulo.tipo)
        similares = tmdb.similares(titulo.tmdb_id, titulo.tipo)
        for r in similares:
            r['en_catalogo'] = Titulo.objects.filter(tmdb_id=r['id'], tipo=r['tipo']).exists()
    except Exception:
        pass

    return render(request, 'catalogo/detalle.html', {
        'titulo': titulo, 'form': form, 'trailer_key': trailer_key, 'similares': similares,
    })


@require_POST
def favorito(request, pk):
    t = get_object_or_404(Titulo, pk=pk)
    t.favorito = not t.favorito
    t.save()
    messages.success(request, 'Añadida a favoritas ⭐' if t.favorito else 'Quitada de favoritas.')
    return redirect('catalogo:detalle', pk=pk)


@require_POST
def eliminar(request, pk):
    get_object_or_404(Titulo, pk=pk).delete()
    messages.success(request, 'Eliminado del catálogo.')
    return redirect('catalogo:catalogo')


def exportar_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mi_catalogo.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nombre', 'Tipo', 'Año', 'Estado', 'Mi nota', 'Favorita', 'Fecha vista', 'Duración (min)', 'Géneros'])
    for t in Titulo.objects.all():
        writer.writerow([t.nombre, t.tipo, t.anio, t.get_estado_display(), t.mi_nota or '',
                         'Sí' if t.favorito else 'No', t.fecha_vista or '', t.duracion_min, t.generos])
    return response