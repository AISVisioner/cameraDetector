# from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


# class IndexTemplateView(LoginRequiredMixin, TemplateView):
class IndexTemplateView(TemplateView):

    template_name = "index.html"
