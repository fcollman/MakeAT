import argparse
from serialize_interface import *
    
def main(targetFeatureFile,sourceFeatureFile,verbose=False,outputTransformFile=None,outputInliersFile=None,modeltype='rigid',minInliers=8,mindist=2.5,Niters=1000,min_inlier_ratio=0.0):
    """Run the main Fiji-based functionality.
    """
    from jython_imports import IJ,ArrayList,RigidModel2D,AffineModel2D,SimilarityModel2D,Float,Vector,FloatArray2DSIFT

    #read in the features
    targetFeatures=readObjectFromFile(targetFeatureFile)
    sourceFeatures=readObjectFromFile(sourceFeatureFile)
    
    #find the best candidates
    candidates = FloatArray2DSIFT.createMatches(sourceFeatures, targetFeatures, 1.5, None, Float.MAX_VALUE, 2.0);
    
    #use a rigid model for ransac
    if modeltype == 'rigid':
        model = RigidModel2D()
    elif modeltype == 'affine':
        model = AffineModel2D()
    elif modeltype == 'similarity':
        model = SimilarityModel2D()
        
    #filter with Ransac, also sets model to best fit with inliers
    inliers = Vector()
    modelFound = model.filterRansac(candidates,inliers,Niters,mindist,min_inlier_ratio);
    
    #write fit model to file if the model was found and it is good enough
    if modelFound and len(inliers)>minInliers:
        #if the option is set, 
        if outputTransformFile is not None:
          writeObjectToFile(model,outputTransformFile)
        if outputInliersFile is not None:
          writeObjectToFile(inliers,outputInliersFile)
          
    else:
        assert modelFound,'no suitable model found'
        assert len(inliers)>minInliers,'only %d inliers found, needed %d\n' % (len(inliers),minInliers)
        
    #print out results
    if verbose:
        print "%d inliers between %s and %s"%(len(inliers),targetFeatureFile,sourceFeatureFile)
        print "was model found?%s" % modelFound
        print "The model: %s" % model.createAffine().toString()
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extract Features from Image File")
    parser.add_argument('--targetFeatureFile',
                        help='The file with the features of the image to be registered to.')
    parser.add_argument('--sourceFeatureFile',
                        help='The file with the features of the image to transform/register.')
    parser.add_argument('--outputTransformFile',
                        default=None,
                        help='The file to save the transformation into')
    parser.add_argument('--outputInliersFile',
                        default=None,
                        help='The file to save the inliers into')
    parser.add_argument('--transformType',
                        default='rigid',
                        help='The transform type (rigid,affine,similarity)')
    parser.add_argument('--minDist',
                        default=2.5,
                        type=float,
                        help='minimum distance in pixels to consider feature an inlier')
    parser.add_argument('--minInliers',
                        default=8,
                        type=int,
                        help='minimum number of inliers to consider it a good model')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print out runtime information.')

    args = parser.parse_args()
    main(args.targetFeatureFile,
          args.sourceFeatureFile,
          outputTransformFile=args.outputTransformFile,
          verbose=args.verbose,
          outputInliersFile=args.outputInliersFile,
          modeltype=args.transformType,
          mindist=args.minDist,
          minInliers=args.minInliers)
    