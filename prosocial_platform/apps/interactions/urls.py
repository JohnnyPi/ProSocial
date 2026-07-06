from django.urls import path

from apps.interactions import views

app_name = "interactions"

urlpatterns = [
    path(
        "posts/<uuid:post_id>/replies/create/",
        views.reply_create,
        name="reply_create",
    ),
    path("replies/<uuid:reply_id>/edit/", views.reply_edit, name="reply_edit"),
    path("replies/<uuid:reply_id>/delete/", views.reply_delete, name="reply_delete"),
    path("posts/<uuid:post_id>/react/", views.react_post, name="react_post"),
    path("replies/<uuid:reply_id>/react/", views.react_reply, name="react_reply"),
    path(
        "posts/<uuid:post_id>/context-note/", views.context_note_create, name="context_note_create"
    ),
    path("context-notes/<int:note_id>/rate/", views.context_note_rate, name="context_note_rate"),
    path("notifications/", views.notification_list, name="notifications"),
    path(
        "notifications/<int:notification_id>/read/",
        views.notification_read,
        name="notification_read",
    ),
    path("notifications/read-all/", views.notification_read_all, name="notification_read_all"),
    path("posts/<uuid:post_id>/hide/", views.hide_post_view, name="hide_post"),
    path("settings/hidden-posts/", views.hidden_posts_list, name="hidden_posts"),
    path("profiles/<slug:handle>/mute/", views.mute_user_view, name="mute_user"),
    path("profiles/<slug:handle>/block/", views.block_user_view, name="block_user"),
    path("profiles/<slug:handle>/unmute/", views.unmute_user_view, name="unmute_user"),
    path("profiles/<slug:handle>/unblock/", views.unblock_user_view, name="unblock_user"),
    path("posts/<uuid:post_id>/report/", views.report_post, name="report_post"),
    path("replies/<uuid:reply_id>/report/", views.report_reply, name="report_reply"),
]
