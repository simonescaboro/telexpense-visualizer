from setuptools import find_packages, setup

setup(
    name="Telexspense-Visualizer",
    version="0.0.22",
    author="Simone Scaboro",
    author_email="scaboro.simone@gmail.com",
    description="A basic Streamlit app to visualize your expenses and incomes reported using the Telegram bot Telexpense",
    license="MIT",
    install_requires=[
        "streamlit",
        "gspread",
        "pandas"

        ],

)
