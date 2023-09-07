from setuptools import setup, find_packages

setup(name='s-py-icd',
      version='1.0',
      description='Python ICD serializer',
      author='PA',
      #install_requires=['xml'],
      packages=find_packages(),
      namespace_packages=find_packages(),
      package_data={}
     )
