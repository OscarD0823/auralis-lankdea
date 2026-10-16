import json
import pytest
from lankdea.storage import LocalVaultRepository, VaultLockedError
from lankdea.models import new_item
from lankdea.editor_draft import EncryptedEditorDraft


def test_pending_credentials_survive_restart_encrypted_and_commit_clears_atomically(tmp_path):
    path = tmp_path / "vault.json"
    repository = LocalVaultRepository(path)
    password = "Prueba local suficientemente larga 2026"
    repository.create(password)
    values = {"service": "Sitio ficticio", "password": "BORRADOR-PRIVADO-93842"}
    draft = EncryptedEditorDraft(repository, "device:password:new", lambda: values.copy())
    draft.flush()
    assert values["password"] not in path.read_text()
    assert values["password"] not in path.with_suffix(".json.bak").read_text()
    repository.lock()
    with pytest.raises(VaultLockedError):
        repository.editor_draft(draft.key)
    restored = LocalVaultRepository(path)
    restored.unlock(password)
    assert restored.editor_draft(draft.key) == values
    assert restored.snapshot()["items"] == []
    restored.upsert_item(new_item("password", service=values["service"], password=values["password"]), draft_key=draft.key)
    assert restored.editor_draft(draft.key) is None
    assert len(restored.snapshot()["items"]) == 1
