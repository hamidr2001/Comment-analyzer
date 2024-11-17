from hazm import word_tokenize, stopwords_list
import string
from typing import List
import pandas as pd
from nltk.corpus.reader import WordListCorpusReader



class RestaurantScoreAnalyzer:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.data = self.file_reader()
        self.tokened_list = self.word_tokenizer(2, 3, 'پیتزا')  # توکنایز کردن نظرات و سفارشات مرتبط با "پیتزا"

    def file_reader(self):
        try:
            with open(self.csv_file_path, encoding="utf-8") as f:
                return pd.read_csv(f)
        except UnicodeDecodeError:
            with open(self.csv_file_path, encoding="ISO-8859-1") as f:
                return pd.read_csv(f)

    def word_tokenizer(self, comment_col: int, order_col: int, target_word: str) -> List[List[str]]:
        """
        توکنایز کردن و فیلتر کردن نظرات مرتبط با کلمه هدف.

        Args:
            comment_col (int): شماره ستون نظرات.
            order_col (int): شماره ستون سفارشات.
            target_word (str): کلمه‌ای که باید بررسی شود (مثلاً 'پیتزا').

        Returns:
            List[List[str]]: لیستی از توکن‌های مرتبط با کلمه هدف.
        """
        punctuation = string.punctuation + '؟ ','،','!'
        stopwords_comment = set(stopwords_list())

        orders = self.data.iloc[:, order_col]
        Main_order_li = [
            [
                word for word in word_tokenize(str(order))
                if word not in stopwords_comment and word not in punctuation
            ] if pd.notna(order) else []
            for order in orders
        ]

        comments = self.data.iloc[:, comment_col]
        Main_comment_li_1 = [
            [
                word for word in word_tokenize(str(comment))
                if word not in stopwords_comment and word not in punctuation
            ] if pd.notna(comment) else []
            for comment in comments
        ]

        main_li_2 = [
            idx for idx, order in enumerate(Main_order_li)
            if target_word in order
        ]


        Main_comment_li = [Main_comment_li_1[i] for i in main_li_2]

        return Main_comment_li

    def people_rate_sum(self, colmn):
        clean_rate_column = self.data.iloc[:, colmn].fillna(3).astype(int)
        return clean_rate_column.sum() / (self.data.shape[0] * 5)

    def score_by_word(self, tokened_list, term):
        term_words = set(term.words())
        score = 0
        for tokens in tokened_list:
            for j in range(len(tokens)):
                if tokens[j] in term_words or (j > 0 and (tokens[j - 1] + ' ' + tokens[j]) in term_words):
                    score += 1
                    break
        return score

    def calculate_final_comment_score(self, score):
        score_quality = score[0] / max((score[0] + score[1]), 1)
        score_delivery = score[2] / max((score[2] + score[3]), 1)
        score_cost = score[4] / max((score[4] + score[5]), 1)
        return score_quality, score_delivery, score_cost

    def calculate_final_score(self, final_comment_score, people_rate_sum):
        return (4 * people_rate_sum) + (3 * final_comment_score[0]) + (2 * final_comment_score[1]) + final_comment_score[2]

    def analyze_scores(self):
        quality_terms = WordListCorpusReader("C:\\Users\\Notebook\\Desktop\\data\\comment", ["quality_terms.txt"])
        neg_quality_terms = WordListCorpusReader("C:\\Users\\Notebook\\Desktop\\data\\comment", ["neg_quality_terms.txt"])
        delivery_terms = WordListCorpusReader("C:\\Users\\Notebook\\Desktop\\data\\comment", ["delivery_terms.txt"])
        neg_delivery_terms = WordListCorpusReader("C:\\Users\\Notebook\\Desktop\\data\\comment", ["neg_delivery_terms.txt"])
        cost_terms = WordListCorpusReader("C:\\Users\\Notebook\\Desktop\\data\\comment", ["cost_terms.txt"])
        neg_cost_terms = WordListCorpusReader("C:\\Users\\Notebook\\Desktop\\data\\comment", ["neg_cost_terms.txt"])

        quality = self.score_by_word(self.tokened_list, quality_terms)
        neg_quality = self.score_by_word(self.tokened_list, neg_quality_terms)
        delivery = self.score_by_word(self.tokened_list, delivery_terms)
        neg_delivery = self.score_by_word(self.tokened_list, neg_delivery_terms)
        cost = self.score_by_word(self.tokened_list, cost_terms)
        neg_cost = self.score_by_word(self.tokened_list, neg_cost_terms)

        list_score = [quality, neg_quality, delivery, neg_delivery, cost, neg_cost]
        final_comment_score = self.calculate_final_comment_score(list_score)
        people_rate = self.people_rate_sum(1)
        final_score = self.calculate_final_score(final_comment_score, people_rate)

        print(f'our score to {self.csv_file_path[:-4]} is {round(final_score, 3)} from 10')


if __name__ == "__main__":
    analyzer = RestaurantScoreAnalyzer("shila.csv")
    analyzer.analyze_scores()
    analyzer = RestaurantScoreAnalyzer("sib.csv")
    analyzer.analyze_scores()







# our score to shila is 8.026 from 10
# our score to sib is 5.065 from 10
# 0.661