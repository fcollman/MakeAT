#input, root directory of images
import argparse
import os
import numpy as np
import csv
import pandas as pd


def write_feature_extract_dependancies(f,df,feature_extract_module,map_chan=0,precommand=''):
  #setup all the feature extraction  dependancies
  uniq_sections=df.groupby(['ribbon','section']).groups.keys()
  uniq_sessions=df.groupby(['session']).groups.keys()
  uniq_stitches=df.groupby(['ribbon','session','section']).groups.keys()
   
  #make a shortcut to run feature extraction on all stitched images
  f.write('extract_features:')
  for (rib,sess,sect) in uniq_stitches:
      imgfeaturefile='feature_files/rib%04dsess%04dsect%04dch%04d.txt'%(rib,sess,sect,map_chan)
      f.write(imgfeaturefile + " ")
  f.write("\n\n")
  
  f.write("feature_files/%.txt:stitched_files/%.tif\n")
  f.write("\t"+precommand + " " + feature_extract_module + " " + "--imageFile " + "$<" + " --outputFile" + " $@" +"\n\n")
  
  #make each feature file dependant on the stiched images for the map channel
  #for (rib,sect) in uniq_sections:
  #  for sess in uniq_sessions:
  #    imagefile='stitched_files/rib%04dsess%04dsect%04dch%04d.tif'%(rib,sess,sect,map_chan)
  #    imgfeaturefile='feature_files/rib%04dsess%04dsect%04dch%04d.txt'%(rib,sess,sect,map_chan)
  #    f.write(imagefeaturefile + " : " + imagefile +"\n")
  #    f.write("\t"+precommand + " " + feature_command + " --inputImage " + imagefile + " --outputFile " + imgfeaturefile "\n\n")
     
  
def write_registration_dependancies(f,df,registration_module,precommand='',map_chan=0):
  
  #setup all the stitching transformation dependancies
  uniq_sections=df.groupby(['ribbon','section']).groups.keys()
  uniq_sessions=df.groupby(['session']).groups.keys()
  
  #make the registration transforms dependant on the feature files for each pair of map images that need to be registered
  for (rib,sect) in uniq_sections:
    for sess in uniq_sessions:
      transform_file='registration_transforms/rib%04dsess%04dsect%04d.txt'%(rib,sess,sect)
      
      if sess>0:
        targetfeaturefile='feature_files/rib%04dsess%04dsect%04dch%04d.txt'%(rib,0,sect,map_chan)
        sourcefeaturefile='feature_files/rib%04dsess%04dsect%04dch%04d.txt'%(rib,sess,sect,map_chan)
        f.write(transform_file+": ")
        f.write(targetfeaturefile+" "+sourcefeaturefile +"\n")
        f.write("\t"+precommand+registration_module +" --featurefile1 " + sourcefeaturefile + " --featurefile2 " + targetfeaturefile + " --outputTransformFile " + transform_file + " --modelType 1\n\n")
        
        
  #make a shortcut for running all the registeration steps
  f.write("register_sections: ")
  for (rib,sect) in uniq_sections:
    for sess in uniq_sessions:
      if sess>0:
        transform_file='registration_transforms/rib%04dsess%04dsect%04d.txt '%(rib,sess,sect)
        f.write(transform_file)
  f.write("\n\n")

def write_stitching_dependancies(f,df,stitching_module,precommand='',map_chan=0):
  
  
  #setup all the stitching transformation dependancies
  uniq_stitches=df.groupby(['ribbon','session','section']).groups.keys()
  
  f.write("stitching: ")
  for (rib,sess,sect) in uniq_stitches:
     f.write("stitch_layouts/rib%04dsess%04dsect%04d_stitch.txt "%(rib,sess,sect))
  f.write("\n")
  
  
  for (rib,sess,sect) in uniq_stitches:
    #rule for each unique section and imaging session
    layoutfile='stitch_layouts/rib%04dsess%04dsect%04d_stitch.txt'%(rib,sess,sect)
    imagefile='stitched_files/rib%04dsess%04dsect%04dch%04d.tif'%(rib,sess,sect,map_chan)
    
    f.write(layoutfile+" "+imagefile)
    f.write(":")
    
    #depends on the stiching module
    #f.write(stitching_module+" ")
    
    #depends on the images
    #pick out the images from the map_channel for this section
    map_images=df[(df['ribbon']==rib) & (df['session']==sess) & (df['section']==sect) & (df['ch']==map_chan)]
    map_images=map_images.sort('frame')
    
    #print map_images[['full_path','frame']]
    
    #this depends on all of them
    for index, row in map_images.iterrows():
      f.write("%s  "%row['full_path'])
      
    #command for making the stiching file and the stiched image of the map channel 
    f.write("\n\t%s%s "%(precommand,stitching_module))
    f.write("--outputLayout " + layoutfile + " --outputImage " + imagefile + " ")
    f.write("--imageFiles ")
    #with these images as inpus
    for index, row in map_images.iterrows():
      f.write("%s,"%row['full_path'])
      
    f.write(" --xoffsets ")
    for index,row in map_images.iterrows():
      f.write("%f,"%row['a02'])
    
    f.write(" --yoffsets ");
    for index,row in map_images.iterrows():
      f.write("%f,"%row['a12'])
      
    f.write("\n\n")  
    
