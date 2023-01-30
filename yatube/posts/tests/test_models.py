from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, FIRST_LETTERS_SHOWN

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        group_title = group.title
        self.assertEqual(str(group), group_title, "GROUP_TITLE BAD")
        title__first_fifteen = post.text[:FIRST_LETTERS_SHOWN]
        self.assertEqual(
            str(post), title__first_fifteen, "POST_FIRST_15_LETTERS BAD"
        )
