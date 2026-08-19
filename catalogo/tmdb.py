import random
import requests
from django.conf import settings

BASE = 'https://api.themoviedb.org/3'
IMG = 'https://image.tmdb.org/t/p/w342'


def _get(path, **params):
    params['api_key'] = settings.TMDB_API_KEY
    params.setdefault('language', 'es-MX')
    r = requests.get(BASE + path, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def _norm(item, tipo):
    item['tipo'] = tipo
    item['nombre'] = item.get('title') or item.get('name') or 'Sin título'
    item['poster_url'] = IMG + item['poster_path'] if item.get('poster_path') else ''
    item['anio'] = (item.get('release_date') or item.get('first_air_date') or '')[:4]
    return item


def buscar(query):
    data = _get('/search/multi', query=query, include_adult='false')
    return [_norm(r, 'pelicula' if r['media_type'] == 'movie' else 'serie')
            for r in data.get('results', []) if r.get('media_type') in ('movie', 'tv')]


def tendencias():  # ← NUEVO (1)
    data = _get('/trending/all/week')
    return [_norm(r, 'pelicula' if r['media_type'] == 'movie' else 'serie')
            for r in data.get('results', [])
            if r.get('media_type') in ('movie', 'tv') and r.get('poster_path')][:12]


def top_valoradas():  # ← NUEVO (1)
    pelis = [_norm(r, 'pelicula') for r in _get('/movie/top_rated').get('results', []) if r.get('poster_path')]
    series = [_norm(r, 'serie') for r in _get('/tv/top_rated').get('results', []) if r.get('poster_path')]
    return sorted(pelis + series, key=lambda x: x.get('vote_average', 0), reverse=True)[:12]


def similares(tmdb_id, tipo):  # ← NUEVO (3)
    ruta = 'movie' if tipo == 'pelicula' else 'tv'
    data = _get(f'/{ruta}/{tmdb_id}/recommendations')
    return [_norm(r, tipo) for r in data.get('results', []) if r.get('poster_path')][:8]


def trailer(tmdb_id, tipo):  # ← NUEVO (4)
    ruta = 'movie' if tipo == 'pelicula' else 'tv'
    data = _get(f'/{ruta}/{tmdb_id}/videos')
    vids = [v for v in data.get('results', []) if v.get('site') == 'YouTube']
    elegido = next((v for v in vids if v.get('type') == 'Trailer'), None) or (vids[0] if vids else None)
    return elegido['key'] if elegido else None


def obtener(tmdb_id, tipo):
    data = _get(f"/{'movie' if tipo == 'pelicula' else 'tv'}/{tmdb_id}")
    if tipo == 'pelicula':
        duracion = data.get('runtime') or 0
    else:
        por_episodio = (data.get('episode_run_time') or [45])[0] or 45
        duracion = por_episodio * (data.get('number_of_episodes') or 0)
    return {
        'tmdb_id': tmdb_id,
        'tipo': tipo,
        'nombre': data.get('title') or data.get('name') or 'Sin título',
        'sinopsis': data.get('overview') or 'Sin sinopsis disponible.',
        'poster': IMG + data['poster_path'] if data.get('poster_path') else '',
        'anio': (data.get('release_date') or data.get('first_air_date') or '')[:4],
        'voto_tmdb': round(data.get('vote_average', 0), 1),
        'generos': ', '.join(g['name'] for g in data.get('genres', [])),
        'duracion_min': duracion,
    }
    
def generos_peliculas():
    return _get('/genre/movie/list').get('genres', [])


def descubrir(genero=''):
    params = {'sort_by': 'popularity.desc', 'page': random.randint(1, 5)}
    if genero:
        params['with_genres'] = genero
    data = _get('/discover/movie', **params)
    resultados = [_norm(r, 'pelicula') for r in data.get('results', []) if r.get('poster_path')]
    for r in resultados:
        r['voto'] = round(r.get('vote_average', 0), 1)
    return resultados