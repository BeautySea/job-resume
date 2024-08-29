from collections import Counter
from itertools import zip_longest

from textstat import textstat


def calculate_percentage(text, count):
    total_sentences = textstat.sentence_count(text=text)
    percentage = count / total_sentences * 100
    processed_percentage = 100 if percentage >= 100 else percentage
    return processed_percentage


def calculate_job_title_score(job_title_count, total_work_experience_count):
    calculated_score = job_title_count / total_work_experience_count * 100
    processed_percentage = 100 if calculated_score >= 100 else calculated_score
    return processed_percentage


def calculate_ats_keyword_score(keyword_score, category_keyword_score,
                                general_keyword_score, email_score, phone_score, linkedin_score, job_title_score,
                                readability_score, keyword_stuffing_score, category_keyword_stuffing_score):
    email_score = 100 if email_score == "Yes" else 0
    phone_score = 100 if phone_score == "Yes" else 0
    linkedin_score = 100 if linkedin_score == "Yes" else 0

    addition = (keyword_score + category_keyword_score + general_keyword_score +
                email_score + phone_score + linkedin_score + job_title_score + readability_score)
    total = addition / 800
    total_score = total * 100
    ats_keyword_score = total_score - (keyword_stuffing_score + category_keyword_stuffing_score)
    return ats_keyword_score


def calculate_keyword_stuffing_score(text, keywords, category_keywords):
    total_words = textstat.lexicon_count(text=text)
    word_counts = Counter(text.split())
    keyword_frequency = {keyword: word_counts[keyword] / total_words for keyword in keywords}
    category_keyword_frequency = {category_keyword: word_counts[category_keyword] / total_words for category_keyword in
                                  category_keywords}
    stuffing_threshold = 0.05

    keyword_frequency_scores = {keyword: min(frequency / stuffing_threshold, 1.0) for keyword, frequency in
                                keyword_frequency.items()}
    category_keyword_frequency_scores = {category: min(frequency / stuffing_threshold, 1.0) for category, frequency in
                                         category_keyword_frequency.items()}

    keyword_values, category_keyword_values = keyword_frequency_scores.values(), category_keyword_frequency_scores.values()

    keyword_stuffing_score = [value for value in keyword_values if value >= stuffing_threshold]
    category_keyword_stuffing_score = [value for value in category_keyword_values if value >= stuffing_threshold]
    return sum(keyword_stuffing_score), sum(category_keyword_stuffing_score)


def get_readability_score(text):
    readability_score = textstat.flesch_reading_ease(text=text)
    processed_readability_score = 50 if readability_score > 50 else readability_score
    return processed_readability_score


def get_readability_level(readability_score):
    if 100 > readability_score >= 50:
        return "Easy to read"
    elif 50 > readability_score >= 30:
        return "College"
    elif 30 > readability_score >= 10:
        return "College Graduate"
    elif 10 > readability_score >= 0:
        return "Professional"


def get_contact_score(email_score, phone_score, linkedin_score):
    email_point = 33 if email_score == "Yes" else 0
    phone_point = 33 if phone_score == "Yes" else 0
    linkedin_point = 34 if linkedin_score == "Yes" else 0
    return email_point + phone_point + linkedin_point
