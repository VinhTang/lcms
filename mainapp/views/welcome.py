from django.views.generic import TemplateView


class WelcomeToSpeedPyView(TemplateView):
    template_name = "mainapp/welcome.html"


class PricingView(TemplateView):
    template_name = "mainapp/pricing.html"
