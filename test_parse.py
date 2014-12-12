import os, re
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
                                     "Parrot back your arguments.")
    parser.add_argument('--outputLayout', help="Path to the output file.")
    parser.add_argument('--outputImage',help="Path to where stiched output should go")
    
    args = parser.parse_args()
    
    outputLayout=args.outputLayout
    outputImage=args.outputImage
    
    print outputLayout
    print outputImage


