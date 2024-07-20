from django.apps import AppConfig


class eventAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eventApp'

    def ready(self):
        import eventApp.signals.eventSignal
        # Import the signals module to register the signal handlers
