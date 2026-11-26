from rest_framework import serializers

from .models import Profession, Skill, SkillOfWarrior, Warrior


# ---------------- Простые сериализаторы ----------------

class WarriorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warrior
        fields = '__all__'


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ['id', 'title', 'description']


class ProfessionCreateSerializer(serializers.Serializer):
    """Низкоуровневый сериализатор из примера (serializers.Serializer)."""
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()

    def create(self, validated_data):
        profession = Profession(**validated_data)
        profession.save()
        return profession


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'title']


class SkillCreateSerializer(serializers.Serializer):
    """Практическое задание: добавление скила (аналогично профессии)."""
    title = serializers.CharField(max_length=120)

    def create(self, validated_data):
        return Skill.objects.create(**validated_data)


class SkillOfWarriorSerializer(serializers.ModelSerializer):
    """Привязка умения к воину с уровнем (ассоциативная сущность)."""

    class Meta:
        model = SkillOfWarrior
        fields = '__all__'


# ---------------- Примеры связанных сериализаторов из практики ----------------

class SkillRelatedSerializer(serializers.ModelSerializer):
    warrior_skils = WarriorSerializer(many=True)

    class Meta:
        model = Skill
        fields = ['title', 'warrior_skils']


class WarriorRelatedSerializer(serializers.ModelSerializer):
    skill = serializers.SlugRelatedField(read_only=True, many=True, slug_field='title')

    class Meta:
        model = Warrior
        fields = '__all__'


class WarriorDepthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warrior
        fields = '__all__'
        depth = 1


# ---------------- Сериализаторы для заданий ----------------

class WarriorWithProfessionSerializer(serializers.ModelSerializer):
    """Воин + полная информация о профессии."""
    profession = ProfessionSerializer(read_only=True)
    race = serializers.CharField(source='get_race_display', read_only=True)

    class Meta:
        model = Warrior
        fields = ['id', 'name', 'race', 'level', 'profession']


class SkillWithLevelSerializer(serializers.ModelSerializer):
    """Умение воина вместе с уровнем освоения (из SkillOfWarrior)."""
    id = serializers.IntegerField(source='skill.id')
    title = serializers.CharField(source='skill.title')

    class Meta:
        model = SkillOfWarrior
        fields = ['id', 'title', 'level']


class WarriorWithSkillsSerializer(serializers.ModelSerializer):
    """Воин + полная информация об умениях (с уровнем освоения)."""
    skills = SkillWithLevelSerializer(source='warrior_skill', many=True, read_only=True)
    race = serializers.CharField(source='get_race_display', read_only=True)

    class Meta:
        model = Warrior
        fields = ['id', 'name', 'race', 'level', 'skills']


class WarriorNestedSerializer(serializers.ModelSerializer):
    """Воин по id: профессия и умения (пример WarriorNestedSerializer из практики)."""
    profession = ProfessionSerializer(read_only=True)
    skills = SkillWithLevelSerializer(source='warrior_skill', many=True, read_only=True)
    race = serializers.CharField(source='get_race_display', read_only=True)

    class Meta:
        model = Warrior
        fields = ['id', 'name', 'race', 'level', 'profession', 'skills']


class WarriorUpdateSerializer(serializers.ModelSerializer):
    """Редактирование воина: имя, раса, уровень, профессия (по id)."""

    class Meta:
        model = Warrior
        fields = ['id', 'name', 'race', 'level', 'profession']
