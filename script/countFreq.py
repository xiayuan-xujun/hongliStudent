#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023/10/18 22:21
# @Author: Xujun
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import string
import os
from collections import Counter
import docx

__all__ = ['WordFinder', 'Book']

# 读取已有的英文词频，以及各种变形情况。
lemmas = {}
with open('./datasets/lemmas.txt') as fin:
    for line in fin:
        line = line.strip()
        headword = line.split('\t')[0]
        try:
            related = line.split('\t')[1]
        except IndexError:
            related = None
        lemmas[headword] = related


valid_words = set()
for headword, related in lemmas.items():
    valid_words.add(headword)
    if related:
        valid_words.update(set(related.split()))


class WordFinder(object):
    '''A compound structure of dictionary and set to store word mapping'''
    def __init__(self):
        """Initialize lame containers for 'quick' search

        Structure of main_table
        {
            'a':{
                     # All related words and the headword start with same letter
                     'abandon': {'abandons', 'abandoned', 'abandoning'},

                     'apply': {'applies', 'applied', 'applying'},

                     # headword with no related word
                     'abeam': None,
                     ...
                },
            'b': {...},
            'c': {...},
            ...
        }

        Structure of special_table
        {

            # 1+ related words does not share the same starting letter
            # with heasdword
            'although': {'altho', 'tho', 'though'},
            'bad': {'badder', 'baddest', 'badly', 'badness', 'worse', 'worst'},
            ...
        }

        """
        self.main_table = {}
        for char in string.ascii_lowercase:
            self.main_table[char] = {}
        self.special_table = {}

        for headword, related in lemmas.items():
            # Only 3 occurrences of uppercase in lemmas.txt, which include 'I'
            # Trading precision for simplicity
            headword = headword.lower()
            try:
                related = related.lower()
            except AttributeError:
                related = None
            if related:
                for word in related.split():
                    if word[0] != headword[0]:
                        self.special_table[headword] = set(related.split())
                        break
                else:
                    self.main_table[headword[0]][headword] = set(related.split())
            else:
                self.main_table[headword[0]][headword] = None

    def find_headword(self, word):
        """Search the 'table' and return the original form of a word"""
        word = word.lower()
        alpha_table = self.main_table[word[0]]
        if word in alpha_table:
            return word

        for headword, related in alpha_table.items():
            if related and (word in related):
                return headword

        for headword, related in self.special_table.items():
            if word == headword:
                return word
            if word in related:
                return headword
        # This should never happen after the removal of words not in valid_words
        # in Book.__init__()
        return None

    # TODO
    def find_related(self, headword):
        pass


def is_dirt(word):
    return word not in valid_words


def list_dedup(list_object):
    """Return the deduplicated copy of given list"""
    temp_list = []
    for item in list_object:
        if item not in temp_list:
            temp_list.append(item)
    return temp_list


class Book(object):
    def __init__(self, filepath):
        # 打开文件。
        file_extension = filepath.split('.')[-1]
        if file_extension == 'doc' or file_extension == 'docx':
            bookfile = docx.Document(filepath)
            fullText = []
            # paragraphs 也是按照行来进行读取。
            for i in bookfile.paragraphs:  # 迭代docx文档里面的每一个段落
                word_txt = i.text.lower()
                low_word = re.split(r'\b([a-zA-Z-]+)\b', word_txt)  # 拆分
                for one_word in low_word:
                    fullText.append(one_word)  # 保存每一个段落的文本
            print("ok")
        else:
            # txt中不能出现中文。
            bookfile = open(filepath, encoding='UTF-8')
            # 统一转换成string格式。
            content = bookfile.read().lower()  # 将单词统一批量转换成小写的形式。
            fullText = re.split(r'\b([a-zA-Z-]+)\b', content)  # 正则匹配单词

        self.temp_list = [item for item in fullText if not is_dirt(item)]
        finder = WordFinder()  # 实例化一个类
        self.temp_list = [finder.find_headword(item) for item in self.temp_list]

    def freq(self):
        """Count word frequencies and return a collections.Counter object"""
        cnt = Counter()
        # 词频统计
        for word in self.temp_list:
            cnt[word] += 1
        return cnt

    # TODO
    def stat(self):
        pass


def statistical_word_frequency_func(input_file):
    LINE_SEP = os.linesep
    book = Book(input_file)
    result = book.freq()
    # Maximum width of the ocurrence column
    max_width = max(len(str(v)) for v in result.values())

    count_words = 0
    report = []
    for word in sorted(result, key=lambda x: result[x], reverse=True):
        report.append('{:>{}} {}'.format(result[word], max_width, word))
        count_words += result[word]

    return count_words, report
    # # print('len words', len(report))
    # # output_file = os.path.join(output_file, 'save.txt')
    # if output_file:
    #     with open(output_file, 'w') as output:
    #         output.write(LINE_SEP.join(report))
    #         output.write(LINE_SEP)
    #         return count_words, report
    # else:
    #     return "error"
        # print(LINE_SEP.join(report))
    # print('\n生成了结果：', output_file)
    # print('\n单词总数：', count_words)


# if __name__ == '__main__':
#     input_file = r'E:\mediaPipe\WordFrequencyCount\test.docx'
#     output_file = r'E:\mediaPipe\WordFrequencyCount\save.txt'
#     test(input_file, output_file)

