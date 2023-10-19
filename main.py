#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023/10/18 14:11
# @Author: Xujun
import sys
import os
import shutil
import random
import time

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QStackedLayout, QWidget, QMainWindow, QFileDialog
from PyQt5.QtCore import QTimer, Qt

from data.select_words_ui import select_words_ui
from data.main_ui import Ui_MainWindow
from data.select_student_name_ui import select_student_name_ui
from data.statistical_word_frequency_ui import statistical_word_frequency_ui

from script.countFreq import statistical_word_frequency_func


class FrameSelectWords(QWidget, select_words_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class FrameSelectStudentName(QWidget, select_student_name_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class FrameStatisticalWordFrequency(QWidget, statistical_word_frequency_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    主窗口
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # 设置初始化变量数据
        self.select_folder_path = None
        self.select_files_path = None
        self.select_words_path = None  # 随机单词地址
        self.select_student_name_path = None  # 随机点名地址
        self.statistical_word_frequency_path = None   # 统计词频地址

        self.words_list_path = "./datasets/Englisth_words"  # 存放当前数据库中的单词
        self.name_student_list_path = './datasets/student_class'  # 存放数据库中班级花名册

        self.count_words = None
        self.report = None

        # 设置堆叠布局
        self.qsl = QStackedLayout(self.right_frame)

        # 实例化堆叠界面
        self.select_words_frame = FrameSelectWords()
        self.select_student_name_frame = FrameSelectStudentName()
        self.statistical_word_frequency_frame = FrameStatisticalWordFrequency()

        # 实现相应的功能
        # 随机选择指定数量的单词
        self.select_words_frame.update_words_chapter.clicked.connect(lambda: self.update_ComboBox_words_chapter(self.words_list_path))  # 更新下拉列表
        # self.select_words_frame.select_chapter_words.activated.connect()
        self.select_words_frame.load_words.clicked.connect(self.load_word_datasets)  # 导入新的文件
        self.select_words_frame.greate_random_words.clicked.connect(self.select_random_words_function)  # 生成随机数

        # 随机点名，选择一个同学
        self.select_student_name_frame.update_select_student_class_button.clicked.connect(
            lambda: self.update_ComboBox_student_name(self.name_student_list_path))  # 更新下拉列表
        # self.select_student_name_frame.select_student_class.clicked.connect(lambda: self.select_files_student_name_path_func())  # 选择班级
        # 设置开始和结束
        self.select_student_name_frame.start_select_student.clicked.connect(lambda: self.start_name())
        self.select_student_name_frame.stop_select_student.clicked.connect(lambda: self.stop())
        # 设置图片显示

        # 词频统计
        self.statistical_word_frequency_frame.select_test_paper.clicked.connect(self.statistical_word_frequency_path_func)
        self.statistical_word_frequency_frame.statistical_word_frequency.clicked.connect(self.statistical_word_frequency_data_button)

        # 加入到布局之中
        self.qsl.addWidget(self.select_student_name_frame)
        self.qsl.addWidget(self.select_words_frame)
        self.qsl.addWidget(self.statistical_word_frequency_frame)

        # 控制函数
        self.controller()

    def controller(self):
        self.select_student_button.clicked.connect(self.switch)
        self.select_words_button.clicked.connect(self.switch)
        self.statistical_word_frequency_button.clicked.connect(self.switch)

    def switch(self):
        sender = self.sender().objectName()  # 获取当前按钮的名字。

        index = {
            "select_student_button": 0,
            "select_words_button": 1,
            "statistical_word_frequency_button": 2,
        }

        self.qsl.setCurrentIndex(index[sender])

    def select_files_student_name_path_func(self):
        self.select_student_name_path = self.select_files()

    def statistical_word_frequency_path_func(self):
        self.statistical_word_frequency_path = self.select_files()

    def select_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        select_files_path, _ = QFileDialog.getOpenFileNames(self, "select_test_paper", "",
                                                     "Text Files (*.txt);;Image Files (*.jpg);;All Files (*)",
                                                     options=options)
        # if select_files_path:
        #     # self.select_files_path = select_files_path
        #     # print(select_files_path)
        return select_files_path

    def select_folder(self):
        select_folder_path = QFileDialog.getExistingDirectory(self, "select_file_path")

        if select_folder_path:
            # self.select_folder_path = select_folder_path
            print(select_folder_path)
            return select_folder_path

    """
    ############################################ 随机生成单词 #######################################
    """

    def update_ComboBox_words_chapter(self, folder_path):
        # folder_path = "./datasets/Englisth_words"  # 请替换为实际文件夹路径
        # folder_path = self.select_folder_path
        print(self.select_student_name_path)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # 清空现有的下拉列表项 # 指定列表
            self.select_words_frame.select_chapter_words.clear()
            # 获取文件夹中的所有文件名
            file_names = os.listdir(folder_path)
            # print(file_names)
            # 将文件名添加到下拉列表中
            self.select_words_frame.select_chapter_words.addItems(file_names)
        else:
            self.select_words_frame.show_words.setText("当前工作目录下没有单词表，请导入对应的单词表")
            print("Updated ComboBox with folder files.")

    def update_ComboBox_student_name(self, folder_path):
        # folder_path = "./datasets/Englisth_words"  # 请替换为实际文件夹路径
        # folder_path = self.select_folder_path
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # 清空现有的下拉列表项 # 指定列表
            self.select_student_name_frame.select_student_class_combox.clear()
            # 获取文件夹中的所有文件名
            file_names = os.listdir(folder_path)
            # print(file_names)
            # 将文件名添加到下拉列表中
            self.select_student_name_frame.select_student_class_combox.addItems(file_names)
        else:
            self.select_words_frame.show_words.setText("当前工作目录下没有单词表，请导入对应的单词表")
            print("Updated ComboBox with folder files.")

    # select_words 相关函数
    # 下拉列表，识别指定文件夹下的所有文件，生成对应的选项， 多选项
    def select_random_words_function(self):
        english_nums = self.select_words_frame.English_words_num.text()
        chinese_nums = self.select_words_frame.chinese_words_num.text()

        print(english_nums)
        if not english_nums:
            english_nums = 10
        if not chinese_nums:
            chinese_nums = 0
        print(english_nums)
        output_random_words = ''
        chapter_index = self.select_words_frame.select_chapter_words.currentIndex()
        chapter_text = self.select_words_frame.select_chapter_words.itemText(chapter_index)
        self.select_words_path = [os.path.join('./datasets/Englisth_words', chapter_text)]
        if self.select_words_path:
            try:
                for once_file_path in self.select_words_path:
                    words_results = []
                    with open(once_file_path, "r", encoding="utf-8") as file:
                        words_lines = file.readlines()
                        words_results += words_lines
                    file.close()

                len_words_results = len(words_results)
                if len_words_results < int(english_nums) + int(chinese_nums):
                    # self.select_words_frame.show_words.setText("所选文件没有这么多单词。已输出所有单词如下：")
                    output_random_words += "所选文件没有这么多单词。已输出所有单词如下："
                    random_words = [x.strip() for x in words_results]
                    self.select_words_frame.show_words.setText(str(output_random_words) + '\n' + ','.join(random_words))
                else:
                    random_words = random.sample(words_lines, int(english_nums))
                    random_words = [x.strip() for x in random_words]
                    self.select_words_frame.show_words.setText(','.join(random_words))

            except FileNotFoundError:
                self.select_words_frame.show_words.setText("File not found")
        else:
            self.select_words_frame.show_words.setText("No file selected")

    # 导入新的文件，先暂时不实现这个功能吧。
    # 要不先做一个移动的功能。
    def load_word_datasets(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        select_files_path, _ = QFileDialog.getOpenFileNames(self, "select_test_paper", "",
                                                            "Text Files (*.txt)",
                                                            options=options)

        if select_files_path:
            # 先统一放置英文单词文件
            target = r'./datasets/Englisth_words'
            if not os.path.exists(target):
                os.makedirs(target)
            print(os.path.basename(select_files_path[0]))

            for once_file_path in select_files_path:
                target = os.path.join(target, os.path.basename(once_file_path))
                # 判断是否有同名文件
                if os.path.exists(target):
                    self.select_words_frame.show_words.append("当前文件已存在，已跳过" + '\n' + str(target))
                    continue
                else:
                    shutil.copy(once_file_path, target)
                    self.select_words_frame.show_words.append("已将文件移动到指定位置:" + '\n' + str(target))
        else:
            self.select_words_frame.show_words.setText("No file selected")

    # statistical_word_frequency 相关函数
    def recognition_image(self):
        pass

    """
        ############################################ 随机点名 ########################################
    """
    # 随机选择一个名字
    def setname_image(self):
        # print(self.select_student_name_path)
        student_name_index = self.select_student_name_frame.select_student_class_combox.currentIndex()
        student_name_text = self.select_student_name_frame.select_student_class_combox.itemText(student_name_index)
        self.select_student_name_path = [os.path.join('./datasets/student_class', student_name_text)]
        if self.select_student_name_path:
            try:
                for once_file_path in self.select_student_name_path:
                    name_lists = []
                    with open(once_file_path, "r", encoding="utf-8") as file:
                        words_lines = file.readlines()
                        name_lists += words_lines
                    file.close()
                # print(name_lists)
                # 设置字体大小
                self.font = QFont()
                self.font.setPointSize(150)
                # 点名系统
                name = random.choice(name_lists)
                self.select_student_name_frame.textBrowser.setText(name)
                self.select_student_name_frame.textBrowser.setAlignment(Qt.AlignCenter)  # 设置文本对齐方式 居中对齐
                self.select_student_name_frame.textBrowser.setFont(self.font)
                self.left_show_text_browser.setText("幸运儿：" + '\n' + '\n' + name)
            except FileNotFoundError:
                self.select_student_name_frame.textBrowser.setText("File not found")
        else:
            self.select_student_name_frame.textBrowser.setText("请先选择班级再进行点名！")

    # 开始程序
    def start_name(self):
        # self.select_student_name_frame.start_select_student.setEnabled(False)  # 将start按钮设置成禁止点击
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.setname_image)
        self.timer.start(50)  # 名字循环的时间

    # 程序结束
    def stop(self):
        self.timer.stop()

    # # 设置按钮解禁
    # def btnsetenabled(self, btn):
    #     print(btn.isEnabled())
    #     # 按下按钮后解除禁止可以继续点击
    #     btn.setEnabled(True)

    """
    ########################### 词频统计 ##############################
    """
    def statistical_word_frequency_data_button(self):
        self.count_words, self.report = self.statistical_word_frequency_data()
        self.statistical_word_frequency_frame.show_word_frequency.setText(str(self.report))
        # print(self.count_words)
        # print(self.report)

    def statistical_word_frequency_data(self):
        # 实现按钮点击事件的逻辑
        end_path = ['jpg', 'png', 'JPEG', 'bmp']
        LINE_SEP = os.linesep
        if self.statistical_word_frequency_path:
            for word_frequent_path in self.statistical_word_frequency_path:
                # 判断是图片还是txt文件或者doc文件
                if os.path.basename(word_frequent_path).split('.')[-1] in end_path:
                    # 进行对应的ocr识别, 识别过后，应该保存对应的统计结果
                    # 先暂时保存对应的识别结果在tmp.txt之中吧。
                    words_lists = self.recognition_image()
                    word_frequent_path = './tmp.txt'
                    with open(word_frequent_path, 'w') as output:
                        output.write(LINE_SEP.join(str(words_lists)))
                        output.write(LINE_SEP)

                count_words, report = statistical_word_frequency_func(word_frequent_path)
        else:
            self.statistical_word_frequency_frame.show_word_frequency.setText("请先选择统计的文件！")

        return count_words, report


if __name__ == "__main__":
    app = QApplication(sys.argv)
    showMain = MainWindow()
    app.setWindowIcon(QIcon('GUI/dog.ico'))
    showMain.show()
    sys.exit(app.exec_())

