from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.ProsocialLoginView.as_view(), name="login"),
    path("logout/", views.ProsocialLogoutView.as_view(), name="logout"),
    path("password-change/", views.ProsocialPasswordChangeView.as_view(), name="password_change"),
    path(
        "password-change/done/",
        views.ProsocialPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("password-reset/", views.ProsocialPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        views.ProsocialPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        views.ProsocialPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.ProsocialPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
