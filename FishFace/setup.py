from distutils.core import setup

setup(
    name='FishFace',
    version='0.0.0',
    author='Wil Langford',
    author_email='fishface@langford.ws',
    packages=['cvwrangler'],
    scripts=[],
    url='',
    license='LICENSE.txt',
    description='Package to find fish in images.',
    long_description=open('README.txt').read(),
    install_requires=[
        "opencv >= 2.3.1",
        "numpy >= 1.6.2",
        "argparse >=1.2.1",
        "scipy >= 0.10.1",
        "PIL >=1.1.7",
        "wxPython >= 2.8.12"
        ],
)
