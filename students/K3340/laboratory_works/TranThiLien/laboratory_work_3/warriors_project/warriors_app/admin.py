from django.contrib import admin

from .models import Profession, Skill, SkillOfWarrior, Warrior

admin.site.register([Warrior, Profession, Skill, SkillOfWarrior])
