#!/usr/bin/env python
#-*- coding: utf-8 -*-

import datetime
import glob
import fnmatch
import os
import random
import re
import shutil
import static
import sys
import time
import argparse
from libxmp.utils import file_to_dict
import iptcinfo
import threading
from threading import Thread
from Queue import Queue
import filelock
from itertools import combinations
from selenium import webdriver
from depot.manager import DepotManager

try:
  from PIL import Image
  from PIL import ImageFont
  from PIL import ImageDraw
  from PIL import ImageFile
  from PIL.ExifTags import TAGS
except ImportError:
  try:
    import Image
  except ImportError:
    print 'Requires Python Imaging Library. See README.'
    sys.exit(1)

parser = argparse.ArgumentParser()

parser.add_argument("--dir", dest='photo_dir', type=str, required=True,
                   help='path to image dir that will be used to generate gallery')
parser.add_argument("--verbose", dest='verbose', type=bool, required=False, default=False,
                   help='More verbose mode - bool - True/False')
parser.add_argument("--index", dest='index', type=bool, required=False, default=False,
                   help='Generate only index and take screenshot - bool - True/False')
parser.add_argument("--copy", dest='copy', type=bool, required=False, default=False,
                   help='Copy images from main dir to combination of dirs - bool - True/False')
parser.add_argument("--thumbs", dest='thumbs', type=bool, required=False, default=False,
                   help='Generate thumbs from originals in every combination dir - bool - True/False')
parser.add_argument("--text", dest='text', type=bool, required=False, default=False,
                   help='Generate text in full and thumb images in generated dir - bool - True/False')
parser.add_argument("--makeall", dest='makeall', type=bool, required=False, default=False,
                   help='make everything in all steps - bool - True/False')

args = parser.parse_args()
root_dir = args.photo_dir
verbose = args.verbose
copy = args.copy
thumbs = args.thumbs
text = args.text
index = args.index
makeall = args.makeall

q = Queue()
lock = threading.Lock()

def ListFiles(regex, path):
  """Returns list of matching files in path."""
  rule = re.compile(fnmatch.translate(regex), re.IGNORECASE)
  return [name for name in os.listdir(path) if rule.match(name)] or None


def ListDirs(path):
  """Returns list of directories in path."""
  return [d for d in os.listdir(path) if os.path.isdir(
      os.path.join(path, d))]


def Now(time=True):
  """Returns formatted current time."""
  if time:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  else:
    return datetime.datetime.now().strftime('%Y%m%d')


def RandomThumb(page):
  """Returns path to random thumbnail for a given page."""
  return random.choice(
      glob.glob(os.path.join(page.split('/')[0], '*_thumb.jpg')))


def PrepareTmpDir():
  """Creates directories for images in root directory for tmp."""
  try:
    os.chdir(root_dir)
  except OSError:
    print 'Could not cd into %s' % root_dir
    sys.exit(1)

  fs = ListFiles('*.jpg', '.')
  if fs:
    tmp_datehour = "tmp_%s" % Now(time=False)
    if os.path.exists(tmp_datehour):
         shutil.rmtree(tmp_datehour)
    if not os.path.exists(tmp_datehour):
        print 'Creating directory: %s' % tmp_datehour
        os.makedirs(tmp_datehour)
    for jpg in fs:
      if not os.path.exists(os.path.join(tmp_datehour, jpg)):
        shutil.copy2(jpg, tmp_datehour)
  return tmp_datehour

def PrepareKeywordsDir():
  try:
    os.chdir(root_dir)
  except OSError:
    print 'Could not cd into %s' % root_dir
    sys.exit(1)

  ## generate dict for all files exported in root_dir
  dict_struct = PrepeareDict(root_dir)

  new_dict = {}
  dir_list = []

  for k,v in dict_struct.iteritems():
      if dict_struct[k]['keywords']:
         combination_keywords = sum([map(list, combinations(dict_struct[k]['keywords'], i)) for i in range(len(dict_struct[k]['keywords']) + 1)], [])
         for keyword in combination_keywords:
             if len(keyword) > 1:
                     jkeyword = '_'.join(keyword)
		     newdir = os.path.join(root_dir,jkeyword)
                     print "Copy originals to dir %s" % newdir
                     #tmpdir = os.path.join(root_dir,tmp_dir)
		     if not os.path.exists(newdir):
			   print "-> Creating directory %s based on keyword %s" % (newdir, keyword)
			   os.makedirs(newdir)
		     filetmp = os.path.join(root_dir,dict_struct[k]['jpg'])
		     filedst = os.path.join(newdir,dict_struct[k]['jpg'])
		     if verbose and copy:
			print "* Copy file %s to %s" % (filetmp, filedst)
                     dir_list.append(newdir)
                     if copy or makeall:
		        shutil.copyfile(filetmp, filedst)
             else:
                continue

  for newdir in dir_list:
   new_dict = PrepeareDict(newdir)
   if thumbs or makeall:
      GenerateThumbnails(newdir)
   WriteTextOnImage(new_dict,newdir)
   if index or makeall:
      WriteGalleryPage(new_dict,newdir)

