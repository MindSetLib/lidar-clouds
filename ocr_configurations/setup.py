import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ocr-configurations",
    version="v0.1.19",
    author="Шихалиев Фрэнк Олегович",
    author_email="frank@mind-set.ru",
    description="Общие утилиты используемые для микросервисов OCR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["ocr-configurations"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 5 - Production/Stable",
    ],
    python_requires=">=3.9",
)
