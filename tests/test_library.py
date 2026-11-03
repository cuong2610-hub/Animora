import tempfile
import unittest
from pathlib import Path

from storage.library import LibraryStore


class LibraryStoreChecks(unittest.TestCase):
    def test_add_is_idempotent_and_remove_keeps_media_file(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            media = directory / "pet.gif"
            media.write_bytes(b"test fixture")
            store = LibraryStore(directory / "library.sqlite3")
            try:
                self.assertTrue(store.add(media))
                self.assertFalse(store.add(media))
                item = store.list()[0]
                self.assertEqual(item["path"], str(media.resolve()))
                store.remove(item["id"])
                self.assertEqual(store.list(), [])
                self.assertTrue(media.exists())
            finally:
                store.close()

    def test_sprite_sheet_metadata_is_stored(self):
        with tempfile.TemporaryDirectory() as directory:
            media = Path(directory) / "sheet.png"
            store = LibraryStore(Path(directory) / "library.sqlite3")
            try:
                self.assertTrue(store.add(media, "sprite_sheet", 4, 2, 12))
                entry = store.list()[0]
                self.assertEqual((entry["kind"], entry["columns"], entry["rows"], entry["fps"]), ("sprite_sheet", 4, 2, 12))
            finally:
                store.close()

    def test_rename_and_recent_order(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            first, second = directory / "first.gif", directory / "second.gif"
            first.touch()
            second.touch()
            store = LibraryStore(directory / "library.sqlite3")
            try:
                store.add(first)
                store.add(second)
                entries = {entry["path"]: entry for entry in store.list()}
                store.rename(entries[str(first.resolve())]["id"], "Renamed pet")
                store.touch(entries[str(second.resolve())]["id"])
                self.assertEqual(store.list_recent()[0]["path"], str(second.resolve()))
                self.assertEqual(store.get(entries[str(first.resolve())]["id"])["name"], "Renamed pet")
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
