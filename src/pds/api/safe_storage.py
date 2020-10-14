import pathlib

from cryptography.fernet import Fernet
from opera.storage import Storage


class SafeStorage(Storage):

    @classmethod
    def create(cls, key, instance_path: str = None) -> "SafeStorage":
        return SafeStorage(
            pathlib.Path(instance_path or cls.DEFAULT_INSTANCE_PATH), key
            )

    def __init__(self, path, key):
        super().__init__(path)
        self.key = key

    def write(self, content, *path):
        f = Fernet(self.key)
        encrypted_data = f.encrypt(content.encode())        
        *subpath, name = path
        dir_path = self.path / pathlib.PurePath(*subpath)
        dir_path.mkdir(exist_ok=True, parents=True)
        with open((dir_path / name), "wb") as file:
            file.write(encrypted_data)

    def read(self, *path):
        f = Fernet(self.key)
        with open(self.path / pathlib.PurePath(*path), "rb") as file:
            encrypted_data = file.read()

        return f.decrypt(encrypted_data).decode()
