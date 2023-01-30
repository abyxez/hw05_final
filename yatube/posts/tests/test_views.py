from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPageTests(TestCase):
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
        cls.post = Post.objects.create(
            text="Test text", author=cls.author, group=cls.group
        )

    def _assert_post_has_right_attributes(self, post, id, author, group):
        """ Шаблонный метод для проверки post.(id,author,group). """
        self.assertEqual(
            post.id, id,
            "Post checking: post.text wrong!"
        )
        self.assertEqual(
            post.author, author,
            "Post checking: post.author wrong!"
        )
        self.assertEqual(
            post.group, group,
            "Post checking: post.group wrong!"
        )

    def test_post_pages_show_correct_templates(self):
        """Шаблоны формируются по указанным name и namespace."""
        url_patterns = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.author.username}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            ): "posts/post_detail.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.id}
            ): "posts/create_post.html",
        }
        for pattern, template in url_patterns.items():
            with self.subTest(pattern=pattern):
                response = self.author_client.get(pattern)
                self.assertTemplateUsed(response, template)

    def test_index_page_gets_correct_context(self):
        """ Шаблон index сформирован с правильным контекстом. """
        response = self.authorized_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        self._assert_post_has_right_attributes(
            first_object,
            self.post.id,
            self.post.author,
            self.post.group
        )

    def test_group_list_page_gets_correct_context(self):
        """ Шаблон group сформирован с правильным контекстом. """
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        first_object = response.context["page_obj"][0]
        post_group_slug_0 = first_object.group.slug
        self.assertEqual(
            post_group_slug_0,
            self.group.slug,
            "Group list context.slug bad!")
        self._assert_post_has_right_attributes(
            first_object,
            self.post.id,
            self.post.author,
            self.post.group
        )

    def test_profile_page_gets_correct_context(self):
        """ Шаблон profile сформирован с правильным контекстом. """
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.author.username})
        )
        first_object = response.context["page_obj"][0]
        self._assert_post_has_right_attributes(
            first_object,
            self.post.id,
            self.post.author,
            self.post.group
        )

    def test_post_detail_page_gets_correct_context(self):
        """ Шаблон post_detail сформирован с правильным контекстом. """
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        first_object = response.context["post"]
        self._assert_post_has_right_attributes(
            first_object,
            self.post.id,
            self.post.author,
            self.post.group
        )

    def test_post_create_page_gets_correct_context(self):
        """ Шаблон post_create(authorized only)
            сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(
                    form_field, expected, "Post create form context bad!"
                )

    def test_post_edit_page_gets_correct_context(self):
        """ Шаблон post_edit(author only) сформирован
            с правильным контекстом.
        """
        response = self.author_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(
                    form_field, expected, "Post edit form context bad!"
                )
