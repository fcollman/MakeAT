import os, re
import argparse

import mpicbg.stitching.StitchingParameters
import mpicbg.stitching.ImageCollectionElement
import mpicbg.stitching.CollectionStitchingImgLib
import mpicbg.stitching.ImageInformation
import java.io.File
import mpicbg.models.TranslationModel2D
import java.util.ArrayList
import net.imglib2.type.numeric.real.FloatType
import mpicbg.imglib.type.numeric.integer.UnsignedShortType,UnsignedByteType
import ij.ImagePlus
import ij.io.FileSaver
import mpicbg.stitching.fusion.Fusion


package hellocl;

public class HelloCL { 
 public static void main(String[] args) {
  // TODO code application logic here
 }
}

 
def define_stitch_parameters():
  params=StitchingParameters()
  params.dimensionality = 2
  params.channel1 = 0
  params.channel2 = 0
  params.timeSelect = 0
  params.checkPeaks = 5
  params.regThreshold = .7
  params.computeOverlap = True
  params.subpixelAccuracy = True
  params.fusionMethod = 0
  
  
  return params
 
def fuse_images(image_list,params,outputImage):
  #first prepare the models and get the targettype
  models = ArrayList()
  images = ArrayList()
  is32bit = False;
  is16bit = False;
  is8bit = False;
  for  imt in  image_list:
    imp = imt.getImagePlus()
    if ( imp.getType() == ImagePlus.GRAY32 ):
      is32bit = True
    elif ( imp.getType() == ImagePlus.GRAY16 ):
      is16bit = True
    elif ( imp.getType() == ImagePlus.GRAY8 ):
      is8bit = True
    images.add( imp )
    models.add(imt.getModel())
			
			
  if ( is32bit ):
    imp = Fusion.fuse( FloatType, images, models, params.dimensionality, params.subpixelAccuracy, params.fusionMethod, None, False, False, False )
  elif ( is16bit ):
    imp = Fusion.fuse(  UnsignedShortType(), images, models, params.dimensionality, False, params.fusionMethod, None, False, False, False)
  elif ( is8bit ):
    imp = Fusion.fuse(  UnsignedByteType, images, models, params.dimensionality, params.subpixelAccuracy, params.fusionMethod, None, False, False, False )
  else:
    IJ.log( "Unknown image type for fusion." );
		
  fs =  FileSaver( imp )
  if not os.path.isdir(os.path.split(outputImage)[0]):
    os.makedirs(os.path.split(outputImage)[0])
  fs.saveAsTiff(  outputImage  )
				
			
	
def write_layout_file(outputLayout,optimized):
  f=open(outputLayout,'w')
  for i,element in enumerate(optimized):
    model=element.getModel()
    (x,y)=(0.0,0.0)
    out=model.apply([x,y])
    f.write("%d 1 0 %f 0 1 %f\n"%(i,out[0],out[1]))
  f.close()
  
def calc_stitch(files,xoff,yoff,outputLayout,outputImage):
 
  #norm_coords = get_norm_coords(files)
  elements=ArrayList()
  for i,file in enumerate(files):
    element=ImageCollectionElement(File(file),i)
    element.setDimensionality( 2 )
    element.setOffset([xoff[i],yoff[i]])
    element.setModel(  TranslationModel2D() );
    elements.add(element)
  
  params = define_stitch_parameters()
  
  optimized = CollectionStitchingImgLib.stitchCollection( elements, params )
  
  if not os.path.isdir(os.path.split(outputLayout)[0]):
    os.makedirs(os.path.split(outputLayout)[0])
    
  write_layout_file(outputLayout,optimized)
  
  fuse_images(optimized,params,outputImage)
  
  
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
                                     "Parrot back your arguments.")
    parser.add_argument('--outputLayout',  help="Path to the output file.")
    parser.add_argument('--outputImage', help="Path to where stiched output should go")
    parser.add_argument('File_X_Y', nargs="*", help="file xoff yoff (files with their initial offsets)")
    args = parser.parse_args()
    
    outputLayout=args.outputLayout
    outputImage=args.outputImage
    
    Nargs=len(args.File_X_Y)
    
    print args.File_X_Y
    files=[]
    xoff=[]
    yoff=[]
    assert(Nargs%3==0)
    
    for i in range(0,Nargs,3):
      filename=args.File_X_Y[i]
      files.append(filename)
      xoff.append(float(args.File_X_Y[i+1]))
      yoff.append(float(args.File_X_Y[i+2]))
      
      
        
        
if len(files)==1:
  print "nothing to do"

else:
  calc_stitch(files,xoff,yoff,outputLayout,outputImage)
  

