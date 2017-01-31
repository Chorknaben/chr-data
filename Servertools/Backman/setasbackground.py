#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import os.path
import shutil
import argparse
import subprocess

conf = {
	"DATABASE_FILE"  : ".setasbackground.py.db",
	"SCALE_BINARY"   : "scaleImage",
	"GAUSS_BINARY"   : "applyGaussianBlur",
	"DATA_DIRECTORY" : "../../data/",
	"MAXIMUM_CALC_RES" : ("2560x1600", "2560x1440", "2048x1536"),
}



def getargs():
	parser = argparse.ArgumentParser(description='Chorserv-Dateistrukturbaum in Chorserv-JSONstruktur umwandeln.')
	parser.add_argument('action', help='Aktion: add use list remove recalculate blur')
	parser.add_argument('-f', '--file', help='Diese Datei auswählen')
	parser.add_argument('-i', '--id', help='Diese ID auswählen')
	return parser.parse_args()

def warn(warnmsg):
	print "WARN:\t%s" % (warnmsg)

def info(infomsg):
	print "INFO:\t%s" % (infomsg)

def err(errormsg):
	print "ERR:\t%s" % (errormsg)
	sys.exit(1)

def add(filename):
	dbptr = open(conf["DATABASE_FILE"], "a+")

	lines = dbptr.readlines()
	for f in lines:
		spl = f.split("\t")
		if spl[1].rstrip() == filename:
			err("Already exists: %s (ID: %s). Did you mean: 'recalculate'?" %(filename, spl[0]))

	id = hex(len(lines))

	calculate(filename, id, False)

	dbptr.write("%s\t%s\n" %(id, filename))
	dbptr.close()
	return

def calculate(filename, id, override_existing):
	cmdScl = "convert chorhintergrund.png -resize {0}^ -gravity Center -crop {0}+0+0 +repage chorhintergrund.png"
	cmdBlr = "convert {0} -blur 0x24 {1}"
	todir  = conf["DATA_DIRECTORY"] + str(id) + "/"

	shutil.copyfile(filename, "chorhintergrund.png")

	if not os.path.isdir(todir):
		os.mkdir(todir)

	info("Calculating Background resolutions")
	for maxres in conf["MAXIMUM_CALC_RES"]:
		subprocess.call(cmdScl.format(maxres), shell=True)
		subprocess.call("./scaleImage chorhintergrund.png True %s" % (todir), shell=True)

	info("Calculating Blurred Backgrounds. This will take a while.")
	for i in os.listdir(todir):
		blurdir = todir + "blur/"
		if not os.path.isdir(blurdir):
			os.mkdir(blurdir)
		subprocess.call(cmdBlr.format(todir+i, blurdir+i), shell=True)

	info("Calculating Blurred Background fragments. This will take a while.")
	for i in os.listdir(todir):
		if i.endswith(".png"):
			subprocess.call("./applyGaussianBlur {0} True {1}".format(todir+i, todir), shell=True)
	return

def list_():
	dbptr = open(conf["DATABASE_FILE"], "r")
	print "\n ", "ID\tFILE"
	for i in dbptr.readlines():
		print " ", i.rstrip()
	print
	dbptr.close()
	return

def use(hash):
	d = conf["DATA_DIRECTORY"]

	# Delete existing Symlinks
	info("Clearing %s" % d)
	for i in os.listdir(d):
		if os.path.islink(d+i):
			os.unlink(d+i)
	for i in os.listdir(d+"blur/"):
		if os.path.islink(d+"blur/"+i):
			os.unlink(d+"blur/"+i)

	a = os.path.abspath(d) + "/"

	# Create new Symlinks
	cnt = [ i for i in os.walk(d+hash) ]
	for m in cnt[0][2]:
		os.symlink(a+str(hash)+"/"+m,a+m)
	for m in cnt[1][2]:
		os.symlink(a+str(hash)+"/blur/"+m,a+"blur/"+m)

	info("Now using %s." % (hash))



def remove(ptr):
	dbptr = open(conf["DATABASE_FILE"], "w+")
	newfile = []

	lines = dbptr.readlines()
	for i in lines:
		splt = i.split("\t")
		if not splt[0] == ptr:
			newfile.append(i)

	if len(lines) == len(newfile):
		err("No such ID: %s" %(ptr))

	dbptr.writelines(newfile)
	dbptr.close()

	shutil.rmtree(conf["DATA_DIRECTORY"] + str(ptr) )
	return

def recalculate(ptr):
	return

def blur(ptr):
	return

def decide_switch(filename, hash):
	if filename and not hash:
		return f2hash(filename)
	elif not filename and hash:
		return hash
	else:
		err("Ambiguity Error: Please supply only one of -f, -i")

def f2hash(filename):
	dbptr = open(conf["DATABASE_FILE"], "r")
	for i in dbptr.readlines():
		splt = i.split("\t")
		if splt[1].rstrip() == filename:
			return splt[0]
	err("This file is not calculated: %s. Did you mean: add?" % (filename))

def check_integrity(fileorhash):
	return

if __name__ == '__main__':
	args = getargs()

	info("Starting up.")

	if args.file:
		check_integrity(args.file)

	if args.id:
		check_integrity(args.id)

	if args.action == "add":
		add(args.file)
	elif args.action == "use":
		definitive_switch = decide_switch(args.file, args.id)
		use(definitive_switch)
	elif args.action == "list":
		list_()
	elif args.action == "remove":
		definitive_switch = decide_switch(args.file, args.id)
		remove(definitive_switch)
	elif args.action == "recalculate":
		definitive_switch = decide_switch(args.file, args.id)
		recalculate(definitive_switch)
	elif args.action == "blur":
		definitive_switch = decide_switch(args.file, args.id)
		blur(definitive_switch)
	else:
		err("Not a valid action: %s" % (args.action))

	info("done.")

	sys.exit(0)
