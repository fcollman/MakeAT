import argparse
from serialize_interface import *

def make_SIFT_parameters(fdSize=4,fdBins=8,maxOctaveSize=1024,minOctaveSize=64,steps=3,initialSigma=1.6):
    
    from jython_imports import FloatArray2DSIFT
    
    p = FloatArray2DSIFT.Param()
    
    p.fdSize = fdSize
    p.fdBins = fdBins 
    p.maxOctaveSize = maxOctaveSize
    p.minOctaveSize = minOctaveSize
    p.steps = steps
    p.initialSigma = initialSigma
    
    return p

def enhance_contrast(imp,percent_saturated=.5):
    from jython_imports import ContrastEnhancer,Calibration,ImageStatistics,Measurements
    
    ip=imp.getProcessor()
    #enhance contrast of image
    cal = Calibration(imp)
    reference_stats = ImageStatistics.getStatistics(ip, Measurements.MIN_MAX, cal)
    cenh=ContrastEnhancer()
    cenh.setNormalize(True)
    cenh.stretchHistogram(ip,.5,reference_stats)
    
    return ip

def extract_features(ip,p):
    from jython_imports import SIFT,FloatArray2DSIFT,ArrayList
    
    ip_float= ip.convertToFloat()
    ijSift = SIFT(FloatArray2DSIFT(p))
    fs = ArrayList()
    ijSift.extractFeatures(ip_float, fs )
    
    return fs
    
    
def main(imageFile,outputFile, verbose):
    """Run the main Fiji-based functionality.
    """
    from jython_imports import IJ,SIFT,FloatArray2DSIFT,ArrayList

    if verbose:
        "Extracting features from %s" % imageFile

    #open the image
    imp= IJ.openImage(imageFile)
    
    #enhance the contrast
    percent_saturated=.5
    ip = enhance_contrast(imp,percent_saturated)
    
    #get features
    maxsize = min(imp.getHeight(),imp.getWidth())
    p = make_SIFT_parameters(maxOctaveSize=maxsize)
    features = extract_features(ip,p)
    
    #write object to file
    writeObjectToFile(features,outputFile)
    
    #print some results
    if verbose:
        "Extracting features from %s" % imageFile
        print "found %d features in image at %s"%(len(features),imageFile)
        print "used contrast enhance with %3.2f " % percent_saturated
    
  
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extract Features from Image File")
    parser.add_argument('--imageFile', help='The file to be opened.')
    parser.add_argument('--outputFile',help='The output file to store the features.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print out runtime information.')

    args = parser.parse_args()
    main(args.imageFile, args.outputFile,args.verbose)
    