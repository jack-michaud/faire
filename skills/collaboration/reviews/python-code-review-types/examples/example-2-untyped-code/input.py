class UserManager:
    def __init__(self, database_url):
        self.db_url = database_url
        self.users = {}
        self.admins = []

    def add_user(self, user_id, username, email):
        if user_id in self.users:
            return False
        self.users[user_id] = {"username": username, "email": email}
        return True

    def get_user(self, user_id):
        return self.users.get(user_id)

    def make_admin(self, user_id):
        if user_id in self.users and user_id not in self.admins:
            self.admins.append(user_id)
            return True
        return False

    def get_all_admins(self):
        return [self.users[uid] for uid in self.admins if uid in self.users]

    def filter_users(self, predicate):
        return [user for user in self.users.values() if predicate(user)]
