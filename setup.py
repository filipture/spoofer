from setuptools import setup

APP = ['spoofer.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PIL', 'numpy', 'piexif', 'tkinterdnd2'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
