from pathlib import Path
import tempfile
import unittest

from openpilot.sunnypilot.formosalink.training_models import save_selection,selected_url,validate_url


class SelectionTest(unittest.TestCase):
  def test_explicit_version_persists_without_loading_or_executing_model(self):
    with tempfile.TemporaryDirectory() as temporary:
      root=Path(temporary)
      self.assertEqual(selected_url(root),'')
      url='https://github.com/TonyBinheWu/sunnypilot/releases/download/n16-20261117-abc/manifest.json'
      save_selection(url,root)
      self.assertEqual(selected_url(root),url)
      self.assertEqual(list(root.iterdir()),[root/'training-selection.json'])

  def test_untrusted_publisher_and_mutable_urls_rejected(self):
    for url in ('http://github.com/TonyBinheWu/sunnypilot/releases/download/n16-a/manifest.json',
      'https://evil.example/manifest.json','https://github.com/other/repo/releases/download/n16-a/manifest.json',
      'https://github.com/TonyBinheWu/sunnypilot/releases/latest/download/manifest.json'):
      with self.assertRaises(ValueError):
        validate_url(url)


if __name__=='__main__':
  unittest.main()
