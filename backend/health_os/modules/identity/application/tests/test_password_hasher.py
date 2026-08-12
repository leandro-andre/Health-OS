from health_os.modules.identity.application import PasswordHasher


class StubPasswordHasher:
    def hash(self, plain_password: str) -> str:
        return f"hashed:{plain_password}"

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return password_hash == self.hash(plain_password)


def test_password_hasher_accepts_expected_contract() -> None:
    password_hasher: PasswordHasher = StubPasswordHasher()

    password_hash = password_hasher.hash("correct-password")

    assert password_hash == "hashed:correct-password"
    assert password_hasher.verify("correct-password", password_hash)
    assert not password_hasher.verify("wrong-password", password_hash)
