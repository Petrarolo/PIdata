from distutils.core import setup
setup(
  name = 'PIdata',         # How you named your package folder (MyLib)
  packages = ['pidata'],   # Chose the same as "name"
  version = '0.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'An easy-to-use connector for the OSI PI historian',   # Give a short description about your library
  author = 'Venanzio Petrarolo',                   # Type in your name
  author_email = 'petrarolov@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/petrarolo/PIdata',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/Petrarolo/PIdata/archive/0.2.tar.gz',    # I explain this later on
  keywords = ['OSI', 'PI', 'Connector', 'Historian', 'Process', 'Control'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pythonnet',
          'numpy',
          'dateutil',
          'pandas',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Manufacturing',      # Define that your audience are developers
    'Topic :: Scientific/Engineering :: Information Analysis',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',
  ],
)