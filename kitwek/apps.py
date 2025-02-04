from django.apps import AppConfig


class KitwekConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kitwek'

    def ready(self):
        # Import signals in the ready method to ensure they are registered
        import kitwek.signals