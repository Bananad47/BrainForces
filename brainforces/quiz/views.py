import typing

import django.contrib.messages
import django.db.models
import django.http
import django.shortcuts
import django.utils.timezone
import django.views.generic

import quiz.forms
import quiz.models
import quiz.services


class QuizMixinView(django.views.generic.View):
    """дополняем контекст именем организации и проверяем доступ пользователя"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        quiz_obj = django.shortcuts.get_object_or_404(
            quiz.models.Quiz.objects.only(
                'id', 'is_private', 'start_time', 'duration'
            ),
            pk=self.kwargs['pk'],
        )
        context['quiz'] = quiz_obj
        context['can_participate'] = quiz.models.QuizResults.objects.filter(
            quiz__pk=self.kwargs['pk'], user__pk=self.request.user.pk
        ).exists()
        quiz_status = quiz_obj.get_quiz_status()
        if quiz_status == 1:
            context['can_access_questions'] = False
        elif quiz_status == 2:
            context['can_access_questions'] = context['can_participate']
        else:
            context[
                'can_access_questions'
            ] = quiz.services.user_can_access_quiz(quiz_obj, self.request.user)
        return context


class AccessToQuizMixinView(QuizMixinView):
    """проверяем доступ участника к викторине"""

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        if not context['can_access_questions']:
            raise django.http.Http404()
        return context


class QuizDetailView(django.views.generic.DetailView):
    """детальная информация о викторине"""

    queryset = quiz.models.Quiz.objects.get_only_useful_list_fields()
    template_name = 'quiz/quiz_detail.html'
    context_object_name = 'quiz'

    def get_context_data(self, *args, **kwargs) -> dict:
        """право доступа"""
        context = super().get_context_data(*args, **kwargs)
        quiz_obj = context['object']
        can_access_quiz = quiz.services.user_can_access_quiz(
            quiz_obj, self.request.user
        )
        if not can_access_quiz:
            raise django.http.Http404()
        context['can_participate'] = quiz.models.QuizResults.objects.filter(
            quiz__pk=self.kwargs['pk'], user__pk=self.request.user.pk
        ).exists()
        quiz_status = quiz_obj.get_quiz_status()
        context['quiz_status'] = quiz_status
        if quiz_status == 1:
            context['can_access_questions'] = False
        elif quiz_status == 2:
            context['can_access_questions'] = context['can_participate']
        else:
            context[
                'can_access_questions'
            ] = quiz.services.user_can_access_quiz(quiz_obj, self.request.user)
        return context


class QuestionsView(AccessToQuizMixinView, django.views.generic.ListView):
    """список вопросов в викторине"""

    template_name = 'quiz/questions.html'
    context_object_name = 'questions'

    def get_queryset(self) -> django.db.models.QuerySet:
        return (
            quiz.models.Question.objects.filter(quiz__pk=self.kwargs['pk'])
            .annotate(
                total_answers=django.db.models.Count('answers__id'),
                success_answers=django.db.models.Count(
                    'answers__id',
                    filter=django.db.models.Q(answers__is_correct=True),
                ),
            )
            .only('name')
        )


class QuestionDetailView(
    AccessToQuizMixinView, django.views.generic.DetailView
):
    """детальная информация о вопросе"""

    template_name = 'quiz/question_detail.html'
    context_object_name = 'question'
    queryset = quiz.models.Question.objects.only('name', 'text', 'difficulty')
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, *args, **kwargs) -> typing.Dict:
        """варианты ответа"""
        context = super().get_context_data(*args, **kwargs)
        variants = quiz.models.Variant.objects.filter(
            question__id=self.kwargs['question_pk']
        ).only('text')
        form = quiz.forms.AnswerForm()
        form.fields['answer'].choices = [
            (variant.id, variant.text) for variant in variants
        ]
        context['form'] = form
        return context

    def post(
        self, request: django.http.HttpRequest, pk: int, question_pk: int
    ) -> django.http.HttpResponse:
        """сохраняем ответ пользователя"""
        quiz_obj = django.shortcuts.get_object_or_404(quiz.models.Quiz, pk=pk)
        if quiz.services.user_can_access_quiz(quiz_obj, request.user):
            is_correct = quiz.models.Variant.objects.filter(
                pk=request.POST['answer'], is_correct=True
            ).exists()
            question_obj = quiz.models.Question.objects.get(pk=question_pk)
            quiz.models.UserAnswer.objects.create(
                user=request.user,
                question=question_obj,
                is_correct=is_correct,
            )
            quiz_result = quiz.models.QuizResults.objects.filter(
                quiz__pk=pk, user__pk=request.user.pk
            ).first()
            if (
                quiz_obj.get_quiz_status() == 2
                and quiz_result
                and is_correct
                and quiz.models.UserAnswer.objects.filter(
                    user__pk=request.user.pk,
                    question__pk=question_pk,
                    is_correct=is_correct,
                ).count()
                == 1
            ):
                quiz_result.solved += 1
                if quiz_obj.is_rated:
                    quiz_result.rating_after += question_obj.difficulty
                quiz_result.save()
        return django.shortcuts.redirect('quiz:user_answers_list', pk=pk)


class UserAnswersList(AccessToQuizMixinView, django.views.generic.ListView):
    """`мои посылки`"""

    template_name = 'quiz/user_answers_list.html'
    context_object_name = 'answers'
    paginate_by = 40

    def get_queryset(self) -> django.db.models.QuerySet:
        """получаем queryset"""
        useful_answer_fields = (
            quiz.models.UserAnswer.objects.get_only_useful_list_fields()
            .filter(
                question__quiz__id=self.kwargs['pk'],
                user__id=self.request.user.id,
            )
            .order_by('-time_answered')
        )
        return list(useful_answer_fields)


class StandingsList(AccessToQuizMixinView, django.views.generic.ListView):
    """положение"""

    template_name = 'quiz/standing.html'
    context_object_name = 'results'
    paginate_by = 40

    def get_queryset(self, *args, **kwargs) -> django.db.models.QuerySet:
        """получаем queryset"""
        return list(
            quiz.models.QuizResults.objects.select_related('user')
            .filter(quiz__pk=self.kwargs['pk'])
            .only('solved', 'user__username')
            .order_by('-solved')
        )


class QuizRegistrationView(django.views.generic.View):
    """регистрация на викторину"""

    def get(
        self, request: django.http.HttpRequest, pk: int
    ) -> django.http.HttpResponse:
        """регистрируем пользователя на викторину"""
        quiz_obj = django.shortcuts.get_object_or_404(quiz.models.Quiz, pk=pk)
        if (
            quiz.services.user_can_access_quiz(quiz_obj, request.user)
            and not quiz.models.QuizResults.objects.filter(
                quiz__pk=pk, user__pk=request.user.pk
            ).exists()
        ):
            quiz.models.QuizResults.objects.create(
                quiz=quiz_obj,
                user=request.user,
                rating_before=request.user.profile.rating,
                rating_after=request.user.profile.rating,
            )
            django.contrib.messages.success(request, 'Регистрация успешна!')
            return django.shortcuts.redirect(
                django.urls.reverse('quiz:quiz_detail', kwargs={'pk': pk})
            )
        else:
            raise django.http.Http404()
