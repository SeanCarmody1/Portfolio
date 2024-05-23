import pandas as pd
import csv
from requests import get
import json
from datetime import datetime, timedelta, date
import numpy as np
from scipy.spatial.distance import euclidean, cityblock, cosine
from scipy.stats import pearsonr

import csv
import re
import pandas as pd
import argparse
import collections
import json
import glob
import math
import os
import requests
import string
import sys
import time
import xml
import random

class Recommender(object):
    def __init__(self, training_set, test_set):
        if isinstance(training_set, str):
            # the training set is a file name
            self.training_set = pd.read_csv(training_set)
        else:
            # the training set is a DataFrame
            self.training_set = training_set.copy()

        if isinstance(test_set, str):
            # the test set is a file name
            self.test_set = pd.read_csv(test_set)
        else:
            # the test set is a DataFrame
            self.test_set = test_set.copy()
    
    def train_user_cosine(self, data_set, userId):
        similarity = {}
        user_ratings = data_set[userId].dropna()
        for other_user in data_set.columns[1:]:
            if other_user != userId:
                other_ratings = data_set[other_user].dropna()
                common = user_ratings.index.intersection(other_ratings.index)
                if len(common) > 0: 
                    user_common_ratings = user_ratings.loc[common].values
                    other_common_ratings = other_ratings.loc[common].values
                    if np.linalg.norm(user_common_ratings) != 0 and np.linalg.norm(other_common_ratings) != 0:
                        sim = 1 - cosine(user_common_ratings, other_common_ratings)
                        similarity[other_user] = sim
                    else:
                        similarity[other_user] = 0
        return similarity

    def train_user_euclidean(self, data_set, userId):
        similarity = {}
        user_ratings = data_set[userId].dropna()
        for other_user in data_set.columns[1:]:
            if other_user != userId:
                other_ratings = data_set[other_user].dropna()
                common = user_ratings.index.intersection(other_ratings.index)
                if len(common) > 0:
                    user_common_ratings = user_ratings.loc[common].values
                    other_common_ratings = other_ratings.loc[common].values
                    sim = 1 / (1 + euclidean(user_common_ratings, other_common_ratings))
                    similarity[other_user] = sim
                else:
                    similarity[other_user] = 0
        return similarity


    def train_user_manhattan(self, data_set, userId):
        similarity = {}
        user_ratings = data_set[userId].dropna()
        for other_user in data_set.columns[1:]:
            if other_user != userId:
                other_ratings = data_set[other_user].dropna()
                common = user_ratings.index.intersection(other_ratings.index)
                if len(common) > 0:
                    user_common_ratings = user_ratings.loc[common].values
                    other_common_ratings = other_ratings.loc[common].values
                    sim = 1 / (1 + cityblock(user_common_ratings, other_common_ratings))
                    similarity[other_user] = sim
                else:
                    similarity[other_user] = 0
        return similarity

    def train_user_pearson(self, data_set, userId):
        similarity = {}
        user_ratings = data_set[userId].dropna()
        for other_user in data_set.columns[1:]:
            if other_user == userId:
                continue
            other_ratings = data_set[other_user].dropna()
            common = user_ratings.index.intersection(other_ratings.index)
            if not common.empty:
                user_common_ratings = user_ratings.loc[common]
                other_common_ratings = other_ratings.loc[common]
                if user_common_ratings.var() > 0 and other_common_ratings.var() > 0:
                    corr, _ = pearsonr(user_common_ratings, other_common_ratings)
                    similarity[other_user] = corr if not np.isnan(corr) else 0
                else:
                    similarity[other_user] = 0
            else:
                similarity[other_user] = 0
        return similarity

    def train_user(self, data_set, distance_function, userId):
        if distance_function == 'euclidean':
            return self.train_user_euclidean(data_set, userId)
        elif distance_function == 'manhattan':
            return self.train_user_manhattan(data_set, userId)
        elif distance_function == 'cosine':
            return self.train_user_cosine(data_set, userId)
        elif distance_function == 'pearson':
            return self.train_user_pearson(data_set, userId)
        else:
            return None
        
    def get_user_existing_ratings(self, data_set, userId):
        existing_ratings = []
        if 'movieId' in data_set.columns:
            data_set.set_index('movieId', inplace=True)
        for index, row in data_set.iterrows():
            movie_id = index 
            rating = row[userId]  
            if not pd.isna(rating): 
                existing_ratings.append((movie_id, rating))
        #print(existing_ratings)
        return existing_ratings

    def predict_user_existing_ratings_top_k(self, data_set, sim_weights, userId, k):
        existing_ratings = self.get_user_existing_ratings(data_set, userId)
        movie_ids = [movieId for movieId, _ in existing_ratings]
        top_k_users = sorted(sim_weights.items(), key=lambda x: x[1], reverse=True)[:k]
        predicted_ratings = []
        for movieId in movie_ids:
            weighted_sum = 0
            similarity_sum = 0
            for other_user, similarity in top_k_users:
                if not pd.isna(data_set.at[movieId, other_user]):
                    weighted_sum += data_set.at[movieId, other_user] * similarity
                    similarity_sum += similarity
            if similarity_sum > 0:
                predicted_rating = weighted_sum / similarity_sum
                predicted_ratings.append((movieId, predicted_rating))
        return predicted_ratings

    def evaluate(self, existing_ratings, predicted_ratings):
        existing_ratings_dict = {movie[0]: float(movie[1]) for movie in existing_ratings if movie[1] is not None}
        predicted_ratings_dict = {movie[0]: float(movie[1]) for movie in predicted_ratings if movie[1] is not None}
        common_movies = set(existing_ratings_dict.keys()) & set(predicted_ratings_dict.keys())
        mse = sum([(existing_ratings_dict[movie] - predicted_ratings_dict[movie]) ** 2 for movie in common_movies])
        rmse = math.sqrt(mse / len(common_movies)) if common_movies else float('inf')
        ratio = len(common_movies) / len(existing_ratings_dict) if existing_ratings_dict else 0
        return {'rmse': rmse, 'ratio': ratio}

    def single_calculation(self, distance_function, userId, k_values):
        user_existing_ratings = self.get_user_existing_ratings(self.test_set, userId)
        print("User has {} existing and {} missing movie ratings".format(len(user_existing_ratings), len(self.test_set) - len(user_existing_ratings)), file=sys.stderr)

        print('Building weights')
        sim_weights = self.train_user(self.training_set[self.test_set.columns.values.tolist()], distance_function, userId)

        result = []
        for k in k_values:
            print('Calculating top-k user prediction with k={}'.format(k))
            top_k_existing_ratings_prediction = self.predict_user_existing_ratings_top_k(self.test_set, sim_weights, userId, k)
            result.append((k, self.evaluate(user_existing_ratings, top_k_existing_ratings_prediction)))
        return result # list of tuples, each of which has the k value and the result of the evaluation. e.g. [(1, {'rmse':1.2, 'ratio':0.5}), (2, {'rmse':1.0, 'ratio':0.9})]

    def aggregate_calculation(self, distance_functions, userId, k_values):
        print()
        result_per_k = {}
        for func in distance_functions:
            print("Calculating for {} distance metric".format(func))
            for calc in self.single_calculation(func, userId, k_values):
                if calc[0] not in result_per_k:
                    result_per_k[calc[0]] = {}
                result_per_k[calc[0]]['{}_rmse'.format(func)] = calc[1]['rmse']
                result_per_k[calc[0]]['{}_ratio'.format(func)] = calc[1]['ratio']
            print()
        result = []
        for k in k_values:
            row = {'k':k}
            row.update(result_per_k[k])
            result.append(row)
        columns = ['k']
        for func in distance_functions:
            columns.append('{}_rmse'.format(func))
            columns.append('{}_ratio'.format(func))
        result = pd.DataFrame(result, columns=columns)
        return result
        
if __name__ == "__main__":
    recommender = Recommender("data/train.csv", "data/small_test.csv")
    print("Training set has {} users and {} movies".format(len(recommender.training_set.columns[1:]), len(recommender.training_set)))
    print("Testing set has {} users and {} movies".format(len(recommender.test_set.columns[1:]), len(recommender.test_set)))

    result = recommender.aggregate_calculation(['euclidean', 'cosine', 'pearson', 'manhattan'], "0331949b45", [1, 2, 3, 4])
    print(result)


    #    def get_user_existing_ratings(self, data_set, userId):
    #    existing_ratings = []
     #   if userId in data_set.columns:
      #      movie_ids = data_set.index
       #     for movieId in movie_ids:
        #        rating = data_set.at[movieId, userId]
         #       if not np.isnan(rating):
          #          existing_ratings.append((movieId, rating))
      #  print(existing_ratings)
    #    return existing_ratings