from django.contrib import admin

from apps.ai_coach.models import (
    AIIntervention,
    CivilityPromptEvent,
    ContentReviewEvent,
    ReflectionJournalEntry,
    SentimentSnapshot,
    ThreadSummary,
)

admin.site.register(SentimentSnapshot)
admin.site.register(ThreadSummary)
admin.site.register(ReflectionJournalEntry)
admin.site.register(AIIntervention)
admin.site.register(CivilityPromptEvent)
admin.site.register(ContentReviewEvent)
