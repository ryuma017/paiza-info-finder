from django.views import generic

import requests
from .forms import PaizaAuthenticationForm
from .module.scraper import login, get_results_data, get_user_name


class IndexView(generic.TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        form = PaizaAuthenticationForm
        context = super().get_context_data(**kwargs)
        context['form'] = form
        return context

class ResultsView(generic.ListView):
    template_name = 'main/results.html'
    context_object_name = 'data'

    # def dispatch(self, request, *args, **kwargs):
    #     print('========dispatch======')
    #     self.is_logged_in = False
    #     return super(ResultsView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_value = {
            'email': self.request.POST.get('email', default=None),
            'password': self.request.POST.get('password', default=None)
        }
        request.session['form_value'] = form_value

        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            email = form_value['email']
            password = form_value['password']

            if login(email, password):
                # self.is_logged_in = True
                queryset = {
                    'user_name': get_user_name(),
                    'results': get_results_data()
                }
                return queryset
            else:
                return None