def write_reconstruction_dependancies(f,df,reconstruction_module,precommand='',mapchan=0):
  #setup all the stitching transformation dependancies
  uniq_stitches=df.groupby(['ribbon','session','section','ch']).groups.keys()
    
  f.write("reconstruction: ")
  for (rib,sess,sect,chan) in uniq_stitches:
      
      imagefile='reconstruction/rib%04dsess%04dsect%04dch%04d.tif '%(rib,sess,sect,chan)
      f.write(imagefile)
  f.write('\n\n')
     
  for (rib,sess,sect,chan) in uniq_stitches:
      imagefile='reconstruction/rib%04dsess%04dsect%04dch%04d.tif'%(rib,sess,sect,chan)
      f.write(imagefile + ":")
      alignment_transform='alignment_transforms/rib%04dsess%04dsect%04dch%04d.tif.xml'%(rib,0,sect,mapchan)
      registration_transform='registration_transforms/rib%04dsess%04dsect%04d.txt'%(rib,sess,sect)
      layout_file='stitch_layouts/rib%04dsess%04dsect%04d_stitch.txt'%(rib,sess,sect)
      
      map_images=df[(df['ribbon']==rib) & (df['session']==sess) & (df['section']==sect) & (df['ch']==chan)]
      map_images=map_images.sort('frame')
      
      if sess>0:
        f.write('%s %s %s\n'%(alignment_transform,registration_transform,layout_file))
      else:
        f.write('%s %s\n'%(alignment_transform,layout_file))
        
      f.write('\t%s '%precommand)
      f.write('%s '%reconstruction_module)
      f.write('--imageFiles ')
      for index, row in map_images.iterrows():
          f.write("%s,"%row['full_path'])
      f.write(' ')
      
      f.write('--layoutFile %s '%layout_file)
      if sess>0:
        f.write('--registrationTransformFile %s '%registration_transform)
      f.write('--alignmentTransformFile %s '%alignment_transform)
      
      f.write('--outputFile %s '%imagefile)
      f.write('--boundBoxFile alignment_transforms/boundbox.xml')
      f.write('\n\n')
      


def write_pairwise_alignment_dependancies(f,df,pairwise_alignment_module,precommand='',map_chan=0,Nhood=5,minDist=15.0):
    uniq_sections=df.groupby(['ribbon','section']).groups.keys()
    uniq_sections.sort()
    
    Nsect=len(uniq_sections)
    f.write('pairwise_comparisons:')
    for (i,rib_sect) in enumerate(uniq_sections):
      (rib,sect)=rib_sect
      for k in range(i+1,i+Nhood):
        if k<Nsect:
          torib=uniq_sections[k][0]
          tosect=uniq_sections[k][1]
          pairwise_pointmatch_file=' pairwise_alignment_pointmatches/rib%04dsect%04d_to_rib%04dsect%04d.txt'%(rib,sect,torib,tosect)
          f.write(pairwise_pointmatch_file)
    f.write('\n\n')
    
    for (i,rib_sect) in enumerate(uniq_sections):
      (rib,sect)=rib_sect
      for k in range(i+1,i+Nhood):
        if k<Nsect:
          torib=uniq_sections[k][0]
          tosect=uniq_sections[k][1]
          sourcefeaturefile='feature_files/rib%04dsess%04dsect%04dch%04d.txt'%(rib,0,sect,map_chan)
          targetfeaturefile='feature_files/rib%04dsess%04dsect%04dch%04d.txt'%(torib,0,tosect,map_chan)
          
          pairwise_pointmatch_file='pairwise_alignment_pointmatches/rib%04dsect%04d_to_rib%04dsect%04d.txt'%(rib,sect,torib,tosect)
          f.write(pairwise_pointmatch_file +": " + sourcefeaturefile + " " + targetfeaturefile + "\n")
          f.write("\t%s%s "%(precommand,pairwise_alignment_module))
          f.write("--targetFeatureFile " + targetfeaturefile + " --sourceFeatureFile " + sourcefeaturefile + " --outputInliersFile " + pairwise_pointmatch_file + " --transformType affine --minDist %3.2f --minInliers 10 -v\n\n"%minDist)
 
 
