from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.views import POSTS_SHOWN

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Test group",
            slug="test-slug",
            description="Test description"
        )
        cls.author = User.objects.create_user(username="Test_Author")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.posts = []
        for i in range(15):
            cls.posts.append(
                Post.objects.create(
                    text=f"Test text {i}", author=cls.author, group=cls.group
                )
            )

    def test_first_page_contains_ten_records(self):
        """Паджинатор показывает 10 первых постов на первой странице."""
        url_patterns = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse(
                "posts:profile",
                kwargs={"username": self.author.username}
            ),
        ]
        for page in url_patterns:
            with self.subTest(page=page):
                response = self.author_client.get(page)
                self.assertEqual(
                    len(response.context["page_obj"]),
                    POSTS_SHOWN,
                    "First page paginator bad!"
                )

    def test_second_page_contains_five_records(self):
        """Паджинатор показывает 5 последних постов на второй странице."""
        url_patterns = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse(
                "posts:profile",
                kwargs={"username": self.author.username}
            ),
        ]
        for page in url_patterns:
            with self.subTest(page=page):
                response = self.author_client.get(page + "?page=2")
                self.assertEqual(
                    len(response.context["page_obj"]),
                    (len(self.posts) - POSTS_SHOWN),
                    "Second page paginator bad!"
                )
