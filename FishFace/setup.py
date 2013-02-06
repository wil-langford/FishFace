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
        "opencv >= 2.3.1"
        ],
)
