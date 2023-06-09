import django.db.models


class QuizManager(django.db.models.Manager):
    """менеджер модели Quiz"""

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для списка викторин на главной"""
        return (
            self.get_queryset()
            .filter(is_published=True)
            .select_related('creator', 'organized_by')
            .only(
                'name',
                'description',
                'creator__username',
                'duration',
                'start_time',
                'organized_by__name',
                'is_private',
                'is_ended',
            )
            .order_by('-start_time')
        )


class UserAnswerManager(django.db.models.Manager):
    """менеджер модели UserAnswer"""

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """поля для отображения посылок пользователя"""
        return (
            self.get_queryset()
            .filter(question__quiz__is_published=True)
            .select_related('user', 'question')
            .only(
                'user__username',
                'question',
                'is_correct',
                'time_answered',
                'question__name',
            )
        )


class QuizResultsManager(django.db.models.Manager):
    """менеджер модели QuizResults"""

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """
        поля для вывода списка соревнований,
        в которых участвовал пользователь
        """
        return (
            self.get_queryset()
            .filter(quiz__is_published=True)
            .select_related('user', 'quiz')
            .only(
                'rating_before',
                'rating_after',
                'user__username',
                'quiz__name',
                'quiz__start_time',
                'solved',
                'place',
            )
        )


class QuestionManager(django.db.models.Manager):
    """менеджер модели Question"""

    def get_only_useful_list_fields(self) -> django.db.models.QuerySet:
        """только нужные поля для списка архивных вопросов"""
        return (
            self.get_queryset()
            .select_related('quiz')
            .filter(
                quiz__is_ended=True,
                quiz__is_private=False,
                quiz__is_published=True,
            )
            .only(
                'id',
                'name',
                'difficulty',
                'quiz__id',
            )
            .order_by('difficulty')
        )
