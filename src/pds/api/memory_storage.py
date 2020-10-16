import pathlib
import io
import errno
import os


from cryptography.fernet import Fernet
from opera.storage import Storage


class SafeMemoryStorage(Storage):

    @classmethod
    def create(cls, instance_path: str = None) -> "SafeMemoryStorage":
        return SafeMemoryStorage(
            pathlib.Path(instance_path or cls.DEFAULT_INSTANCE_PATH)
            )

    def __init__(self, path):
        super().__init__(path)
        self.key = Fernet.generate_key()
        self.memStorage = {}

    def write(self, content, *path):
        f = Fernet(self.key)
        encrypted_data = f.encrypt(content.encode())
        *subpath, name = path
        dir_path = self.path / pathlib.PurePath(*subpath)
        self.memStorage[str(dir_path / name)] = io.BytesIO(encrypted_data)

    def read(self, *path):
        f = Fernet(self.key)
        dir_path = self.path / pathlib.PurePath(*path)
        if self.exists(*path):
            encrypted_data = self.memStorage[str(dir_path)].getvalue()
            return f.decrypt(encrypted_data).decode()
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), str(dir_path))

    def exists(self, *path):
        return str(self.path / pathlib.PurePath(*path)) in self.memStorage

    def remove(self, *path):
        mem = self.memStorage.pop(str(self.path / pathlib.PurePath(*path)), None)
        if mem is not None:
            mem.close()

    def remove_all(self):
        for path in self.memStorage.keys:
            self.remove(*path)

