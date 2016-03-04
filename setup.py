from setuptools import setup

setup(name='my-python',
      version='1.0.1',
      description='hello 123',
      url='https://github.com/raymondchen/python-learning',
      author='chenjinying',
      author_email='415683089@qq.com',
      packages=['spider_jd', 'analyze'],
      install_requires=[
            'pybluez',
            'pandas',
            'MySQL-python'
      ],
      zip_safe=False
      )