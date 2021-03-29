from django.views.generic import ListView

from search_interface.forms import SearchCriteriaForm
from search_interface.github_scraper import Scraper


class SearchResultsView(ListView):
    context_object_name = 'search_results'
    template_name = 'search_interface/results_list.html'

    def get_queryset(self):
        # TODO: get criteria parameters from url
        form = SearchCriteriaForm(self.request.GET)
        if not form.is_valid():
            return []
        search_criteria = form.cleaned_data

        scraper = Scraper()
        return scraper.get_projects(search_criteria)
