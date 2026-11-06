class Authenticator:

    def __init__(self, storage):
        self.storage = storage

    def authenticate(self, email, password):
        users = self.storage.get_users()
        user = users.get(email)

        if user is None or user["password"] != password:
            return 401, {"error": "Invalid client credentials supplied"}

        if user["account_status"] == "locked":
            return 403, {"status": "Access Denied", "reason": "Account Suspended"}

        return 200, {"profile": user["profile"]}
