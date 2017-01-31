import struktur

import os
import sys
import json as JSON
import argparse

def getargs():
	parser = argparse.ArgumentParser(description='Presseverzeichnis in Chorserv-JSONstruktur umwandeln')
	parser.add_argument('strukturlocation', help='Der Pfad zum Presseverzeichnis')
	parser.add_argument('-f', '--file', help='Ausgabe-Jsondatei')
	parser.add_argument('-w', '--writeto', help='Zu diesem Chorserv-Pressepfad schreiben')
	return parser.parse_args()


def checkPresseFolder(path):
	files = [i[2] for i in os.walk(path)][0]

	infof = filter(lambda x: x.endswith(".info"), files)
	realf = filter(lambda x: not x.endswith(".info"), files)

	# mhhh
	if len(infof) != len(realf):
		struktur.err("Not all files have an accompanying .info")

	return realf

def buildJSONStruktur(files, location, writeto):
	json = []
	globPresseCnt = 0

	files.sort()
	for f in files:
		info = location + f + ".info"
		fhdl = open(info, 'r').readlines()

		name = fhdl[0].rstrip()
		url  = "/presse/%s" % globPresseCnt
		caption = fhdl[1].rstrip()
		date = fhdl[2].rstrip()

		if writeto != None:
			struktur.thumbnail(location + f, globPresseCnt, (676,420), writeto)

		json.append({'name':name,'url':url,'date':date,'caption':caption})
		globPresseCnt += 1

	return JSON.dumps({'presse':json}, sort_keys=True, indent=4, separators=(',',': '))


if __name__ == '__main__':
	args = getargs()
	if not args.strukturlocation.endswith('/'):
		args.strukturlocation = args.strukturlocation+'/'

	struktur.info("Struktur-Presse beginnt.")

	files = checkPresseFolder(args.strukturlocation)
	jsonstr = buildJSONStruktur(files, args.strukturlocation, args.writeto)

	if args.file is None:
		args.file = "out-presse.json"

	struktur.info("Writing Struktur to %s" % (args.file))

	open(args.file, 'w').write(jsonstr)

	struktur.info("Done. Exiting")

	sys.exit(0)
