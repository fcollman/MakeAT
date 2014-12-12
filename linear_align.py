import argparse
from serialize_interface import *
import csv

def main(pairwiseDir,linearAlignmentDir,sectionList,verbose=False,lam=0.1,maxError=15,plateauSize=200,max_iters=1000):
  """Run the main Fiji-based functionality.
  """
  from jython_imports import IJ,ArrayList,RigidModel2D,AffineModel2D,Tile,InterpolatedAffineModel2D,TileConfiguration
  
  #get a list of the sections (assumes the list is in order)
  sections=[]
  csvfile=open(sectionList, 'r')
  reader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for row in reader:
    if len(row)==2:
      sections.append((int(row[0]),int(row[1])))
  csvfile.close()
  
  #initialize the tiles and their models
  tiles =  ArrayList()
  m=AffineModel2D() #fit an affine
  r=RigidModel2D() #but use rigid to regularize
  
  #add all the tiles we need
  for (rib,sect) in sections:
    tiles.add( Tile( InterpolatedAffineModel2D( m.copy(), r.copy(), lam ) ) )
    
  #initialize tileConfiguration  
  tileConfiguration =  TileConfiguration()
  
  #get a list of all pairwise files (has _to_ in midddle)
  pairwise_files = [f for f in os.listdir(pairwiseDir) if len(f.split('_to_'))==2]
	
  #loop over these files
  for file in pairwise_files:
    pairwise_file=os.path.join(pairwiseDir,file)
    print pairwise_file
    #read the point matches from this file
    pointMatches=readObjectFromFile(pairwise_file)
    
    #pull out the section indexes from the filename
    (fromstring,tostring)=file.split('_to_')
    rib=int(fromstring[3:7])
    sect=int(fromstring[11:15])
    torib=int(tostring[3:7])
    tosect=int(tostring[11:15])
    
    #now find the linear index into tile that corresponds to each of these
    #ribbon,section pairs
    from_index=sections.index((rib,sect))
    to_index=sections.index((torib,tosect))
    
    print "connecting %d to %d"%(from_index,to_index)
    #pull out their respective tiles	 
    t1 = tiles.get(from_index)
    t2 = tiles.get(to_index)
    
    #add them to the configuration
    tileConfiguration.addTile(t1)
    tileConfiguration.addTile(t2)
		
    #connect these tiles with their point matches
    #AHH NOT SURE WHICH IS WHICH HERE, could swap t1,t2
    t1.connect(t2,pointMatches)
		
  #prealign? tiles
  #(see https://github.com/trakem2/TrakEM2/blob/6cb318e3ca077e217444158090ab607223cf921c/TrakEM2_/src/main/java/mpicbg/trakem2/align/RegularizedAffineLayerAlignment.java line 405)
  nonPreAlignedTiles=tileConfiguration.preAlign()
  
  #optimize overall alignment
  tileConfiguration.optimize(maxError,max_iters,plateauSize)

  #print out results if verbose
  if verbose:
    print " average displacement: " + " %.3f" % tileConfiguration.getError() + "px"
    print " minimal displacement: " + " %.3f" % tileConfiguration.getMinError() + "px"
    print " maximal displacement: " + " %.3f" % tileConfiguration.getMaxError() + "px"

  #loop over tiles to get resulting model
  for (i,rib_sect) in enumerate(sections):
    #construct the file path to save the result
    (rib,sect)=rib_sect
    linear_alignment_file='rib%04dsess%04dsect%04dch%04d.txt'%(rib,0,sect,0)
    filepath=os.path.join(linearAlignmentDir,linear_alignment_file)
    
    #get the linear model
    linear_model=tiles.get(i).getModel().createAffine() 
    
    #write the resulting transformation to file
    writeObjectToFile(linear_model,filepath)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find Final Alignment Transformations Given Pairwise Point Matches")
    parser.add_argument('--pairwiseDir',
                        help='The directory with all the pairwise point matches.')
    parser.add_argument('--linearAlignmentDir',
                        help='The directory in which to store all the transformations.')
    parser.add_argument('--sectionList',
                        default = 'all_sections.txt',
                        help='a csv file will all ribbon,sect pairs in order')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print out runtime information.')

    args = parser.parse_args()
    main(args.pairwiseDir,args.linearAlignmentDir,sectionList=args.sectionList,verbose=args.verbose)
    