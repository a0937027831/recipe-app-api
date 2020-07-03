from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')

class PublicTagsApiTests(TestCase):
    # test the publicly available tags API

    def setUp(self):
        # 在測試testcase下 setUp 將會在測試時先行調用 這樣其他方法不須 重複code 做初始化動作
        self.client = APIClient()
    
    def test_login_required(self):
        # test that login is required for retrieving tags
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
class PrivateTagsApiTests(TestCase):
    # test the authorized user tags API

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_restrieve_tags(self):
        # test retrieving tags
        Tag.objects.create(user=self.user,name='Vegan')
        Tag.objects.create(user=self.user,name='Dessert')
        res = self.client.get(TAGS_URL)
        tags =Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many = True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
    
    def test_tags_limited_to_user(self):
        # test that tags returned arre for tje authenticated user
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        # test creating a new tag
        payload = {'name':'test tag'}
        self.client.post(TAGS_URL,payload)
        exists = Tag.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        # test creating a new tag with invalid payload
        payload = {'name':''}
        res = self.client.post(TAGS_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)