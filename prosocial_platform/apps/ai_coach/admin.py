from django.contrib import admin

from apps.ai_coach.models import AIIntervention, ReflectionJournalEntry, SentimentSnapshot, ThreadSummary

admin.site.register(SentimentSnapshot)
admin.site.register(ThreadSummary)
admin.site.register(ReflectionJournalEntry)
admin.site.register(AIIntervention)
