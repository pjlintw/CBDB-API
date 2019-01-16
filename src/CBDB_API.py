import requests
import argparse
import json
import time
import pandas as pd
from pprint import pprint
import openpyxl
import os
from pathlib import Path

class CBDBAPI(object):


	CBDB_URL = 'http://cbdb.fas.harvard.edu/cbdbapi/person.php?name={}&o=json'


	'''docstring for CBDBAPI'''
	def __init__(self):
		parser = argparse.ArgumentParser(
			description='''
			An China Biographical Database Project (CBDB) API, which allows user access CBDB data easily\n
			Input: person name, Id or file\n
			Output: .xlsx
			'''
		)
		parser.add_argument('-n', nargs='*',help='Person Name in zh or en')
		parser.add_argument('-i', nargs='*', help='Person id')
		parser.add_argument('-w', help='write file')
		parser.add_argument('-rf', help='import file')
		args = parser.parse_args()

		# 測試區
		#'趙弘殷','張令鐸','趙元佐'
		args.n = ['趙美光','趙弘殷','張令鐸','趙元佐','趙匡胤']  # 趙瑗

		if args.rf:
			query_lst = self.file2lst(args.rf)
		elif args.i:
			query_lst = args.i
		elif args.n:
			query_lst = args.n
		else:
			query_lst = None


		if not query_lst:
			parser.print_help()
		else:
			self.parser_data(query_lst)



	def parser_data(self, query_lst, timeout=3):

		url = self.CBDB_URL

		# writer
		path = 'C:/Users/Linus/PycharmProjects/CBDB_API/w_in_one_1.xlsx'
		file_index = 1
		while Path(path).exists():
			path = path.split('.')[0] + '_' + str(file_index) + '.xlsx'
			file_index += 1


		writer = pd.ExcelWriter(path, engine='openpyxl')

		df = pd.DataFrame()
		df_set = {'BasicInfo': df,
				  'PersonSources': df,
				  'PersonAliases': df,
				  'PersonAddresses': df,
				  'PersonEntryInfo': df,
				  'PersonPostings': df,
				  'PersonSocialStatus': df,
				  'PersonKinshipInfo': df,
				  'PersonSocialAssociation': df,
				  'PersonTexts': df
				  }


		for i in query_lst:
			print('Processing Name:', i)

			res = requests.get(url.format(i), timeout=timeout)

			if res.status_code != 200 or res.text == '':
				print('invalid url: {}\n'.format(res.url))
				continue


			data = res.json()
			pprint(data)
			try:
				person_infos = data['Package']['PersonAuthority']['PersonInfo']['Person']
				# if data['Package']['PersonAuthority']['DataSource'] == 'BDB':
				# 	continue
			except:
				continue
			time.sleep(0.1)

			# detect list or dictionary
			if isinstance(person_infos, list):
				k = person_infos[0]
			elif isinstance(person_infos, dict):
				k = person_infos
			else:
				print('unknown instance')

			for key_name in k:

				if type(k[key_name]) == str:
					print('no data inside', k[key_name])
				elif key_name == 'BasicInfo':
					# dict
					basic_info_dict = k['BasicInfo']
					new_df = pd.Series(basic_info_dict).to_frame().T
					df_set['BasicInfo'] = pd.concat([df_set['BasicInfo'], new_df], axis=0, ignore_index=True)
					person_id = basic_info_dict['PersonId']
				else:
					for second_key_name in k[key_name]:

						type_of_dict_or_list = type(k[key_name][second_key_name])
						data_dict_or_list = k[key_name][second_key_name]
						if type_of_dict_or_list == list:
							is_list = data_dict_or_list
							new_df = pd.DataFrame(is_list)
							# add person_id to first position
							first_position_col = [person_id for i in range(len(new_df.index))]
							new_df.insert(loc=0, column='add_person_id', value=first_position_col)

							df_set[key_name] = pd.concat([df_set[key_name], new_df], axis=0, ignore_index=True)

						elif type_of_dict_or_list == dict:
							is_dict = data_dict_or_list
							new_df = pd.Series(is_dict).to_frame().T

							# add person_id to first position
							first_position_col = [person_id for i in range(len(new_df.index))]
							new_df.insert(loc=0, column='add_person_id', value=first_position_col)

							df_set[key_name] = pd.concat([df_set[key_name], new_df], axis=0, ignore_index=True)

						else:
							print('!!! type:', type_of_dict_or_list)




		# store
		self.store_pd_excel_writer(df_set, writer)

		return query_lst

	@staticmethod
	def file2lst(file_name):
		file_path = os.getcwd() + '/' + file_name
		f = open(file_path, 'r',encoding='utf-8').read()
		return [ i for i in f.split('\n') if i != '']

	@staticmethod
	def store_pd_excel_writer(df_set, excel_writer):
		for k in df_set:
			df_set[k].to_excel(excel_writer, sheet_name=k, header=True, index=False)
			excel_writer.save()


if __name__ == '__main__':
	c = CBDBAPI()




