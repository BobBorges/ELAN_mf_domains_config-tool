#!/usr/bin/env python3
import argparse, sys, os, shutil, time
import xml.etree.ElementTree as et

# LICENSE GNU gpl-3 http://www.gnu.org/licenses/gpl-3.0.html
# Author assumes no liability. Read and understand what the program does before you use it.

#####################
### Start Options ###

mf_loc = None

### End Options ###
###################

def set_default_file_location(args):
    if args.domainsFileLocation:
        with open('mk_mf_config.py', 'r') as this:
            this = this.readlines()
            for i, line in enumerate(this):
                if line.startswith('mf_loc ='):
                    this[i] = 'mf_loc = "'+args.domainsFileLocation+'"\n'
        with open('mk_mf_config.py', 'w') as new_this:
            new_this.writelines(this)
        print("The mf_domains.pfsx file location has been changed to {}.".format(args.domainsFileLocation))
    if args.locchk:
        if mf_loc:
            print("The location of your mf_domains.pfsx file is set to:", mf_loc)
        else:
            parser.error('The location for mf_domains.pfsx has not been set. Run with "set -l" and provide a path to your mf_domains file.')

def ask_overwrite():
    ovrwrt = str(input("~~~~~~~~~~\nThere's already an OLD file. Do you want to overwrite it? (y|n): ")).lower().strip()          
    if ovrwrt == "y":
        return True
    if ovrwrt == "n":
        print("Decide how you want to handle your historical files, then try again.")
        time.sleep(1)
        print("...quitting...")
        time.sleep(1)
        exit()
    else:
        ask_overwrite()

def mk_history():
    if mf_loc:
        shutil.copyfile(mf_loc+"/mf_domains.pfsx", mf_loc+"/mf_domains.pfsx.OLD")
    else:
        shutil.copyfile("mf_domains.pfsx", "mf_domains.pfsx.OLD")

def generate_file(args):
    if args.fileList and os.path.isfile(args.fileList):
        with open(args.fileList, 'r') as fL:
            file_list = fL.readlines()
            file_list = [f.strip() for f in file_list]
    else:
        parser.error("Your file list doesn't exist. Maybe check that the path and filename is specified correctly.")

    if args.src_path:
        if args.src_path.endswith("/"):
            file_list = [args.src_path+f for f in file_list]
        else:
            file_list = [args.src_path+"/"+f for f in file_list]

    if args.src_path:
        print('"SRC_PATH" is set to:', args.src_path)
    print("Source file list is:", args.fileList, "\nThe batch name will be:", args.batchName)

    if args.update:
        if mf_loc:
            if os.path.isfile(mf_loc+"/mf_domains.pfsx"):
                if os.path.isfile(mf_loc+"/mf_domains.pfsx.OLD"):
                    ask_overwrite()
                    mk_history()
                else:
                    mk_history()

                mf_domains_tree = et.parse(mf_loc+"/mf_domains.pfsx.OLD")
                mf_domains_root = mf_domains_tree.getroot()
                for preflist in mf_domains_root:
                    if preflist.get("key") == "DomainNames":
                        batch_name = et.Element("String")
                        batch_name.text = args.batchName
                        batch_name.tail = "\n\t"
                        preflist[-1].tail = "\n\t\t"
                        preflist.append(batch_name)

                mf_domains_root[-1].tail = "\n\t"
                new_path_list = et.SubElement(mf_domains_root, "prefList")
                new_path_list.text = "\n\t\t"
                new_path_list.tail = "\n"
                new_path_list.set("key", args.batchName+".Paths")
                for f in file_list:
                    new_str = et.Element("String")
                    new_str.text = f
                    if f == file_list[-1]:
                        new_str.tail = "\n\t"
                    else:
                        new_str.tail = "\n\t\t"
                    new_path_list.append(new_str)

                tree = et.ElementTree(mf_domains_root)
                tree.write(mf_loc+"/mf_domains.pfsx", encoding='utf-8', xml_declaration=True) 
                        
            else:
                parser.error('You\'re trying to update a file that doesn\'t exist. Check that your mf_domains file is set correctly.')
        else:
            parser.error('The location for mf_domains.pfsx has not been set. Run with "set -l" and provide a path to your mf_domains file.')
    else:
        
        print('"REPLACE" is set')
        preferences = et.Element("preferences")
        preferences.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        preferences.set("version", "1.1")
        preferences.set("xsi:noNamespaceSchemaLocation", "http://www.mpi.nl/tools/elan/Prefs_v1.1.xsd")
        preferences.text = "\n\t"        

        domains_lst = et.SubElement(preferences, "prefList")
        domains_lst.set("key", "DomainNames")
        domains_lst.text = "\n\t\t"
        domains_lst.tail = "\n\t"
        new_domain = et.SubElement(domains_lst, "String")
        new_domain.text = args.batchName
        new_domain.tail = "\n\t"

        new_path_list = et.SubElement(preferences, "prefList")
        new_path_list.set("key", args.batchName+".Paths")
        new_path_list.text = "\n\t\t"
        new_path_list.tail = "\n"
        for f in file_list:
            new_str = et.SubElement(new_path_list, "String")
            new_str.text = f
            if f == file_list[-1]:
                new_str.tail = "\n\t"
            else:
                new_str.tail = "\n\t\t"

        tree = et.ElementTree(preferences)

        if args.replace:
            if mf_loc:
                if os.path.isfile(mf_loc+"/mf_domains.pfsx"):
                    if os.path.isfile(mf_loc+"/mf_domains.pfsx.OLD"):
                        ask_overwrite()
                        mk_history()
                    else:
                        mk_history()
                    tree.write(mf_loc+"/mf_domains.pfsx", encoding='utf-8', xml_declaration=True)                
                else:
                    tree.write(mf_loc+"/mf_domains.pfsx", encoding='utf-8', xml_declaration=True)
            else:
                parser.error('The location for mf_domains.pfsx has not been set. Run with "set -l" and provide a path to your mf_domains file.')                
        else:
            if os.path.isfile("mf_domains.pfsx"):
                if os.path.isfile("mf_domains.pfsx.OLD"):
                    ask_overwrite()
                    mk_history()
                else:
                    mk_history()
                tree.write("mf_domains.pfsx", encoding='utf-8', xml_declaration=True)                
            else:
                tree.write("mf_domains.pfsx", encoding='utf-8', xml_declaration=True)

