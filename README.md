---
title: "Sean Carmody's CS Portfolio"
author: "Sean Carmody"
date: "`r format(Sys.time(), '%B %d, %Y')`"
output:
  html_document:
    toc: true
    toc_depth: 2
    theme: cerulean
    highlight: tango
---

# Introduction

Welcome to my portfolio! I am Sean Carmody, a Research Scientist and Computational Biology graduate with a passion for data analysis, scientific research, and software development. You can find my professional profile on [LinkedIn](https://www.linkedin.com/in/sean-carmody-b7a54b252/).

---

# Resume

You can view my resume [here](ResumeS.pdf).

---

# Projects

## Project 1: Calculations
This project involves various calculations implemented in Python.

**Code Snippet:**

\`\`\`python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
\`\`\`

**Full Code:** [calculations.py](calculations.py)

## Project 2: Recommender System
Developed a movie recommender system using collaborative filtering.

**Code Snippet:**

\`\`\`python
import numpy as np

def recommend(user_ratings, movie_data):
    # Dummy recommendation logic
    recommended_movies = np.argsort(user_ratings)[::-1]
    return movie_data[recommended_movies]
\`\`\`

**Full Code:** [recommender.py](recommender.py)

## Project 3: Movie Database
Created a movie database interface using Python and SQL.

**Code Snippet:**

\`\`\`python
import sqlite3

def connect_db(db_name):
    conn = sqlite3.connect(db_name)
    return conn

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE movies (id INTEGER PRIMARY KEY, title TEXT, genre TEXT, year INTEGER)''')
    conn.commit()
\`\`\`

**Full Code:** [movie_db.py](movie_db.py)

## Project 4: Pittsburgh Bikes Analysis
Analyzed bike share data in Pittsburgh using Jupyter Notebook and Python.

**Code Snippet:**

\`\`\`python
import pandas as pd

def load_data(file_path):
    return pd.read_csv(file_path)

def analyze_data(df):
    return df.describe()
\`\`\`

**Jupyter Notebook:** [bikes_pgh_data.ipynb](bikes_pgh_data.ipynb)

**Full Code:** [pittbikes.py](pittbikes.py)

---

# Contact

Feel free to reach out to me through the following channels:

- **Email:** spc53@pitt.edu
- **Phone: ** 240-217-3091
- **LinkedIn:** [Sean Carmody](https://www.linkedin.com/in/sean-carmody-b7a54b252/)
- **Lab Website:** [Shemesh Lab](https://www.shemeshlab.com/)

Thank you for visiting my portfolio!
