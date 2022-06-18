import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="PPKunOfficial",
  version="0.0.1",
  author="PP",
  author_email="2426181331@qq.com",
  description="123云盘接口",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/PPKunOfficial/123PanApi",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)