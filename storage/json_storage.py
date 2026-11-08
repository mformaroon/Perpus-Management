from abc import ABC, abstractmethod
import json
import os

class BaseStorage(ABC):
    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def get_all(self) -> list:
        pass

    @abstractmethod
    def get_by_id(self, id_val) -> object:
        pass

    @abstractmethod
    def create(self, obj) -> bool:
        pass

    @abstractmethod
    def update(self, id_val, obj) -> bool:
        pass

    @abstractmethod
    def delete(self, id_val) -> bool:
        pass

class JsonStorage(BaseStorage):
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        dir_name = os.path.dirname(self._file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if not os.path.exists(self._file_path):
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)

    def load(self) -> list:
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return []

    def save(self, data: list):
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving to {self._file_path}: {e}")
