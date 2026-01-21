class User:
    def __init__(
        self,
        full_name,
        email,
        password=None,
        role="learner",
        provider="local"
    ):
        self.full_name = full_name
        self.email = email
        self.password = password          # None for Google users
        self.role = role                  # learner | admin
        self.provider = provider          # local | google

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "provider": self.provider
        }
