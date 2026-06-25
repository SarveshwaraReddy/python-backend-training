from api.repositories.user import UserRepository

class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def get_all_users(self):
        return self.repository.get_all()

    def get_user_by_id(self, pk):
        return self.repository.get_by_id(pk)

    def create_user(self, data):
        password = data.pop('password', None)
        user = self.repository.model.objects.create_user(**data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update_user(self, pk, data):
        user = self.repository.get_by_id(pk)
        if not user:
            return None
        password = data.pop('password', None)
        updated_user = self.repository.update(user, **data)
        if password:
            updated_user.set_password(password)
            updated_user.save()
        return updated_user

    def delete_user(self, pk):
        user = self.repository.get_by_id(pk)
        if not user:
            return False
        self.repository.delete(user)
        return True
