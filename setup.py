from setuptools import setup, find_packages

# Charger les dépendances depuis requirements.txt
def load_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name='iono_seismic_ai',   
    version='0.1.0',       
    description='RAG for searching events in the ionosphere and seismic activity.',   
    author='SB',       
    author_email='rag.agentic@gmail.com',  
    url='https://github.com/rag-agentic/iono_seismic_AI',   
    packages=find_packages(),   
    install_requires=load_requirements(),  
    python_requires=">=3.10",   
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)
