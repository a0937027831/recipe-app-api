from django.urls import path
from user import views


app_name = 'user'

# as_view() 

urlpatterns = [
    path('create/',views.CreateUserView.as_view(),name='create'),
    path('token/',views.CreateTokenView.as_view(),name='token'),
    path('me/',views.ManageUserView.as_view(),name='me'),
]

# url中使用了as_view()方法後，返回的閉包會根據請求的方式到對應的視圖函數中找以請求方式命名的函數進行執行。