def undo_prev(args):
    if mf_loc:
        if os.path.isfile(mf_loc+"/mf_domains.pfsx.OLD"):
            os.rename(mf_loc+"/mf_domains.pfsx.OLD", mf_loc+"/mf_domains.pfsx") 
            print('Replaced mf_domains.pfsx with the OLD file')
        else:
            parser.error('There\'s no OLD file at the specified location. Check the specified location using "set -c" and make sure there is an mf_domains.pfsx.OLD file at that location.')
    else:
        parser.error('The location for mf_domains.pfsx has not been set. Run with "set -l" and provide a path to your mf_domains file.')

#
##########
# PARSER #
##########
#
parser = argparse.ArgumentParser(description='Update or create an mf_domains.pfsx file for your ELAN multifile search batches.')
subparsers = parser.add_subparsers()

# `SET` OPTIONS

set_options = subparsers.add_parser('set', help='Sets stuff. Run "set -h" for more info.')
set_options.add_argument('-l', '--mf_domains-file-location', type=str, dest='domainsFileLocation', metavar='', help='This sets the location of your mf_domains.pfsx file. If you have never set this it will be None.')
set_options.add_argument('-c', '--check-mf-domains-file-loc', dest='locchk', action='store_true', help='Use to check where this program thinks your mf_domains.pfsx file is.')
set_options.set_defaults(func=set_default_file_location)

# `GENERATE` OPTIONS

gen_options = subparsers.add_parser('generate', help='Use this option to generate mf_domains.pfsx file. Run "generate -h" for more info.')
u_or_n = gen_options.add_mutually_exclusive_group()
u_or_n.add_argument('-u', '--update', dest='update', action='store_true', help='this will update the existing mf_domains file (renaming the old one to mf_domains.pfsx.OLD) – adds new batch to existing')
u_or_n.add_argument('-r', '--replace', dest='replace', action='store_true', help='this will replace the existing mf_domains file (renaming the old one to mf_domains.pfsx.OLD) – new file with only new batch')
gen_options.add_argument('-p', '--src-path', type=str, dest='src_path', metavar='', help='this will provide a path in the case where the .eaf list does not contain absolute paths. If this is not set, the assumption is that the .eaf list contains absolute paths')
gen_options.add_argument('fileList', type=str, help='a .txt file with list of .eaf files to be included in the mf search batch. If the list does not contain absolute paths, use the "-p" option.')
gen_options.add_argument('batchName', type=str, help='a name for the batch. This is how you will find your new multifile search group in Elan.')
gen_options.set_defaults(func=generate_file)

# `UNDO`

undo = subparsers.add_parser('undo', help="Use this option to undo previous --update or --replace. Resets mf_domains.pfsx.OLD as mf_domains.pfsx.")
undo.set_defaults(func=undo_prev)

def main():
    args = parser.parse_args()

    if len(vars(args)) == 0:
        parser.print_help()
        exit()
    elif sys.argv[1] == 'set' or sys.argv[1] == 'generate' or sys.argv[1] == 'undo':
        print(sys.argv[1])
        args.func(args)
    else:
        parser.print_help()
        exit()
    print('Done')

if __name__ == '__main__':
	main()
