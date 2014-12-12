import argparse
from serialize_interface import *
    
def main(targetImageFile,sourceImageFile,blockMatchFile,verbose=False):
    """Run the main Fiji-based functionality.
    """
    from jython_imports import IJ,ArrayList,RigidModel2D,AffineModel2D,SimilarityModel2D,Float,Vector,FloatArray2DSIFT
    from mpicbg.trakem2.align.Util import imageToFloatAndMask
    from mpicbg.models import ErrorStatistic
    from mpicbg.trakem2.util import Triple
    from ij.process import FloatProcessor
    from mpicbg.models import SpringMesh
    from mpicbg.ij.blockmatching import BlockMatching
    #from mpicbg.trakem2.align.concurrent import BlockMatchPairCallable
    #read in the features

    pm12 = ArrayList()
    pm21 = ArrayList()
    
    #open the images
    img1 = IJ.openImage(targetImageFile).getImage()
    img2 = IJ.openImage(sourceImageFile).getImage()
    
    #get the image height and width
    width = img1.getWidth()
    height = img1.getHeight()

    #get the second image height and width
    width2= img2.getWidth()
    height2 = img2.getHeight()
    
    #the image sizes should match
    assert (width==width2),"image widths do not match"
    assert (height==height2),"image heights do not match"

    ip1 = FloatProcessor( width, height )
    ip2 = FloatProcessor( width, height )
    ip1Mask = FloatProcessor( width, height )
    ip2Mask = FloatProcessor( width, height )

    #elastic alignment parameters
    blockRadius = 150 #half-width of block to cut out (pixels)
    searchRadius = 50 #size of search neighborhood (pixels)
    minR = .4 #minimum correlation coefficent to find match
    rodR = .9 #maximal_second_best_r/best_r 
    maxCurvatureR = 10.0 #maximal_curvature_ratio 
    scalefactor=0.5
    
    imageToFloatAndMask( img1, ip1, ip1Mask )
    imageToFloatAndMask( img2, ip2, ip2Mask )
    
    #variables to save the error statistics
    error1=ErrorStatistic(1)
    error2=ErrorStatistic(1)
    
    #i don't think these are relevant because this is just setting up the vertices
    #not actually setting up the springs
    spring_stiff=0.1
    max_stretch=2000.0
    spring_damp=0.9
    
    interVertexDistance=blockRadius*2.2
    numX=int(width/interVertexDistance)
    numY=int(height/interVertexDistance)
    
    m1=SpringMesh(numX,numY,width,height,spring_stiff,max_stretch,spring_damp)
    m2=SpringMesh(numX,numY,width,height,spring_stiff,max_stretch,spring_damp)
    
    #the only reason to setup the springmesh is to get these vertices
    v1 = m1.getVertices()
    v2 = m2.getVertices()
    print "matching 1"
    print numX,numY
    print width,height
    print v1.size()
    
    BlockMatching.matchByMaximalPMCC(
                    ip1,
                    ip2,
                    ip1Mask,
                    ip2Mask,
                    scalefactor,
                    RigidModel2D().createInverse(),
                    blockRadius,
                    blockRadius,
                    searchRadius,
                    searchRadius,
                    minR,
                    rodR,
                    maxCurvatureR,
                    v1,
                    pm12,
                    error1)
    print pm12.size()                
    #for each block it cuts out, it find the best fit, this defines a vector field between the two images
    #it then excludes outliers by systematically going through each element in the vector field,
    #for each element it takes creates a local average 
    #use a rigid model to calculate local weighted average
    localSmoothnessFilterModel = RigidModel2D()
    localRegionSigma = 1.75 * blockRadius #local smoothness neighborhood
    maxLocalEpsilon = 10 #local smoothness error (pixels)
    maxLocalTrust = 3.0 #factor by which average error of localized fit must be less 
    
    print "smoothing 1"
    #filter out the results that don't match localSmoothness filter
    localSmoothnessFilterModel.localSmoothnessFilter( pm12, pm12, localRegionSigma, maxLocalEpsilon,maxLocalTrust )
    print pm12.size()
    
    print "matching 2"
    BlockMatching.matchByMaximalPMCC(
                    ip2,
                    ip1,
                    ip2Mask,
                    ip1Mask,
                    scalefactor,
                    RigidModel2D(),
                    blockRadius,
                    blockRadius,
                    searchRadius,
                    searchRadius,
                    minR,
                    rodR,
                    maxCurvatureR,
                    v2,
                    pm21,
                    error2)

    print "smoothing 2"
    localSmoothnessFilterModel.localSmoothnessFilter( pm21, pm21, localRegionSigma, maxLocalEpsilon, maxLocalTrust )
    
 
 
    #i'm packaging up the results here into a more compact format.. original results package resulted in a 50MB file per comparison where this is 1.6 MB. could be further reduce.
    pm12comp=[]
    for i in range(pm12.size()):
      p1=(pm12.get(i).getP1().getL(),pm12.get(i).getP1().getW())
      p2=(pm12.get(i).getP2().getL(),pm12.get(i).getP2().getW())
      pm12comp.append((p1,p2))
  
    pm21comp=[]
    for i in range(pm21.size()):
      p1=(pm21.get(i).getP1().getL(),pm21.get(i).getP1().getW())
      p2=(pm21.get(i).getP2().getL(),pm21.get(i).getP2().getW())
      pm21comp.append((p1,p2))
      
      
    results=(pm12comp, pm21comp)
    
    #save the results
    writeObjectToFile(results,blockMatchFile)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Do block matching between these two images")
    parser.add_argument('--targetImage',
                        help='The file with the features of the image to be registered to.')
    parser.add_argument('--sourceImage',
                        help='The file with the features of the image to transform/register.')
    parser.add_argument('--blockMatchFile',
                        help='the file to save the block matching results')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print out runtime information.')

    args = parser.parse_args()
    main(args.targetImage,
         args.sourceImage,
         args.blockMatchFile,
         verbose=args.verbose)
        