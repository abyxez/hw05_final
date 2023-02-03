from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, RequestFactory

from posts.models import Group, Post
from core.views import csrf_failure

User = get_user_model()


class PostURLTests(TestCase):
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
        cls.user = User.objects.create_user(username="Test_User")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(text="Test text", author=cls.author)

    def test_non_authorized_pages_exist_at_desired_location(self):
        """ Страницы, доступные неавторизованным. """
        url_patterns = [
            "/",
            f"/group/{PostURLTests.group.slug}/",
            f"/profile/{PostURLTests.post.author}/",
            f"/posts/{PostURLTests.post.id}/",
        ]
        for pattern in url_patterns:
            with self.subTest(pattern=pattern):
                response = self.client.get(pattern)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    "Non-authorized страницы НЕ ок(",
                )

    def test_non_authorized_new_edit_post_pages_redirect(self):
        """ Переадресация со страниц, не доступных неавторизованным. """
        url_redirections = {
            "/create/": "/auth/login/?next=/create/",
            f"/posts/{PostURLTests.post.id}/edit/": "/auth/login/?next="
            f"/posts/{PostURLTests.post.id}/edit/",
        }
        for request, answer in url_redirections.items():
            with self.subTest(request=request):
                response = self.client.get(request, follow=True)
                self.assertRedirects(response, answer)

    def test_authorized_new_post_page_exists_at_desired_location(self):
        """ Страницы, доступные авторизованным. """
        response = self.authorized_client.get("/create/")
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK.value,
            "Authorized any новый пост не ок(",
        )

    def test_authorized_post_edit_page_exists_at_desired_location(self):
        response = self.author_client.get(
            f"/posts/{PostURLTests.post.id}/edit/"
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK.value,
            "Author only редактирование поста не ок(",
        )

    def test_unexisting_address_redirects_not_found_page(self):
        """ Несуществующая страница не существует 404. """
        response = self.client.get("/any_url/")
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND.value,
            "Откуда в проекте левая страница???",
        )

    def test_authorized_page_urls_use_right_templates(self):
        """ URLS соответствуют правильным шаблонам
            (authorized clients and no author).
        """
        url_patterns = {
            "/": "posts/index.html",
            f"/group/{PostURLTests.group.slug}/": "posts/group_list.html",
            f"/profile/{PostURLTests.post.author}/": "posts/profile.html",
            f"/posts/{PostURLTests.post.id}/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
            "/qwertyyylol/": "core/404.html"
        }
        for pattern, template in url_patterns.items():
            with self.subTest(pattern=pattern):
                response = self.authorized_client.get(pattern)
                self.assertTemplateUsed(response, template)

    def test_authorized_post_edit_page_uses_right_template(self):
        """ Post edit соответствует своему шаблону(author client only). """
        response = self.author_client.get(
            f"/posts/{PostURLTests.post.id}/edit/"
        )
        self.assertTemplateUsed(response, "posts/create_post.html")

    def test_403_used_custom_template_and_returned_403(self):
        """Проверяем status_code для core error-pages."""
        factory = RequestFactory()
        request = factory.get("/")
        self.assertTrue(csrf_failure(request), HTTPStatus.FORBIDDEN)
