from django.urls import path

from apps.knowledge import views

app_name = "knowledge"

urlpatterns = [
    path("vault/", views.vault_list, name="vault"),
    path("collections/", views.collection_list, name="collection_list"),
    path("collections/new/", views.collection_create, name="collection_create"),
    path("collections/<uuid:public_id>/", views.collection_detail, name="collection_detail"),
    path(
        "collections/<uuid:public_id>/add-clip/<uuid:clip_id>/",
        views.collection_add_clip,
        name="collection_add_clip",
    ),
    path(
        "collections/<uuid:public_id>/add-post/<uuid:post_id>/",
        views.collection_add_post,
        name="collection_add_post",
    ),
    path("tags/", views.tag_browse, name="tag_browse"),
    path("tags/<slug:slug>/", views.tag_detail, name="tag_detail"),
    path("search/", views.search, name="search"),
    path("clips/post/<uuid:post_id>/", views.clip_post, name="clip_post"),
    path("clips/post/<uuid:post_id>/selection/", views.clip_selection, name="clip_selection"),
]
