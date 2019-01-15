import sys
from CBDB_API import *

def main(args=None):
	''' the main routine '''
	if args == None:
		args = sys.argv[1:]

	CBDBAPI(args)

if __name__ == '__main__':
	main()
