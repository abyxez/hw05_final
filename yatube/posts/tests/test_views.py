from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Follow

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

    def _assert_post_has_right_attributes(self, post, id, author, group, text):
        """ Шаблонный метод для проверки post.(id,author,group). """
        self.assertEqual(
            post.id, id,
            "Post checking: post.id wrong!"
        )
        self.assertEqual(
            post.author, author,
            "Post checking: post.author wrong!"
        )
        self.assertEqual(
            post.group, group,
            "Post checking: post.group wrong!"
        )
        self.assertEqual(
            post.text, text,
            "Post checking: post.text wrong!"
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
            self.post.group,
            self.post.text
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
            self.post.group,
            self.post.text
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
            self.post.group,
            self.post.text
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
            self.post.group,
            self.post.text
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

    def test_post_created_belongs_only_to_its_group(self):
        """ Созданный пост не существует в другой группе,
            которой не принадлежит.
        """
        Group.objects.create(
            title="Useless",
            slug="Any",
            description="No need after test is done"
        )
        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": "Any"})
        )
        content_new_group = response.context["page_obj"]
        self.assertEqual(
            len(content_new_group),
            0,
            "Created post is shown in a foreign group!"
        )

    def test_follow_system_is_working_correctly(self):
        """
            Система подписки работает, как положено
            (authorized follows author).
        """
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )
        self.authorized_client.post(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author.username}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )

    def test_unfollow_system_is_working_correctly(self):
        """
            Система отписки работает, как положено
            (authorized forced follower successfully unfollows).
        """
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        self.authorized_client.post(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.author.username}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )

    def test_follow_system_shows_correct_content_for_the_follower(self):
        """
            Юзер подписался и видит контент в follow_index.
        """
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        response = self.authorized_client.get(
            reverse("posts:follow_index")
        )
        expected = response.context["page_obj"][0]
        self._assert_post_has_right_attributes(
            expected,
            self.post.id,
            self.post.author,
            self.post.group,
            self.post.text
        )

    def test_follow_system_shows_no_content_if_not_following(self):
        """
            Юзер НЕ подписался и НЕ видит контент в follow_index.
        """
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )
        response = self.authorized_client.get(
            reverse("posts:follow_index")
        )
        expected = response.context["page_obj"]
        self.assertEqual(
            len(expected),
            0,
            "Not following gets content for followers"
        )
