# -*- coding: UTF-8 -*-

import os, glob

class LogFileReader(object):
	def __init__(self, base_dir, filename_patterns, dir_depths=-1):
		"""日志文件读取器
		在base_dir内，遍历符合filename_pattern模式的日志文件
		如果base_dir有嵌套文件夹，遍历嵌套文件夹内的日志文件。目前仅支持嵌套遍历一层。

		Args:
			base_dir (str): 日志文件所在基础路径
			filename_patterns (str or list[str]): 日志文件名匹配的模式. 默认是glob模式. 例如 "*.log". 可以是模式的列表.
			dir_depths (int): 遍历日志文件的目录层数，-1表示无限层
		"""

		self.dir_depths = dir_depths
		self.base_dir = base_dir # 日志文件基础目录
		if isinstance(filename_patterns, str):
			filename_patterns = [filename_patterns]
		self.filename_patterns = filename_patterns # glob 格式的文件筛选
		self.resetContext()

	def resetContext(self):
		# 遍历过程中的上下文缓存
		self.filedir = None
		self.filepath = None
		self.filename = None

		self.enter_filedir_callback = None # 进入目录的执行函数
		self.exit_filedir_callback = None # 离开目录的执行函数

	# region -------------- 进入目录，离开目录的自定义逻辑 --------------

	def register_enter_filedir_callback(self, callback):
		self.enter_filedir_callback = callback

	def register_exit_filedir_callback(self, callback):
		self.exit_filedir_callback = callback

	# endregion -------------- 进入目录，离开目录的自定义逻辑 --------------

	def iter_file_by_pattern(self, base_path, filename_pattern, dir_left_depth):
		# def iter_file_by_pattern
		#	遍历base目录下，满足格式的所有文件
		#
		# Args:
		#	base_path(str): 基础目录
		#	filename_pattern(str): 文件的glob格式 eg: *.txt
		#	dir_left_depth(int): 还要遍历杜少层目录

		if dir_left_depth != 0:
			for filepath in os.listdir(base_path):
				tmp_base_path = os.path.join(base_path, filepath)
				if os.path.isdir(tmp_base_path):
					self.enter_filedir_callback and self.enter_filedir_callback(tmp_base_path) # 执行进入某个目录的逻辑
					yield from self.iter_file_by_pattern(tmp_base_path, filename_pattern, dir_left_depth-1)
					self.exit_filedir_callback and self.exit_filedir_callback(tmp_base_path)

		filepath_pattern = os.path.join(base_path, filename_pattern)
		for filepath in glob.glob(filepath_pattern):
			if os.path.isdir(filepath):
				self.filedir = os.path.basename(filepath)
				self.enter_filedir_callback and self.enter_filedir_callback(self.filedir) # 执行进入某个目录的逻辑
				nest_all_files = glob.glob(os.path.join(filepath, self.filename_pattern))

				for nest_filepath in nest_all_files:
					if not os.path.isfile(nest_filepath):
						# 不再进一步嵌套遍历，直接跳过
						continue
					self.filepath = nest_filepath
					self.filename = os.path.basename(nest_filepath)
					yield nest_filepath
				self.exit_filedir_callback and self.exit_filedir_callback(self.filedir)
			else:
				self.filedir = None
				self.filepath = filepath
				self.filename = os.path.basename(filepath)
				yield filepath

	def __iter__(self):
		for filename_pattern in self.filename_patterns:
			yield from self.iter_file_by_pattern(self.base_dir, filename_pattern, self.dir_depths)
		self.resetContext()


# region ---------------------- 作者自己测试使用 ----------------------
def testLogFileReader():
	file_reader = LogFileReader("D:\python\LogProcessor", "*.py", 2)
	file_reader.register_enter_filedir_callback(lambda filepath: print("[enter]", filepath))
	file_reader.register_exit_filedir_callback(lambda filepath: print("[exit]", filepath))
	for filepath in file_reader:
		print('[match_file] ', filepath)

if __name__ == '__main__':
	testLogFileReader()
# endregion ---------------------- 作者自己测试使用 ----------------------
