import argparse
from serialize_interface import *
import csv
from jarray import zeros
from net.imglib2.type.numeric.real import FloatType
from mpicbg.imglib.type.numeric.integer import UnsignedShortType,UnsignedByteType
from mpicbg.stitching.fusion import Fusion
from java.util import ArrayList

def read_layout_file(StitchLayoutDir,rib,sect,sess):

    from jython_import import AffineModel2D
    
    filename="rib%04dsess%04dsect%04d_stitch.txt"%(rib,sess,sect)
    filepath=os.path.join(StitchLayoutDir,filename)

    f=open(filepath,'r')
    reader = csv.reader(f, delimiter=' ', quotechar='|')
    
    frame_layout_dict={}
    for row in reader:
      (frame,a11,a12,a13,a21,a22,a23)=row
      model = AffineModel2D()
      model.set(float(a11),float(a12),float(a21),float(a22),float(a13),float(a23))
      frame_layout_dict{int(frame)}=model
    
    return frame_layout_dict

  
def fuse_images(files,frames,model_dict):
  #first prepare the models and get the targettype

  models = ArrayList()
  images = ArrayList()
  is32bit = False;
  is16bit = False;
  is8bit = False;
  for  file,frame in zip(files,frames):
    imp=IJ.openImage(file)
    if ( imp.getType() == ImagePlus.GRAY32 ):
      is32bit = True
    elif ( imp.getType() == ImagePlus.GRAY16 ):
      is16bit = True
    elif ( imp.getType() == ImagePlus.GRAY8 ):
      is8bit = True
    images.add( imp )
    models.add(model_dict{frame})
			
  if ( is32bit ):
    imp = Fusion.fuse( FloatType, images, models, 2, True, 0, None, False, False, False )
  elif ( is16bit ):
    imp = Fusion.fuse(  UnsignedShortType(), images, models, 2, True, 0, None, False, False, False)
  elif ( is8bit ):
    imp = Fusion.fuse(  UnsignedByteType, images, models, 2, True, 0, None, False, False, False )
  else:
    IJ.log( "Unknown image type for fusion." )
		
	return imp
  
def main(AlignmentDir,StitchLayoutDir,RegistrationDir,files,frames,rib,sect,sess,verbose=False,stitched_dir=)
  """Run the main Fiji-based functionality.
  """
  from jython_imports import FileSaver,IJ,ArrayList,InverseTransformMapping,AffineModel2D,ImageProcessor,CoordinateTransformMesh,TiffDecoder
  from mpicbg.stitching import StitchingParameters,ImageCollectionElement,CollectionStitchingImgLib
  #get a list of all pairwise files (has _to_ in midddle)
  
  frame_layout_dict=read_layout_file(StitchLayoutDir,rib,sect,sess)
  
  imp=fuse_images(files,frames,frame_layout_dict)
  
  if (sess>0):
    registration_file='rib%04dsess%04dsect%04d.txt'%(rib,sess,sect)
    reg_transorm = read_object_from_file_gson(os.path.join(RegistrationDir,registration_file))
    
	
  
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
    parser.add_argument('--AlignmentDir',
                        help='The directory with the alignment transforms.')
    parser.add_argument('--StitchLayoutDir',
                        help='The directory with the stitch layouts.')
    parser.add_argument('--RegistrationDir',
                        default=None,
                        help='The directory with the registration transforms.')
    parser.add_argument('--ribbon',
                        help='The ribbon number.')
    parser.add_argument('--section',
                        help='The section number.')
    parser.add_argument('--session',
                        help='The session number.')
    parser.add_argument('--Files_frames','*','list of files followed by their frame number')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print out runtime information.')

    args = parser.parse_args()
 
    Nargs=len(args.Files_frames)
    
    files=[]
    frames=[]
    
    assert(Nargs%2==0)
    
    for i in range(0,Nargs,2):
      filename=args.Files_frames[i]
      files.append(filename)
      frames.append(omt(args.Files_frames[i+1]))
 
    main(args.AlignmentDir,args.StitchLayoutDir,args.RegistrationDir,files,frames,args.ribbon, args.section,args.session,verbose=args.verbose)
    