import setuptools

with open("README.md", "r", encoding='utf-8') as readme:
    long_description = readme.read()

install_requires = []
with open("requirements.txt", "rt", encoding='utf-8') as f:
    for line in f.readlines():
        install_requires.append(line.replace('==', '=').replace('\n', ''))


setuptools.setup(
    name="embulkpy",
    version="0.0.1",
    author="deadkorskiy",
    description="Python wrapper for Embulk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Deadkorskiy/embulkpy.git",
    install_requires=install_requires,
    keywords=['embulk', 'etl'],
    license="wtfpl",
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
