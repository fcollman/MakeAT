import argparse
from serialize_interface import *
import csv
from jarray import zeros


def main(linearAlignmentDir,ImageDir,outputDir,verbose=False):
  """Run the main Fiji-based functionality.
  """
  from jython_imports import FileSaver,IJ,ArrayList,InverseTransformMapping,AffineModel2D,ImageProcessor,CoordinateTransformMesh,TiffDecoder
  
  #get a list of all pairwise files (has _to_ in midddle)

  transform_files = [f for f in os.listdir(linearAlignmentDir) if 'txt' in os.path.splitext(f)[1]]
  transform_files.sort()
  if not os.path.isdir(outputDir):
      os.makedirs(outputDir)
    
  minx=0
  miny=0
  maxx=0
  maxy=0

  #loop over these files
  for file in transform_files:
    (base,ext)=os.path.splitext(file)
    print file
    #read the transform for this file
    transform=readObjectFromFile(os.path.join(linearAlignmentDir,file))
    model=AffineModel2D()
    model.set(transform)
    
    #print "|"+image_file+"|"
    decoder=TiffDecoder(ImageDir,base+'.tif')
    file_info=decoder.getTiffInfo()[0]
    
    width=file_info.width
    height=file_info.height
    
    #mapping =InverseTransformMapping(model)
    coor_model=CoordinateTransformMesh(model, 128, width,height )
    meshMin= zeros(2, 'f')
    meshMax= zeros(2,'f')
    coor_model.bounds(meshMin, meshMax)
    
    if meshMin[0]<minx:
      minx=meshMin[0]
    if meshMin[1]<miny:
      miny=meshMin[1]
    if meshMax[0]>maxx:
      maxx=meshMax[0]
    if meshMax[1]>maxy:
      maxy=meshMax[1]

  maxWidth=int(maxx-minx)
  maxHeight=int(maxy-miny)
  
  for file in transform_files:
    print file
    (base,ext)=os.path.splitext(file)
    image_file=os.path.join(ImageDir,base+'.tif')
    
    #read the transform for this file
    transform=readObjectFromFile(os.path.join(linearAlignmentDir,file))
    transform.translate(-minx,-miny)
    model=AffineModel2D()
    model.set(transform)
    mapping =InverseTransformMapping(model)
    
    #read in this file
    imp=IJ.openImage(image_file)
      
    in_ip = imp.getProcessor()  
    in_ip.setInterpolationMethod(ImageProcessor.BILINEAR)
    out_ip=in_ip.createProcessor(maxWidth,maxHeight)
    out_ip.setMinAndMax(in_ip.getMin(),in_ip.getMax())
    mapping.mapInterpolated(in_ip,out_ip)

    imp.setProcessor(out_ip)
    fs =  FileSaver( imp )
    fs.saveAsTiff(os.path.join(outputDir,base+'.tif'))
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find Final Alignment Transformations Given Pairwise Point Matches")
    parser.add_argument('--linearAlignmentDir',
                        help='The directory with the alignment transforms.')
    parser.add_argument('--imagesDir',
                        help='The directory with the unaligned images.')
    parser.add_argument('--linearAlignedImages',
                        help='The directory in which to store all the aligned images.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print out runtime information.')

    args = parser.parse_args()
    main(args.linearAlignmentDir,args.imagesDir,args.linearAlignedImages,verbose=args.verbose)
    