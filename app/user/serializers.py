from django.contrib.auth import get_user_model ,authenticate
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

class UserSerializer(serializers.ModelSerializer):
    # Serializer for the users object
    class Meta:
        model = get_user_model()
        fields = ['email','password','name']
        extra_kwargs = {'password':{'write_only':True,'min_length':5 }}
 
    def create(self,validated_data):
        # Create a new user with encrypted password and return it
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self,instance,validated_data):
        # Update a user ,settinig the password correctly and return it
        password = validated_data.pop('password',None)
        # pop 在這資料列表 提取password 並替換掉
        user = super().update(instance,validated_data)
        # super() 是去呼叫 繼承serializers.ModelSerializer 裡的 update 方法
        if password:
            user.set_password(password)
            user.save()
        # 在這設定進去叫安全
        return user


    

class AuthTokenSerializer(serializers.Serializer):
    # Serializer for the user authentication object
    # trim_whitespace 清除空格
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace = False
    )

    #attrs <-上面的列表變成json傳入 
    def validate(self,attrs):
        # Validate and authenticate the user
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request = self.context.get('request'),
            username = email,
            password = password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg,code='authentication')

        attrs['user'] = user
        return attrs
    


