import parameterized

import django.conf
import django.core
import django.test
import django.urls
import django.utils

import quiz.models
import users.models


class UserProfileTests(django.test.TestCase):
    """тестируем профиль пользователя"""

    def setUp(self) -> None:
        """подготовка к тестированию, создание тестовых данных"""
        self.test_user1 = users.models.User.objects.create(
            username='testuser1',
            is_staff=True,
            is_superuser=True,
            email='testuser1@gmail.com',
        )
        self.test_user1.set_password('password')
        self.test_user1.save()
        users.models.Profile.objects.create(user=self.test_user1)

        self.test_user2 = users.models.User.objects.create(
            username='testuser2',
            is_staff=False,
            is_superuser=False,
            email='testuser2@gmail.com',
        )
        self.test_user2.set_password('password')
        self.test_user2.save()
        users.models.Profile.objects.create(user=self.test_user2)

        super().setUp()

    @parameterized.parameterized.expand([[1, 200], [2, 200], [3, 404]])
    def test_user_profile_information_status_code(
        self, pk: int, expected: int
    ) -> None:
        """тестируем статус код страницы с информацией о пользователе"""
        response = django.test.Client().get(
            django.urls.reverse('users:profile', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, expected)

    @parameterized.parameterized.expand([[1, 200], [2, 200], [3, 404]])
    def test_user_profile_answers_status_code(
        self, pk: int, expected: int
    ) -> None:
        """тестируем статус код страницы с ответами пользователя"""
        response = django.test.Client().get(
            django.urls.reverse('users:answers', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, expected)

    def test_user_profile_answers_context(self) -> None:
        """теcтируем контекст страницы с ответами пользователя"""
        response = django.test.Client().get(
            django.urls.reverse('users:answers', kwargs={'pk': 1})
        )
        self.assertIn('answers', response.context)

    def test_user_profile_answers_correct_model(self) -> None:
        """тестируем правильный объект модели на странице с ответами"""
        response = django.test.Client().get(
            django.urls.reverse('users:answers', kwargs={'pk': 1})
        )
        self.assertTrue(
            all(
                map(
                    lambda x: isinstance(x, quiz.models.UserAnswer),
                    response.context['answers'],
                )
            )
        )

    def test_users_can_change_their_profile(self) -> None:
        """тестирование возможности изменить профиль"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            {'username': 'testuser2', 'password': 'password'},
        )
        response = client.get(
            django.urls.reverse('users:profile_change', kwargs={'pk': 2})
        )
        self.assertEqual(response.status_code, 200)

    def test_users_can_not_change_other_profiles(self) -> None:
        """пользователь не может менять чужие профили"""
        client = django.test.Client()
        client.post(
            django.urls.reverse('users:login'),
            {'username': 'testuser2', 'password': 'password'},
        )
        response = client.get(
            django.urls.reverse('users:profile_change', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, 404)

    @parameterized.parameterized.expand([[1, 200], [2, 200], [3, 404]])
    def test_user_profile_quizzes_status_code(
        self, pk: int, expected: int
    ) -> None:
        """тестируем статус код страницы с викторинами пользователя"""
        response = django.test.Client().get(
            django.urls.reverse('users:quizzes', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, expected)

    def test_user_profile_quizzes_context(self) -> None:
        """теcтируем контекст страницы с викторинами пользователя"""
        response = django.test.Client().get(
            django.urls.reverse('users:quizzes', kwargs={'pk': 1})
        )
        self.assertIn('results', response.context)

    def test_user_profile_quizzes_correct_model(self) -> None:
        """тестируем правильный объект модели на странице с викторинами"""
        response = django.test.Client().get(
            django.urls.reverse('users:quizzes', kwargs={'pk': 1})
        )
        self.assertTrue(
            all(
                map(
                    lambda x: isinstance(x, quiz.models.QuizResults),
                    response.context['results'],
                )
            )
        )

    def tearDown(self) -> None:
        """удаление тестовых данных"""
        users.models.User.objects.all().delete()
        super().tearDown()
