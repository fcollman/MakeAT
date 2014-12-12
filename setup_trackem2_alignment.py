import argparse
from serialize_interface import *
import csv
from jarray import zeros


def main(linearAlignmentDir,ImageDir,trackEMfile,verbose=False):
  """Run the main Fiji-based functionality.
  """
  from jython_imports import AffineModel2D,InverseTransformMapping
  from ini.trakem2.display import Display, Patch
  from ini.trakem2 import Project
  
  #get a list of all pairwise files (has _to_ in midddle)

  transform_files = [f for f in os.listdir(linearAlignmentDir) if 'txt' in os.path.splitext(f)[1]]
  transform_files.sort()
  
  dirname=os.path.split(os.path.split(ImageDir)[0])[1]
  
  target = Project.newFSProject(dirname, None, ImageDir,True)
  #layerset = target.getRootLayerSet()
  
  #for i,file in enumerate(transform_files):
  #  print file
  #  (base,ext)=os.path.splitext(file)
  #  image_file=os.path.join(ImageDir,base+'.tif')
    
  #  #read the transform for this file
  #  transform=readObjectFromFile(os.path.join(linearAlignmentDir,file))
  #  model=AffineModel2D()
  #  model.set(transform)
  #  mapping =InverseTransformMapping(model)
  #  layer = layerset.getLayer(float(i), 1, True)
  #  patch = Patch.createPatch(project, image_file)
  #  patch.setCoordinateTransform(model) 
  #  layer.add(patch)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find Final Alignment Transformations Given Pairwise Point Matches")
    parser.add_argument('--linearAlignmentDir',
                        help='The directory with the alignment transforms.')
    parser.add_argument('--imagesDir',
                        help='The directory with the unaligned images.')
    parser.add_argument('--trackEMfile',
                        help='The file to store the results.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print out runtime information.')

    args = parser.parse_args()
    main(args.linearAlignmentDir,args.imagesDir,args.trackEMfile,verbose=args.verbose)
    