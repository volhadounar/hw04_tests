from django.test import TestCase, Client
from .models import Post
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import get_object_or_404
# Create your tests here.

User = get_user_model()


class TestStringMethods(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345')

    def test_ifRegister(self):
        response = self.client.post(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_ifRegUserCanCreatePost(self):
        self.client.login(username='sarah', password='12345')
        response = self.client.post('/new/', {'text': '¡Qué mala suerte!'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.post('/new/', {'text': '¡Qué mala suerte!'},
                                    follow=True)
        self.assertNotEqual(response.status_code, 404)
        final_url = reverse('login')
        found = False
        for item in response.redirect_chain:
            if final_url in item[0]:
                found = True
                break
        self.assertTrue(found)

    def test_ifCreatePost(self):
        self.client.login(username='sarah', password='12345')
        new_text = 'Mi nueva nota.'
        self.client.post('/new/', {'text': new_text}, follow=True)
        response = self.client.get('/')
        self.assertContains(response, new_text)
        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, new_text)
        my_post = get_object_or_404(Post, author=self.user, text=new_text)
        my_url = f'/{self.user.username}/{my_post.id}/edit/'
        response = self.client.get(my_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, my_post.text)
        self.client.logout()

    def test_ifResultEditingPost(self):
        self.client.login(username='sarah', password='12345')
        new_post = Post.objects.create(author=self.user, text="Это мой пост!")
        my_url = f'/{self.user.username}/{new_post.id}/edit/'
        new_text = '¡no te permito qué me hables así!'
        r = self.client.post(my_url, {'text': new_text}, follow=True)
        self.assertEqual(r.status_code, 200)
        response = self.client.get(f'/{self.user.username}/{new_post.id}/')
        self.assertContains(response, new_text)
        self.client.logout()

    def test_length(self):
        self.assertEqual(len('yatube'), 6)
    # def test_show_msg(self):
        # действительно ли первый аргумент — True?
        # self.assertTrue(False, msg="Важная проверка на истинность")

    def tearDown(self):
        pass
