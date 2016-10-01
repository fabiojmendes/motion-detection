import main
from argparse import ArgumentParser

def size_tuple(size_str):
	return tuple(size_str.split('x'))

if __name__ == '__main__':
	parser = ArgumentParser(description='Process some integers.')
	parser.add_argument('--fps', type=int, default=10)
	parser.add_argument('--size', type=size_tuple, default=(1280,720), help='The frame size in WxH')

	args = parser.parse_args()
	main.main(args)
