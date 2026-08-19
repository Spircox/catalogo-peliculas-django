\# 🎬 Catálogo Personal de Películas y Series



Un "Letterboxd" personal construido con Django que consume la \*\*API de TMDB\*\* en español.

Descubre, cataloga, califica y obtén estadísticas de tu vida cinéfila. Incluye una

ruleta \*"¿Qué veo hoy?"\* que sugiere películas que \*\*no tienes\*\*, filtradas por género.



> 🔗 \*\*Demo en vivo:\*\* \*(próximamente)\*



\## ✨ Funcionalidades



\- 🔍 Búsqueda de películas y series en TMDB (resultados en español)

\- 🎲 \*\*Ruleta "¿Qué veo hoy?"\*\*: sugiere películas populares del género elegido que NO están en tu catálogo

\- 📺 Tráilers de YouTube embebidos

\- 🎬 Recomendaciones de títulos similares

\- ⭐ Favoritas, calificación personal (1-10), comentarios y fecha de visionado

\- 📊 Estadísticas: horas de cine, vistas por mes (Chart.js) y géneros top

\- 🔥 Tendencias de la semana y top histórico

\- 💾 Exportación del catálogo a CSV

\- 🌙 Modo oscuro persistente



\## 🛠️ Stack tecnológico



\*\*Python · Django · SQLite · Bootstrap 5 · Chart.js · API REST de TMDB (requests) · JavaScript (fetch)\*\*



\## 🚀 Ejecución local



```bash

git clone https://github.com/TU\_USUARIO/catalogo-peliculas-django.git

cd catalogo-peliculas-django

python -m venv venv

source venv/bin/activate      # Windows: venv\\Scripts\\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver

```



⚙️ \*\*Configuración:\*\* obtén una API key gratis en \[themoviedb.org/settings/api](https://www.themoviedb.org/settings/api) y pégala en `settings.py` → `TMDB\_API\_KEY`.



\## 📚 Lo que aprendí construyéndolo



\- Consumo de APIs REST externas (parámetros, normalización de respuestas JSON)

\- Endpoints propios que devuelven JSON para el frontend

\- Manejo defensivo de fallos de API (la app funciona aunque TMDB no responda)

\- Agregaciones y estadísticas basadas en fechas

\- Modales dinámicos y `fetch` con Django



\## ✍️ Autor



\*\*Scrodia\*\* · \[GitHub](https://github.com/Spircox)
