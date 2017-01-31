#!/usr/bin/env python2.7
import os
import os.path
import sys
import json as JSON
import argparse
import shutil
import filecmp
from PIL import Image, ImageOps

def getargs():
	parser = argparse.ArgumentParser(description='Chorserv-Dateistrukturbaum in Chorserv-JSONstruktur umwandeln.')
	parser.add_argument('strukturlocation', help='Der Pfad zum Strulturbaum')
	parser.add_argument('-f', '--file', help='Ausgabe-Jsondatei')
	parser.add_argument('-w', '--writeto', help='Zu diesem Chorserv-Bilderpfad schreiben')
	return parser.parse_args()

def warn(warnmsg):
	print "WARN:\t%s" % (warnmsg)

def info(infomsg):
	print "INFO:\t%s" % (infomsg)

def err(errormsg):
	print "ERR:\t%s" % (errormsg)
	sys.exit(1)

def checkTree(location):
	# In order to be valid, a tree must have the following: 
	# 1) At least one subfolder
	# 2) In each subfolder: File chapter.name
	# 3) Optional: Datei chapter.order
	# Deeper Structures will be ignored, Files with accompanying <filename>.info are optional and will not be checked.
	tree = [ f for f in os.walk(location) ]
	okstructs = []

	if tree[0][1] == []:
		err("Keine Kategoriestrukturen gefunden. Die ganze Geschichte waere sinnlos.")

	if tree[0][2] != []:
		warn("Ignoriere Dateien im Rootverzeichnis des Strukturbaums.")

	for i in xrange(1, len(tree)):
		if not "chapter.name" in tree[i][2]:
			warn("Kategoriestruktur '%s' hat kein chapter.name und ist deshalb ungueltig. ueberspringen." % (tree[i][0]))
		else:
			info("Erkannte Kategoriestruktur: '%s'" % (tree[i][0]))
			okstructs.append(tree[i])
			if len(tree[i][2]) < 2:
				warn("Kategoriestruktur '%s' enthaelt keine weiteren Dateien." % (tree[i][0]))

	if okstructs == []:
		err("Alle vorhandenen Strukturen sind ungueltig. Struktur.py kann nicht weiterarbeiten.")

	return okstructs

def buildJSONStruktur(structs, loc, beschreibepfad):
	# JSON Syntax einer Kategorie 
	# {"name":{"title":"Titel","caption":"Caption","content":"Inhalt",childs:[["id","name"]]}}
	json = []
	reihenfolge = []
	for element in structs:
		reihenfolge.append(element[0].split('/')[-1])
	reihenfolge.sort()
	print reihenfolge

	globImgCounter = 0
	for element in reihenfolge:
		match = filter(lambda x: x[0] == loc+element, structs)
		print match
		fhdl = open(match[0][0] + '/chapter.name', 'r').readlines()

		title = fhdl[0].rstrip()
		caption = fhdl[1].rstrip()
		
		content = ""
		if len(fhdl) > 2:
			content = fhdl[2]

		childs = []

		matchingimages = match[0][2]

		# preprocessing, we work with lowercase file extensions here
		for x in matchingimages:
			info("Preprocessing folder")

			fullpath = "{0}/{1}".format(match[0][0], x)

			if x.lower().endswith(".jpg") or x.lower().endswith(".jpeg"):
				without_ext = os.path.splitext(x)[0]
				os.rename(fullpath, "{0}/{1}.jpg".format(match[0][0], without_ext))

				# If the creator of the structure worked with .info files, we've gotta rename them, too
				if os.path.exists("{0}.info".format(fullpath)):
					os.rename("{0}.info".format(fullpath), "{0}/{1}.jpg.info".format(match[0][0], without_ext))

		if "chapter.order" in matchingimages:
			info("Detected chapter.order file in Struktur: Overriding alphanumerical sort")
			order = []
			with open(match[0][0] + '/chapter.order', 'r') as orderhdl:
				order = orderhdl.readlines()
			for i in range(0,len(order)):
				order[i] = order[i].rstrip()

				# Don't care if supplying file ext. or not in order file
				if not order[i].lower().endswith(".jpg"):
					order[i] += ".jpg"
			matchingimages = order
			print matchingimages
		else:
			matchingimages.sort()
		for img in matchingimages:
			if img == "chapter.name":
				continue 
			if img.endswith(".info"):
				continue
			img_info = match[0][0]+"/"+img+".info"
			img_name = ""
			if os.path.exists(img_info):
				with open(img_info, "r") as f:
					img_name = f.readlines()[0].rstrip()
			else:
				info("\tImage \"%s\" has no .info: Using Filename for name" % (img))
				img_name = os.path.splitext(img)[0]
			childs.append([globImgCounter, img_name])
			if beschreibepfad != None:
				thumbnail(match[0][0] + "/" + img, globImgCounter, (340, 210), beschreibepfad)
			globImgCounter += 1

		json.append(
			{'category':
				{'title':title,
				 'caption':caption,
				 'content':content,
				 'childs':childs}})

	return JSON.dumps(json, sort_keys=True, indent=4, separators=(',',': '))

def thumbnail(img, id, size, path):
	if not path.endswith('/'):
		path = path + '/'
	if not os.path.exists(path):
		err("Specified path %s does not exists, unable to write to filesystem." % path)
	else:
		for p in ("thumbs/", "real/"):
			if not os.path.exists(path + p):
				info("Creating necessary dir for thumbnail creation: %s" % p)
				os.makedirs(path + p)

	info("Processing File: %s\t%s" % (id, img))

	# Create Thumbnail of Image
	image = Image.open(img)
	thumb = ImageOps.fit(image, size, Image.ANTIALIAS)
	thumb.save(path + "thumbs/%s" % (id), "JPEG")

	# Create Real of Image
	shutil.copyfile(img, path + "real/%s" % (id))



if __name__ == '__main__':
	args = getargs()
	if not args.strukturlocation.endswith('/'):
		args.strukturlocation = args.strukturlocation+'/'

	info("Struktur beginnt.")

	structs = checkTree(args.strukturlocation)
	jsonstr = buildJSONStruktur(structs, args.strukturlocation, args.writeto)

	if args.file is None:
		args.file = "out.json"

	info("Writing Struktur to %s" % (args.file))

	open(args.file, 'w').write(jsonstr)

	info("Done. Exiting")

	sys.exit(0)
	