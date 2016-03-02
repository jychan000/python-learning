from setuptools import setup

setup(name='spider-jd',
      version='1.0.1',
      description='hello 123',
      url='https://github.com/raymondchen/python-learning/tree/master/spider_jd',
      author='jychan',
      author_email='415683089@qq.com',
      packages=['spider_jd'],
      install_requires=[
            'pybluez',
            'pandas',
            'MySQL-python'
      ],
      zip_safe=False
      )