def write_linear_alignment_dependancies(f,df,linear_alignment_module,apply_alignment_module,precommand='',map_chan=0):
  
    uniq_sections=df.groupby(['ribbon','section']).groups.keys()
    uniq_sections.sort()
    
    Nsect=len(uniq_sections)
    #write a shortcut to initiate linear alignment of all sections in session 0,in the map channel
    f.write('linear_alignment:') 
    for (rib,sect) in uniq_sections:
        linear_alignment_file=' linear_alignment_transforms/rib%04dsess%04dsect%04dch%04d.txt'%(rib,0,sect,map_chan)
        f.write(linear_alignment_file)
    f.write('\n\n')
    
    #create a rule for creating all_sections.txt, a simply list of the ribbon, section pairs in order
    f.write("all_sections.txt:state.csv\n")
    f.write('\t echo "')
    for (rib,sect) in uniq_sections:
        f.write("%d,%d"%(rib,sect)+'\\'+'n')
    f.write('" > all_sections.txt\n')
    
    #each of the linear_alignment_transforms for each section depends on all the pairwise comparisons being completed
    for rib,sect in uniq_sections:
        linear_alignment_file='linear_alignment_transforms/rib%04dsess%04dsect%04dch%04d.txt '%(rib,0,sect,map_chan)
        f.write(linear_alignment_file)
    f.write(':pairwise_comparisons all_sections.txt\n')
    
    #and those 
    f.write("\t%s%s "%(precommand,linear_alignment_module))
    f.write("--pairwiseDir pairwise_alignment_pointmatches --linearAlignmentDir linear_alignment_transforms --sectionList all_sections.txt\n\n")
    
    f.write("apply_linear_to_map:linear_alignment ")
    for rib,sect in uniq_sections:
        imagefile=' aligned_files/rib%04dsess%04dsect%04dch%04d.tif'%(rib,0,sect,map_chan)
        f.write(imagefile)
    f.write("\n")
    
    
    f.write("aligned_files/%.tif:linear_alignment_transforms/%.tif stitched_files/%.tif/n")
    
    
  
print("\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a state file describing the images in Stanfoord root folder format")
    #parser.add_argument('--inputDir', default=sys.stdout, type=argparse.FileType('r'),
    #    help='Path to the input directory.')
    parser.add_argument('--inputFile', help="Path to the state file.")
    parser.add_argument('--outputFile', help="Path to makefile to output.")
    args = parser.parse_args()
    
    inputFile = args.inputFile
    outputFile = args.outputFile
    
    
    assert os.path.isfile(inputFile), "'"+inputFile + "' is not a valid file"
    
ImageJCommand = os.path.expanduser('~/packages/Fiji.app/ImageJ-linux64')+ ' --headless '
renderJar = os.path.expanduser('~/FijiBento/target/render-0.0.1-SNAPSHOT.jar')
FijiPluginJar = os.path.expanduser('~/.m2/repository/sc/fiji/Fiji_Plugins/2.0.1/Fiji_Plugins-2.0.1.jar')
FijiBentoCommand  = 'java -cp %s:%s '%(renderJar,FijiPluginJar)
#scriptdir = '~/MakeAT/'
#stitching_module = scriptdir+'fiji_stitch.py'
stitching_module = 'org.janelia.alignment.StitchImagesByCC'

#feature_extract_module = scriptdir+'extract_features.py'
feature_extract_module = 'org.janelia.alignment.ComputeSiftFeaturesFromPath'

#registration_module = scriptdir+'register_images.py'
registration_module = 'org.janelia.alignment.MatchSiftFeaturesFromFile'

#linear_alignment_module = scriptdir + 'linear_align.py'
#apply_linear_alignment_module = scriptdir + 'apply_linear_align.py'

reconstruction_module = 'org.janelia.alignment.ReconstructImage'


map_chan=0

df=pd.read_csv(inputFile)
f = open(outputFile,'w')


#write the stitching dependancies to the file
write_stitching_dependancies(f,df,stitching_module,precommand=FijiBentoCommand)

#write the feature extraction dependancies
write_feature_extract_dependancies(f,df,feature_extract_module,precommand=FijiBentoCommand)
  
#write the registration dependancies to the file
write_registration_dependancies(f,df,registration_module,precommand=FijiBentoCommand)

#write the reconstruction dependancies to the file
write_reconstruction_dependancies(f,df,reconstruction_module,precommand=FijiBentoCommand)

  
#write the pairwise alignment dependancies to the file
#write_pairwise_alignment_dependancies(f,df,registration_module,precommand=ImageJCommand)

#write_linear_alignment_dependancies(f,df,linear_alignment_module,apply_linear_alignment_module,precommand=ImageJCommand)

f.close()
