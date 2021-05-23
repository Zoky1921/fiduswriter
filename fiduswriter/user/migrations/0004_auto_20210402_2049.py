# Generated by Django 3.1.4 on 2021-04-02 18:49

from django.db import migrations
from django.conf import settings


def teammembers_to_contacts(apps, schema_editor):
    TeamMember = apps.get_model('user', 'TeamMember')
    team_members = TeamMember.objects.all().iterator()
    for team_member in team_members:
        member = team_member.member
        leader = team_member.leader
        leader.contacts.add(member)
        member.contacts.add(leader)
    TeamMember.objects.all().delete()


def contacts_to_teammembers(apps, schema_editor):
    User = apps.get_model('user', 'User')
    TeamMember = apps.get_model('user', 'TeamMember')
    users = User.objects.all().iterator()
    for user in users:
        for contact in user.contacts.all():
            TeamMember.objects.get_or_create(
                leader=user,
                member=contact
            )
        user.contacts.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20210411_1440'),
    ]

    operations = [
        migrations.RunPython(teammembers_to_contacts, contacts_to_teammembers),
    ]
