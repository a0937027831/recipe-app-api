from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe,Tag, Ingredient
from recipe.serializers import RecipeSerializer,RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    # return recipe detail URL
    return reverse('recipe:recipe-detail',args=[recipe_id])

def sample_tag(user,name='Main course'):
    # Create and return a sample tag
    return Tag.objects.create(user=user,name=name)

def sample_ingredient(user,name='Cinnamon'):
    # Create and return a sample ingredient
    return Ingredient.objects.create(user=user,name=name)

def sample_recipe(user,**params):
    # **將參數轉成字典
    # create and return a sample recipe
    defaults = {
        'title':'Sample recipe',
        'time_minutes':10,
        'price':5.00
    }
    # 這裡update 是指用戶傳近來的參數 可以覆蓋defaults值或新增進來
    defaults.update(params)
    # 在調用函數時有用兩個星號會產生相反的效果 將字典轉成參數
    return Recipe.objects.create(user=user,**defaults)

class PublicRecipeApiTests(TestCase):
    # Test unauthenticated recipe API access

    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        # test unauthentication is required
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)  

class PrivateRecipeApiTests(TestCase):
    # Test unauthenticated recipe API access
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_recips(self):
        # test retrieving a list of recipes
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
    
    def test_recipe_limited_to_user(self):
        # test retrieving recipes for user
        user2 = get_user_model().objects.create_user(
            'other@loandonappdev.com',
            'password123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data,serializer.data)

    def test_view_recipe_detail(self):
        # Test viewing a recipe detail
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data,serializer.data)

    def test_create_basic_recipe(self):
        # Test creating recipe
        payload = {
            'title':'Chocolate cheesecake',
            'time_minutes': 30,
            'price':5.00
        }
        res = self.client.post(RECIPES_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        # 遍歷字典 key欄位的值 比對 
        # python getattr 可以返回一个对象属性值
        for key in payload.keys():
            self.assertEqual(payload[key],getattr(recipe,key))
    
    def test_create_recipe_with_tags(self):
        # test creating a recipe with tags
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title' : 'Avocado lime cheesecake',
            'tags' : [tag1.id ,tag2.id],
            'time_minutes':60,
            'price':20.00    
        }
        res = self.client.post(RECIPES_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(),2)
        self.assertIn(tag1,tags)
        self.assertIn(tag2,tags)

    def test_create_recipe_with_ingredients(self):
        # test creating recipe with ingredients
        ingredient1 = sample_ingredient(user=self.user,name='Prawns')
        ingredient2 = sample_ingredient(user=self.user,name='Ginger')
        payload = {
            'title':'Thau prawn red curry',
            'ingredients':[ingredient1.id,ingredient2.id],
            'time_minutes':20,
            'price':7.00
        }
        res = self.client.post(RECIPES_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(),2)
        self.assertIn(ingredient1,ingredients)
        self.assertIn(ingredient2,ingredients)
