from django.apps import AppConfig


class ProfileSectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profile_section'

    def ready(self):
        import profile_section.signals  # noqa: F401
