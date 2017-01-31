import struktur

import os
import sys
import shutil
import json as JSON
import argparse

SPLIT = False

def getargs():
	parser = argparse.ArgumentParser(description='Musikverzeichnis in Chorserv-MUSIKstruktur umwandeln')
	parser.add_argument('strukturlocation', help='Der Pfad zum Musikverzeichnis')
	parser.add_argument('-f', '--file', help='Ausgabe-Jsondatei')
	parser.add_argument('-w', '--writeto', help='Zu diesem Chorserv-Musikpfad schreiben')
	return parser.parse_args()

def checkMusikFolder(folder):
	files = [i[2] for i in os.walk(folder)][0]

	mp3s = 0
	for f in files:
		if f.endswith(".mp3"):
			mp3s += 1

	if mp3s == 0:
		struktur.err("Keine MP3 Dateien zu strukturieren in %s" % (folder))

	return files

def buildJSONStruktur(files, location, writeto):
	json = []
	globMusikCnt = 0

	files.sort()
	for f in files:
		real = f[0:f.find(".mp3")]
		destination_file = f.replace(" ", "_")
		if writeto != None:
			if not writeto.endswith("/"):
				writeto += "/"
			struktur.info("Processing %s" % f)
			if SPLIT:
				os.system("mp3splt \"%s\" 00.00.000 00.30.000 > /dev/null 2>&1" %(location+f))
				created_src_file = location + f[0:f.find(".mp3")]+"_00m_00s__00m_30s.mp3"
				os.system("mv \"%s\" \"%s\"" %(created_src_file, writeto + destination_file))
			else:
				shutil.copyfile(location + f, writeto + destination_file)


		json.append({"displayname":real,"pathname":destination_file})

	return JSON.dumps({'musik':json}, sort_keys=True, indent=4, separators=(',',': '))

if __name__ == '__main__':
	args = getargs()
	if not args.strukturlocation.endswith('/'):
		args.strukturlocation = args.strukturlocation+'/'

	struktur.info("Struktur-Musik beginnt.")

	files = checkMusikFolder(args.strukturlocation)
	jsonstr = buildJSONStruktur(files, args.strukturlocation, args.writeto)

	if args.file is None:
		args.file = "out-musik.json"

	struktur.info("Writing Struktur to %s" % (args.file))

	open(args.file, 'w').write(jsonstr)

	struktur.info("Done. Exiting")

	sys.exit(0)
