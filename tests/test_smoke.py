import os
import glob
import text_plistlib.plistlib

self_path = os.path.dirname(os.path.realpath(__file__))

def test_read():
    sources = glob.glob(os.path.join(self_path, "*.strings")) + glob.glob(os.path.join(self_path, "*.plist"))
    for s in sources:
        with open(s, "rb") as f:
            d = text_plistlib.plistlib.load(f, fmt=text_plistlib.plistlib.PF.FMT_TEXT)
            print(s)
            print(d)