def get_field (exif,field):
  # get exif k/v's
  for (k,v) in exif.iteritems():
     if TAGS.get(k) == field:
        return v

def upperfirst(x):
    return x[0].upper() + x[1:]

def addImageText(jpg, number, price, font_size):
          im = Image.open(jpg)
	  im.convert('RGBA')
	  size = width, height = im.size
	  # get a font
	  fnt = ImageFont.truetype('/Library/Fonts/Times New Roman Bold.ttf', font_size)
	  draw = ImageDraw.Draw(im,'RGBA')
	  draw.text((40,40), str(number) + ". " + price.decode("utf-8"), font=fnt, fill=(0,0,255,128))
	  im.save(jpg)
          im.close()

#def addImageText():
#		 qelement = q.get(block=True)
#                 if verbose:
#   	              print "Elements in queue done: %d" % q.qsize()
#		 im = Image.open(qelement[0])
#		 im.convert('RGBA')
#		 size = width, height = im.size
#		 # get a font
#		 fnt = ImageFont.truetype('/Library/Fonts/Times New Roman Bold.ttf', qelement[3])
#		 draw = ImageDraw.Draw(im,'RGBA')
#		 draw.text((40,40), str(qelement[1]) + ". " + qelement[2].decode("utf-8"), font=fnt, fill=(0,0,255,128))
#		 im.save(qelement[0])
#		 im.close()
#		 q.task_done()
def PrepeareDict(finaldir):
  try:
    os.chdir(finaldir)
    jpgs = ListFiles('*[0-9].j*g', '.')
  except OSError:
    print 'Could not cd into %s and read files' % finaldir
    sys.exit(1)

  count = 0

  desc_dict = {}

  for jpg in jpgs:
      if verbose:
         print 'Opening for metadata read >>-----> %s' % jpg
      else:
         print "Opening %s" % jpg
      im = Image.open(jpg, "r")

      exif_data = im._getexif()
      xmp = file_to_dict(jpg)

      try:
         iptc = iptcinfo.IPTCInfo(jpg)
         caption = iptc.data['caption/abstract']
      except:
         if verbose:
            print "No IPTC in image"
         continue

      if caption is None:
         print '!!!! Image has no caption !!!!!'
         continue

      elif '|' not in caption and caption is not None:
              caption_price = caption
              caption_desc = ""

      else:
              caption_price, caption_desc = caption.split("|")

      caption_price = caption_price.strip()
      caption_desc = caption_desc.strip()
      if caption_price:
        caption_price = upperfirst(caption_price)
      if caption_desc:
        caption_desc = upperfirst(caption_desc)

      caption = caption.decode("utf-8")
      keywords = iptc.keywords

      if verbose:
        print 'Keywords |----> %s' % keywords

      try:
             if caption_price and caption_desc:
                count = count + 1
                desc_dict[count] = {}
                desc_dict[count]["number"] = count
                desc_dict[count]["price"] = caption_price
                desc_dict[count]["description"] = caption_desc
                desc_dict[count]["keywords"] = keywords
                desc_dict[count]["jpg"] = jpg
                if verbose:
                   print "Metadata |----> Number: %s Price: %s Description: %s" % (count, caption_price, caption_desc)
      except:
         print '!!!! Image has no caption field or IPTC read error or no IPTC !!!!!'
         continue

  print "Generated dict with size %s with files in dir in number of %s" % (len(desc_dict), len(jpgs))
  if verbose:
     print 'Returned dict structure: %s size: %s' % (desc_dict, len(desc_dict))
  return desc_dict

def GenerateThumbnails(finaldir):
  """Generates thumbnails for gallery pages.

  Args:
    page: str, name of page for thumbnails.
    jpgs: list, jpg files to create thumbnails for.
  Returns:
    url_imgs: list, image links to write.
  """
  try:
    os.chdir(finaldir)
    jpgs = ListFiles('*[0-9].j*g', '.')
  except OSError:
    print 'Could not cd into %s and list files' % finaldir
    sys.exit(1)

  c_exist = 0
  c_save = 0
  c_small = 0
  pc = 0
  count = 0

  desc_dict = {}

  for jpg in jpgs:
      if verbose:
         print 'Opening for thumb generate >>-----> %s' % jpg
      im = Image.open(jpg, "r")

      if im.size > static.min_size:
        thumb = '%s_%s.%s' % (jpg.split('.')[0], 'thumb', 'jpg')
        if not os.path.exists(thumb):
          im.thumbnail(static.thumb_size, Image.ANTIALIAS)
	  print "|----- Generating thumb %s" % thumb
          im.save(thumb, 'JPEG')
          c_save += 1

      #    if (pc == 100):  # progress counter
      #      print '%s: wrote 100 thumbnails, continuing' % page
      #      pc = 0
      #    pc += 1

        else:
          c_exist += 1

      else:
        if '_thumb.jpg' not in jpg:
          c_small += 1
   # except IOError as e:
   #   print 'Problem with %s: %s, moving to %s' % (jpg, e, static.tmp)
   #   try
   #     shutil.move(jpg, static.tmp)
   #   except shutil.Error:
   #     print 'Could not move %s' % jpg
   #     pass

  print '%d new thumbnails, %d already exist, %d too small' % (
      c_save, c_exist, c_small)

