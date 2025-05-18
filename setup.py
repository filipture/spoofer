from setuptools import setup

APP = ['spoofer.py']
OPTIONS = {
    'argv_emulation': True,
    'includes': ['tkinterdnd2'],
    'packages': ['PIL', 'numpy', 'piexif'],
    'frameworks': ['/System/Library/Frameworks/Tk.framework', '/System/Library/Frameworks/Tcl.framework'],
}


setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
