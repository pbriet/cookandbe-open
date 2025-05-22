from django.db.models           import Count

from articles.models            import Article

from common.date                import today

from diet_mgr.models            import Diet

from optalim.settings           import SITE_BASE_URL

from recipe_mgr.models          import Recipe, FoodTag

def generate_sitemap():
    """
    Returns the XML content of sitemap.xml
    """
    res =  '<?xml version="1.0" encoding="UTF-8"?>\n'
    res += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url, options in iter_urls():
        res += '  <url>\n'
        res += '    <loc>%s</loc>\n' % url
        res += '    <lastmod>%s</lastmod>\n' % options.get('lastmod', str(today()))
        res += '    <changefreq>%s</changefreq>\n' % options.get('changefreq', 'monthly')
        res += '    <priority>%s</priority>\n' % options.get('priority', 0.5)
        res += '  </url>\n'

    res += '</urlset>'
    return res


def iter_urls(base_url=None):
    """
    Iterate on URLs to index (tuples (URL -> options for sitemap))
    """
    if base_url is None:
        base_url = "%s" % SITE_BASE_URL
    yield base_url,                 {'priority': 1}
    yield "%s/team"         % base_url, {'priority': 0.1,}
    # yield "%s/toutes-nos-recettes" % base_url, {'priority': 0.1,}
    yield "%s/nutrition"    % base_url, {'priority': 0.5,}
    yield "%s/partners"     % base_url, {'priority': 0.6,}
    yield "%s/how"          % base_url, {'priority': 0.5,}
    yield "%s/marque-blanche" % base_url, {'priority': 1}
    #yield "%s/tariffs"      % base_url, {'priority': 0.2,}
    # Disabled until existing publications and new urls (.../question)
    # yield "%s/publication"  % base_url, {'priority': 0.1,}
    yield "%s/articles"     % base_url, {'priority': 0.3, 'changefreq': 'weekly'}

    recipes = Recipe.objects.filter(internal = False, status__gte=Recipe.STATUS_PUBLISHED)
    recipes = recipes.annotate(nb_ingredients = Count('ingredients')).filter(nb_ingredients__gte=4)
    nb_published_recipes = recipes.count()

    diets = Diet.objects.filter(enabled = True)
    for diet in diets:
        yield "%s/menus/%s" % (base_url, diet.url_key), {'priority': 1}

    # for i in range(nb_published_recipes // 10 + 1):
    #     yield "%s/toutes-nos-recettes/%i" % (base_url, i), {'priority': 0.1, 'changefreq': 'weekly'}

    for recipe in recipes.only('url_key').order_by('id').all():
        yield "%s/recettes/recette-%s" % (base_url, recipe.url_key), {}

    for article in Article.objects.only('url_key').filter(published=True).order_by('id').all():
        yield "%s/articles/%s" % (base_url, article.url_key), {}

    # Disabled until existing publications and new urls (.../question)
    # for publication in Publication.objects.only('url_key').filter(public=True).order_by('creation_date').all():
        # yield "%s/publication/%s" % (base_url, publication.url_key), {}

    for food_tag in FoodTag.objects.only('url_key').order_by('id').all():
        yield "%s/recettes/a-base-de/%s" % (base_url, food_tag.url_key), {'priority': 0.3}
