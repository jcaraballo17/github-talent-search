from django.views.generic import ListView

from search_interface.github_scraper import Scraper


class SearchResultsView(ListView):
    context_object_name = 'search_results'
    template_name = 'search_interface/results_list.html'

    def get_queryset(self):
        # TODO: get criteria parameters from url
        search_criteria = {
            'language': "Python",
            'ignore_forks': True,
            'last_update': '2017-01-01',
            'project_title': 'django',
            'country_codes': ['br', 'mx', 'co', 'ar', 'pe', 'do', 'pr'],
            'stars_lower_bound': 10,
            'stars_upper_bound': 200
        }
        scraper = Scraper()
        return scraper.get_projects(search_criteria)
