from django.db import migrations


def create_initial_user(apps, schema_editor):
    User = apps.get_model("api", "User")

    User.objects.get_or_create(
        email="admin@example.com",
        defaults={
            "username": "doron",
            "password": "doron2002",
            "auth_token": None,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
    ("api", "0002_order"),
]

    operations = [
        migrations.RunPython(create_initial_user),
    ]
