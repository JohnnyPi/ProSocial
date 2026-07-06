from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render


def health_check(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


def home_redirect(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    return redirect("accounts:login")


def error_400(request: HttpRequest, exception=None) -> HttpResponse:
    return render(request, "errors/400.html", status=400)


def error_403(request: HttpRequest, exception=None) -> HttpResponse:
    return render(request, "errors/403.html", status=403)


def error_404(request: HttpRequest, exception=None) -> HttpResponse:
    return render(request, "errors/404.html", status=404)


def error_500(request: HttpRequest) -> HttpResponse:
    return render(request, "errors/500.html", status=500)
