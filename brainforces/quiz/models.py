import ckeditor.fields

import django.db.models

import users.models


class Tag(django.db.models.Model):
    """модель тега для викторины"""

    is_published = django.db.models.BooleanField(
        verbose_name='опубликован',
        help_text='Опубликован тег или нет',
        default=True,
    )
    name = django.db.models.CharField(
        verbose_name='имя тега', help_text='Введите имя тега', max_length=150
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self) -> str:
        """строковое представление"""

        return self.name[:20]


class Quiz(django.db.models.Model):
    """модель викторины"""

    class Statuses(django.db.models.IntegerChoices):
        NOT_STARTED = 1, 'Не начата'
        GOES_ON = 2, 'Идет'
        FINISHED = 3, 'Закончена'

    creator = django.db.models.ForeignKey(
        users.models.User,
        verbose_name='пользователь',
        on_delete=django.db.models.CASCADE,
        related_name='user_creator',
        help_text='пользователь, который создал викторину',
        null=True,
    )

    name = django.db.models.CharField(
        max_length=50,
        help_text='Напишите название викторины',
        verbose_name='название викторины',
    )

    status = django.db.models.IntegerField(
        choices=Statuses.choices,
        help_text='Поставьте статус викторины',
        default=1,
        verbose_name='статус',
    )

    description = ckeditor.fields.RichTextField(
        help_text='Создайте описание для Вашей викторины',
        verbose_name='описание',
    )

    start_time = django.db.models.DateTimeField(
        help_text='Назначьте стартовое время для Вашей викторины',
        null=True,
        blank=True,
        verbose_name='стартовое время',
    )

    duration = django.db.models.IntegerField(
        help_text='Укажите продолжительность викторины в минутах',
        null=True,
        blank=True,
        verbose_name='продолжительность',
    )

    users = django.db.models.ManyToManyField(
        users.models.User,
        verbose_name='пользователи зарегистрированные на викторину',
        help_text='Укажите пользователей,'
        'которые зарегистрировались на викторину',
        related_name='quiz_users',
    )

    class Meta:
        verbose_name = 'викторина'
        verbose_name_plural = 'викторины'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]


class Question(django.db.models.Model):
    """модель вопроса"""

    name = django.db.models.CharField(
        max_length=100,
        help_text='Напишите название вопроса',
        verbose_name='название вопроса',
    )

    text = ckeditor.fields.RichTextField(
        help_text='Напишите вопрос', verbose_name='текст'
    )

    quiz = django.db.models.ForeignKey(
        Quiz,
        verbose_name='викторина',
        on_delete=django.db.models.CASCADE,
        related_name='quiz_question',
        help_text='викторина, к которой относится вопрос',
    )

    difficulty = django.db.models.PositiveSmallIntegerField(
        verbose_name='сложность',
        help_text='сложность вопроса',
        default=1,
    )

    tags = django.db.models.ManyToManyField(
        Tag,
        related_name='question_tags',
        verbose_name='теги вопроса',
        help_text='выберите теги вопроса',
    )

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]


class Variant(django.db.models.Model):
    """модель варианта ответа"""

    text = django.db.models.CharField(
        max_length=150,
        help_text='Напишите вариант ответа',
        verbose_name='ответ',
    )

    question = django.db.models.ForeignKey(
        Question,
        verbose_name='вопрос',
        on_delete=django.db.models.CASCADE,
        related_name='question_answer',
        help_text='вопрос, к которому относится вариант ответа',
    )

    class Meta:
        verbose_name = 'вариант ответа'
        verbose_name_plural = 'варианты ответов'

    def __str__(self) -> str:
        """строковое представление"""
        return self.text[:20]


class UserAnswer(django.db.models.Model):
    """модель ответа пользователя"""

    user = django.db.models.ForeignKey(
        users.models.User,
        verbose_name='пользователь',
        on_delete=django.db.models.CASCADE,
        related_name='useranswer_user',
        help_text='пользователь, который дал ответ',
    )

    question = django.db.models.ForeignKey(
        Question,
        verbose_name='вопрос',
        help_text='вопрос на который пользователь дал ответ',
        related_name='useranswer_question',
        on_delete=django.db.models.CASCADE,
    )

    is_correct = django.db.models.BooleanField(
        verbose_name='правильность ответа',
        help_text='правильный ответ или нет',
    )

    class Meta:
        verbose_name = 'ответ пользователя'
        verbose_name_plural = 'ответы пользователей'
