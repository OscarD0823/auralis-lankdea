from __future__ import annotations
from typing import Callable
from .storage import LocalVaultRepository


class EncryptedEditorDraft:
    """A draft remains inside the existing encrypted vault, never in a plaintext file."""
    def __init__(self, repository: LocalVaultRepository, key: str, values: Callable[[], dict[str, str]]):
        self.repository, self.key, self.values = repository, key, values
        self.active = True
        self.last = repository.editor_draft(key)

    def flush(self):
        if not self.active:
            return
        values = self.values()
        if values != self.last:
            self.repository.save_editor_draft(self.key, values)
            self.last = values.copy()

    def finish(self):
        self.active = False
