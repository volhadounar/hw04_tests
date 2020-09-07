from django.test import TestCase, Client
from .models import Post, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings


User = get_user_model()


class TestStringMethods(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_with_unlogged = Client()
        self.sarah = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345')
        self.user_sarah = User.objects.get(username=self.sarah)
        self.client.force_login(self.user_sarah)
        self.group = Group.objects.create(title='Grupo de prueba',
                                          slug='prueba',
                                          description='Mucho gusto')

    def test_if_register(self):
        response = self.client.post(f'/{self.sarah}/')
        self.assertEqual(response.status_code, 200)

    def check_param(self, url, args, user, my_text):
        post = get_object_or_404(Post, text=my_text)
        self.assertEqual(post.author, user)
        self.assertEqual(post.group, self.group)
        response = self.client.get(url, kwargs_view=args)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, my_text)

    def test_if_logged_user_can_create_post(self):
        url_new = reverse('new_post')
        old_user_objcnt = self.user_sarah.posts.count()
        my_text = '¡Qué mala suerte!'
        response = self.client.post(url_new, {'text': my_text,
                                    'group': self.group.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        new_cnt = Post.objects.filter(author=self.user_sarah).count()
        self.assertNotEqual(old_user_objcnt, new_cnt)
        final_url = reverse('index')
        self.check_param(final_url, '', self.user_sarah, my_text)

    def test_if_not_logged_user_can_create_post(self):
        url_new = reverse('new_post')
        old_post_cnt = Post.objects.filter(author=self.sarah).count()
        my_text = '¡Qué faena!'
        response = self.client_with_unlogged.post(url_new,
                                                  {'text': my_text,
                                                   'group': self.group.id,
                                                   'author': self.sarah},
                                                  follow=True)
        self.assertEqual(response.status_code, 200)
        new_post_cnt = Post.objects.filter(author=self.sarah).count()
        self.assertEqual(old_post_cnt, new_post_cnt)
        self.assertRedirects(response, '%s?next=%s' %
                             (settings.LOGIN_URL, url_new))

    def get_list_of_urls(self, user, my_text):
        post = get_object_or_404(Post, text=my_text, author=user)
        url_main = reverse('index')
        kwargs_edit = {'username': user.username, 'post_id': post.id}
        url_edit = reverse('post_edit', kwargs=kwargs_edit)
        kwargs_view = {'username': user.username, 'post_id': post.id}
        url_view = reverse('post', kwargs=kwargs_view)
        return {url_main: '', url_edit: kwargs_edit, url_view: kwargs_view}

    def test_if_create_post(self):
        self.client.force_login(self.user_sarah)
        old_user_objcnt = self.user_sarah.posts.count()
        new_text = 'Mi nueva nota.'
        url = reverse('new_post')
        response = self.client.post(url, {'text': new_text,
                                          'group': self.group.id},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        new_cnt = Post.objects.filter(author=self.user_sarah).count()
        self.assertNotEqual(old_user_objcnt, new_cnt)
        list_to_check = self.get_list_of_urls(self.user_sarah, new_text)
        for url, args in list_to_check.items():
            self.check_param(url, args, self.user_sarah, new_text)
        self.client.logout()

    def test_if_result_editing_post(self):
        new_post = Post.objects.create(author=self.user_sarah,
                                       text='Это мой пост!')
        old_user_objcnt = self.user_sarah.posts.count()
        changed_text = '¡no te permito qué me hables así!'
        kwargs_edit = {'username': self.sarah, 'post_id': new_post.id}
        url_edit = reverse('post_edit', kwargs=kwargs_edit)
        r = self.client.post(url_edit, {'text': changed_text,
                                        'group': self.group.id},
                             follow=True)
        self.assertEqual(r.status_code, 200)
        new_cnt = Post.objects.filter(author=self.user_sarah).count()
        self.assertEqual(old_user_objcnt, new_cnt)
        list_to_check = self.get_list_of_urls(self.user_sarah, changed_text)
        for url, args in list_to_check.items():
            self.check_param(url, args, self.user_sarah, changed_text)

    def tearDown(self):
        self.client.logout()
