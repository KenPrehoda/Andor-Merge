#!/usr/bin/env python3
import sys
import numpy as np
from glob import glob

try:
    import tifffile
except:
    print("The tifffile python module must be installed (try pip install tifffile)")
    sys.exit(1)
    
def process_files(file_list,target_file,crop=None,split=False):
    if crop:
        rows = np.arange(crop[1],crop[3])
        columns = np.arange(crop[0],crop[2])
    if split:
        with tifffile.TiffWriter(f'{target_file}_ch1.tif', bigtiff=True) as tif1, tifffile.TiffWriter(f'{target_file}_ch2.tif', bigtiff=True) as tif2:
            for filename in file_list:
                frames = tifffile.imread(filename)
                print(f'Processing {filename}')
                for frame in frames:
                    if crop:    
                        tif1.save(frame[:, :1024][rows][:,columns],software=None)    
                        tif2.save(frame[:, 1024:][rows][:,columns],software=None)
                    else:
                        tif1.save(frame[:, :1024],software=None)    
                        tif2.save(frame[:, 1024:],software=None)
    else:
        with tifffile.TiffWriter(target_file, bigtiff=True) as tif:
            for filename in file_list:
                frames = tifffile.imread(filename)
                print(f'Processing {filename}')
                for frame in frames:
                    if crop:    
                        tif.save(frame[:, :1024][rows][:,columns],software=None)    
                        tif.save(frame[:, 1024:][rows][:,columns],software=None)
                    else:
                        tif.save(frame[:, :1024],software=None)    
                        tif.save(frame[:, 1024:],software=None)
                        
if __name__ == "__main__":
    import argparse
    import re
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='Merge Andor tif channels and files into a single tif or multiple tif files by channel.',epilog='''Examples:
    andor_merge.py -t merged.tif *.tif
    andor_merge.py -s -t merged_and_sorted.tif *.tif
    andor_merge.py -s -c 12x34x65x120 -t merged_and_sorted_and_cropped.tif *.tif
    andor_merge.py -s -c 12x34x65x120 -p -t merged_and_sorted_and_cropped_and_split *.tif
    ''')
    parser.add_argument('files', nargs='+')    
    parser.add_argument('-s','--sort', help='sort filenames by the number before the suffix',action="store_true")
    parser.add_argument('-p','--split', help='split channels into separate files- ch1, ch2 suffix will be added to file name',action="store_true")
    parser.add_argument('-c','--crop', help='crop source 1x2x3x4 upper then lower corner of rect, origin is at upper left')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-t', '--target', help='Merged TIFF file to be created', required=True)
    args = parser.parse_args()
    if args.sort:
        files = sorted(glob(args.files[0]),key=lambda f: int(re.findall(r'\d+',f)[-1]))
    else:
        files = glob(args.files[0])
    crop = None
    if args.crop:
        inp = args.crop.split('x')
        if len(inp) < 4:
            print('Crop argument must have two points representing upper left and lower right in format 1x2x3x4')
            sys.exit(1)
        crop = [int(i) for i in inp]
        if crop[2] <= crop[0] or crop[3] <= crop[1]:
            print('Incorrect crop argument')
            sys.exit(1)
        print(f'Cropping to {crop[0]},{crop[1]} X {crop[2]},{crop[3]}')
    process_files(files,args.target,crop,args.split)
    