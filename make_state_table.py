#input, root directory of images
import argparse
import os
import convertmetadata
import numpy as np
import csv

print("\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a state file describing the images in Stanfoord root folder format")
    #parser.add_argument('--inputDir', default=sys.stdout, type=argparse.FileType('r'),
    #    help='Path to the input directory.')
    parser.add_argument('inputDirectory', nargs=1, help="Path to the input directory.")
    parser.add_argument('outputFile', nargs=1, help="Path to output file.")
    args = parser.parse_args()
    
    rootdir = args.inputDirectory[0]
    outputfile = args.outputFile[0]
    

    assert os.path.isdir(rootdir), "'"+rootdir + "' is not a valid directory"
    
        

#output, state table ala bill karsh
#bill's format
#Z tileID a00 a01 a02 a10 a11 a12 col row cam full_path

#my format
#includes ribbon number, section number, session number, channel number
#tileID ribbon section frame a00 a01 a02 a10 a11 a12 session ch full_path
#tileID = ch + 1000*frame + 1000*1000*section + 1000*1000*1000*1000*ribbon + 1000*1000*1000*1000*100*session

#pull out all the tif files that are subdirectories under this
tif_files=[]
for (dirpath, dirnames, filenames) in os.walk(rootdir):
  tif_files.extend([os.path.join(dirpath,f) for f in filenames if os.path.splitext(f)[1]=='.tif'])
  
Nfiles=len(tif_files)


#get the unique channel names
ch_names=sorted(set([os.path.split(os.path.split(f)[0])[1] for f in tif_files]))
print "channels "
print ch_names
print "\n"

#get the unique image session names

image_sessions = sorted(set([os.path.split(os.path.split(os.path.split(f)[0])[0])[1] for f in tif_files]))
print "imaging sessions:"
print image_sessions
print "\n"

#in this example there is only one ribbon
ribbon = 0
  
frames=[]
sections=[]
ch_indexes=[]
sessions=[]
metafiles=[]
stitchsect_ids=[]
for file in tif_files:
  #the frame index
  [dir,f]=os.path.split(file)
  f=os.path.splitext(f)[0]
  (f,part,frame)=f.partition('_F')
  frame=int(frame)
  
  #the section index
  (f,part,section)=f.partition('-S')
  section=int(section)
  
  #find the index for the channel
  ch_name=os.path.split(os.path.split(file)[0])[1]
  if 'dapi' in ch_name.lower():
    ch_index=0
  else:
    ch_index=ch_names.index(ch_name)
  

  #find the index for the imaging sessions
  sess_name=os.path.split(os.path.split(os.path.split(file)[0])[0])[1] 
  session_index = image_sessions.index(sess_name)
  
  #get the metafile for this file
  metafile=os.path.splitext(file)[0] + '_metadata.txt'
  metafiles.append(metafile)
  
  ch_indexes.append(ch_index)
  sections.append(section)
  frames.append(frame)
  sessions.append(session_index)

  stitchsect_id=ch_index+1000*section+1000*1000*1000*ribbon+1000*1000*1000*100*session_index
  stitchsect_ids.append(stitchsect_id)
  
uniq_stitch_sect_ids=sorted(set(stitchsect_ids))

shiftx=np.zeros(Nfiles)
shifty=np.zeros(Nfiles)

for stitch_sect_id in uniq_stitch_sect_ids:
  #print stitch_sect_id
  indexes = [i for i,x in enumerate(stitchsect_ids) if x == stitch_sect_id]
  #print map(tif_files.__getitem__, indexes)
  these_metafiles=map(metafiles.__getitem__, indexes)
  #these_files=map(tif_files.__getitem__,indexes)

  (metadata,norm_coords)=convertmetadata.get_freeframe_pix_coords(these_metafiles)
  #print norm_coords
  
  norm_coords=np.array(norm_coords)
  norm_coords=norm_coords-np.tile(norm_coords.min(axis=0),(norm_coords.shape[0],1))
  
  shiftx[indexes]=norm_coords[:,0]
  shifty[indexes]=norm_coords[:,1]

f = open(outputfile, 'w+')
csvwrite = csv.writer(f, delimiter=',')
csvwrite.writerow(['tileID','ribbon','section','frame','a00','a01','a02','a10','a11','a12','session','ch','full_path'])
                            
for i,file in enumerate(tif_files):

  #tileID ribbon section frame a00 a01 a02 a10 a11 a12 session ch full_path
  tileID =  ch_indexes[i] + 1000*frames[i] + 1000*1000*sections[i] + 1000*1000*1000*1000*ribbon + 1000*1000*1000*1000*100*sessions[i]
  #[1 0 0 1] and [a2 a5] = image [left top].
  csvwrite.writerow([tileID,ribbon,sections[i],frames[i],1,0,shiftx[i],0,1,shifty[i],sessions[i],ch_indexes[i],tif_files[i]])
  
f.close()
  
  