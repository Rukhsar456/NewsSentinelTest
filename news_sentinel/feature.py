import numpy as np  
import pandas as pd  

import os
import re
import nltk



from nltk.corpus import stopwords

stop_words = stopwords.words('english')

from nltk.stem import WordNetLemmatizer

nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()


def get_all_query(title, author):
    total = str(title) + str(author)
    total = [total]
    return total
