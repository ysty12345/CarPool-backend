from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class MyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 在这里实现你的认证逻辑
        # 例如，检查请求头中的Token
        token = request.query_params.get('token')
        if token == 'your_token':
            return None, None  # 返回用户和认证对象

        raise AuthenticationFailed({'code': 401, 'detail': 'Invalid token.'})

    def authenticate_header(self, request):
        # 返回一个用于WWW-Authenticate头的字符串
        return 'Token realm="api"'
