import tornado.web
import tornado.escape

from app.accounts.models import user_model
from app.accounts.handlers.login_handler import BaseHandler


class SignUpHandler(BaseHandler):
    def post(self):
        self.set_header("Content-Type", "text/plain")

        sign_up_data = tornado.escape.json_decode(self.request.body)

        input_user_name = sign_up_data.get('user_name', None)
        input_password = sign_up_data.get('user_password', None)

        if not input_user_name or not input_password:
            sign_up_info_json = {'success': False, 'error_msg': 'empty user name or password'}
            return self.write(sign_up_info_json)

        user_name = user_model.get_user_name(input_user_name)

        if user_name:
            sign_up_info_json = {'success': False, 'error_msg': 'already existing user name'}
            return self.write(sign_up_info_json)

        user_model.add_user(input_user_name, input_password)

        sign_up_info_json = {'success': True, 'error_msg': ''}
        self.write(sign_up_info_json)