def WriteTextOnImage(newdir_dict,newdir):
        try:
          os.chdir(newdir)
        except OSError:
          print "No such directory, could not cd to %s" % keyword_dir

        ## now we need prepare index per each dir from dirlist

        counter = 0

        for k,v in newdir_dict.items():
 #           for item in v['keywords']:
               #print os.path.basename(keyword_dir), item, v['keywords']
 #              if os.path.basename(keyword_dir) == item:
            if verbose:
               print "Adding %s" % v
            counter += 1
            newdir_dict[counter] = v
            v['number'] = counter
            price = v['price']
            jpg = v['jpg']
            thumb = '%s_%s.%s' % (jpg.split('.')[0], 'thumb', 'jpg')
            v['thumb'] = thumb
            jpg_file = os.path.join(newdir, jpg)
            jpg_thumb = os.path.join(newdir, thumb)
          ### full jpeg elements to queue
    #             qelements = []
    #                  qelements.append(jpg_file)
    #                  qelements.append(counter)
    #                  qelements.append(price)
    #                  qelements.append(static.font_size_full)
    #                  q.put(qelements)
    #                  qelements = []
    #                  qelements.append(jpg_thumb)
    #                  qelements.append(counter)
    #                  qelements.append(price)
    #                  qelements.append(static.font_size_thumb)
    #                  q.put(qelements)

          #print "Added % elements to queue" % counter*2
          #t = threading.Thread(target=addImageText, args=(jpg_file,counter,price))
          #t.start()
            if text or makeall:
               addImageText(jpg_file, counter, price, static.font_size_full)
               addImageText(jpg_thumb, counter, price, static.font_size_thumb)

def CreateScreenShot(index_name):
    fullpath = os.path.join(os.getcwd(),index_name)
    depot = DepotManager.get()
    driver = webdriver.PhantomJS()
    driver.set_window_size(1024, 768) # set the window size that you need 
    url = "file://%s" % fullpath
    driver.get(url)
    driver.save_screenshot('index_screenshoot.png')

def WriteGalleryPage(newdir_dict, newdir):
        try:
          os.chdir(newdir)
        except OSError:
          print "No such directory, could not cd to %s" % newdir

        print "Writing gallery index in: %s" % newdir

        if len(newdir_dict) > 0:
            with open(static.index_mini, 'w') as index_file:
                index_file.write(static.header % "galeria") 
                """index_file.write(static.timestamp % Now())"""
                count_columns = 0
                index_file.write('\n<section id="photos">')
                #index_file.write("\n<table>")
                for i in range(1, len(newdir_dict)+1):
                   url_imgs = static.images % (newdir_dict[i]['jpg'], newdir_dict[i]['thumb'])
                   index_file.write(url_imgs)
                index_file.write("\n</section>")
                index_file.write("\n</br>")
            index_file.close()     
            # copy mini index
            shutil.copyfile(static.index_mini, static.index)
            with open(static.index, 'a+') as index_file_full:
                index_file_full.write("\n<table>")
                for i in range(1, len(newdir_dict)+1):
                  indexed_description = "\n<tr><td>%s. </td><td>%s. %s</td></tr>" % (newdir_dict[i]['number'], newdir_dict[i]['price'], newdir_dict[i]['description'])
                  index_file_full.write(indexed_description)
                index_file_full.write("\n</table>")
                index_file_full.write(static.footer)
	# after index generation create screenshot from index
        CreateScreenShot(static.index_mini)


def WriteIndex():
  """Write index file with gallery links and thumbnails in root path."""
  os.chdir(root_dir)

  with open(static.index, 'w') as index_file:
    index_file.write(static.header % 'Ekspozycja')
    """index_file.write(static.timestamp % Now())"""

    page_count = 0
    for page in sorted(glob.glob('*/%s' % static.index)):
      page_count += 1
      try:
        for _ in range(static.n_thumbs):
          index_file.write(static.img_src % RandomThumb(page))
        index_file.write(static.url_dir % (page, page.split('/')[0]))
      except IndexError:
        print '%s: No thumbnails found, removing' % page
        os.unlink(page)

    index_file.write(static.footer)

  print 'Wrote %s with %s gallery link(s)' % (
      os.path.join(root_dir, static.index), page_count)

def jpeglist(tmpdir):
  os.chdir(tmpdir)
  try:
      jpgs = sorted(ListFiles('*.jpg', '.'))[::-1]
  except TypeError:
      print '%s: No images found' % tmpdir
      return
  return jpgs

def main():
  """Main function."""
  PrepareKeywordsDir()

if __name__ == '__main__':
  main()
