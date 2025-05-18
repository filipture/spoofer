from setuptools import setup

APP = ['spoofer.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PIL', 'numpy', 'piexif', 'tkinterdnd2'],
    'plist': {
        'CFBundleIdentifier': 'com.filipturek.spoofer',
        'CFBundleName': 'Spoofer',
        'CFBundleShortVersionString': '1.0',
        'CFBundleVersion': '1.0',
        'LSUIElement': False,
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
