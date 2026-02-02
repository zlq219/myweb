from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId


class User(UserMixin):
    def __init__(self, user_data):
        if user_data is None:
            return None

        self.id = str(user_data['_id']) if '_id' in user_data else None
        self.username = user_data.get('username', '')
        self.email = user_data.get('email', '')
        self.password_hash = user_data.get('password_hash', '')
        self.avatar = user_data.get('avatar', '')
        self.bio = user_data.get('bio', '')
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.updated_at = user_data.get('updated_at', datetime.utcnow())

        # 使用下划线前缀避免与Flask-Login的property冲突
        self._is_active = user_data.get('is_active', True)
        self._is_admin = user_data.get('is_admin', False)
        self.email_verified = user_data.get('email_verified', False)

    # Flask-Login需要的属性（只读）
    @property
    def is_active(self):
        return self._is_active and self.email_verified

    @property
    def is_admin(self):
        return self._is_admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'bio': self.bio,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self._is_active,
            'is_admin': self._is_admin,
            'email_verified': self.email_verified,
            'password_hash': self.password_hash
        }

    # 【关键修复】确保以下静态方法都存在：
    @staticmethod
    def get_by_id(mongo, user_id):
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
            return None
        except:
            return None

    @staticmethod
    def get_by_email(mongo, email):
        user_data = mongo.db.users.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def get_by_username(mongo, username):
        user_data = mongo.db.users.find_one({'username': username})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def create(mongo, user_data):
        user = User(user_data)
        if 'password' in user_data:
            user.set_password(user_data['password'])

        user_dict = user.to_dict()
        user_dict['created_at'] = datetime.utcnow()
        user_dict['updated_at'] = datetime.utcnow()

        result = mongo.db.users.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    @staticmethod
    def update(mongo, user_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )

    @staticmethod
    def get_all(mongo, page=1, per_page=20):
        skip = (page - 1) * per_page
        users = mongo.db.users.find().skip(skip).limit(per_page)
        return [User(user) for user in users]

    @staticmethod
    def get_count(mongo):
        return mongo.db.users.count_documents({})