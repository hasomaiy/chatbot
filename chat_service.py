#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import tarfile
import datetime
import urllib
import urllib3
from flask import Flask, flash, request, redirect, url_for,render_template
# from werkzeug import secure_filename
from flask_restful import Resource, Api
import string
import bot_helper_service
import glob
import re
import custom_difflib
import sqlite3
import shutil
import preprocessor

basedir = os.path.abspath(os.path.dirname(__file__))

from logging import Formatter, FileHandler

handler = FileHandler(os.path.join(basedir, 'log.txt'), encoding='utf8')
handler.setFormatter(
    Formatter("[%(asctime)s] %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S")
)

app = Flask(__name__)
app.logger.addHandler(handler)

# This is the path to the upload directory
# app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['UPLOAD_FOLDER'] = './uploads'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'gz'])
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    print(app.config['ALLOWED_EXTENSIONS'])
    print('.' in filename and filename.rsplit('.', 1)[1])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
api = Api(app)


class CreateUrl(Resource):
    bot = ''
    kernel = ''
    app_name = ''
    pathUPfolder = ''
    kernel2 = ''
    WORD = ''
    WORD2 = ''
    cro_flo = ''
    file = ''

    def get(self):

        return {"success": 0, "message": "Method Not Allowed."}

    def post(self):
        runtime_appname = []
        app_name = request.values.get("app_name");
        CreateUrl.app_name = request.values.get("app_name");
        print(request.values)
        routes_info()
        if not app_name:
            return {'success': 0, 'message': 'Please Provide me the App Name.'}
        if 'file' not in request.files:
            return {'success': 0, 'message': 'Please Provide me file.'}
        # Get the name of the uploaded file
        file = request.files['file']
        CreateUrl.file = request.files['file']

        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            # filename = secure_filename(file.filename)
            # Move the file form the temporal folder to
            # the upload folder we setup
            path = os.path.join(app.config['UPLOAD_FOLDER'], app_name)
            if not os.path.exists(path):
                os.makedirs(path)
            pathBackup = os.path.join(path, 'tar');
            if not os.path.exists(pathBackup):
                os.makedirs(pathBackup)
            # uploadFilename = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            uploadFilename = 'div'

            file.save(os.path.join(pathBackup, uploadFilename))
            pathUP = os.path.join(path, 'untar');
            if not os.path.exists(pathUP):
                os.makedirs(pathUP)
            pathUPfolder = os.path.join(pathUP, uploadFilename)
            CreateUrl.pathUPfolder = os.path.join(pathUP, uploadFilename)
        if not os.path.isdir(pathUPfolder):
            os.mkdir(pathUPfolder)
        if os.path.exists(pathUPfolder):
            shutil.rmtree(pathUPfolder)
            # os.makedirs(pathUPfolder)
            print(os.path.join(pathBackup, uploadFilename),'DDD')
            t = tarfile.open(os.path.join(pathBackup, uploadFilename), 'r')
            t.extractall(pathUPfolder);
            route_list = routes_info()
            checkFlag = 0

            cro_flo = create_questions_and_spell_corrector(pathUPfolder)

            CreateUrl.cro_flo = create_questions_and_spell_corrector(pathUPfolder)

            for line in sorted(route_list):
                if str(app_name) in line:
                    checkFlag = 1

            if 1 == checkFlag:
                del_route(str(app_name))
                routes_info()
            else:

                f = open(pathUPfolder + "/std-startup.xml", 'r')
                if f.mode == 'r':
                    contents = f.read()
                    f.close()
                    contents = str.replace(contents, ">*.aiml", ">" + pathUPfolder + "/*.aiml")
                    contents = str.replace(contents, "small_talk/", pathUPfolder + "/small_talk/")
                    p = open(pathUPfolder + "/std-startup.xml", "w")
                    p.write(contents)
                    p.close()

                CreateUrl.bot = bot_helper_service.WebMessages(app_name, pathUPfolder, 'std-startup.xml', "", "", "", "", "")

                bot = bot_helper_service.WebMessages(app_name, pathUPfolder, 'std-startup.xml', "", "", "", "", "")
                print("kernel 1")
                kernel = bot.loadKernel("load aiml b")
                CreateUrl.kernel = bot.loadKernel("load aiml b")
                print("kernel 2")
                kernel2 = bot.loadKernel2("load aiml b2")
                CreateUrl.kernel2 = bot.loadKernel2("load aiml b2")

                print(kernel2)
                WORD = bot.loadSpellCheck("")
                WORD2 = bot.loadSpellCheck("")

                CreateUrl.WORD = bot.loadSpellCheck("")
                CreateUrl.WORD2 = bot.loadSpellCheck("")

                op_line = []
                for rule in app.url_map.iter_rules():

                    options = {}
                    for arg in rule.arguments:
                        options[arg] = "[{0}]".format(arg)

                    methods = ','.join(rule.methods)
                    url = url_for(rule.endpoint, **options)
                    line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
                    print("LINE IN POST: ", line)
                    op_line.append(line)

                if (app_name in str(op_line)):
                    print("REPETITION")
                    # print app.view_functions
                    # del app.view_functions[app_name]
                    # print app.view_functions

                    bot_helper_service.WebMessages(
                        app_name, pathUPfolder,
                        "std-startup.xml", kernel,
                        kernel2, WORD, WORD2, cro_flo)

                    # api.add_resource(bot_helper_service.WebMessages, "/bot/" + app_name, endpoint=str(app_name),
                    #				 resource_class_kwargs={"data": app_name, 'aiml_path': pathUPfolder,
                    #										'std_startup': "std-startup.xml", 'kernel': kernel,
                    #										'kernel2': kernel2, 'words': WORD, 'words2': WORD2});

                    print(app.view_functions)
                else:
                    print("FIRST TIME CREATION")
                    api.add_resource(bot_helper_service.WebMessages, "/bot/" + app_name, endpoint=str(app_name),
                                     resource_class_kwargs={"data": app_name, 'aiml_path': pathUPfolder,
                                                            'std_startup': "std-startup.xml", 'kernel': kernel,
                                                            'kernel2': kernel2, 'words': WORD, 'words2': WORD2,
                                                            'cross_flow': cro_flo});
                    print("just after add resource")
                    print(app.view_functions)
                    print(type(app.view_functions))

                runtime_appname.append(app_name)
                routes_info()
            return {'success': 1, 'message': 'File Uploaded'}
        else:
            return {'success': 0, 'message': 'Please Upload Valid File'}

    def updateKernel(self, app_name, question, answer, topic_to_update):

        pathUPfolder = "./uploads/" + app_name + "/untar/div"
        runtime_appname = []
        app_name = app_name

        self.update_aiml(question, answer, topic_to_update, pathUPfolder)

        print("SENDING PATYH UP: ", pathUPfolder)
        f = open(pathUPfolder + "/std-startup.xml", 'r')
        if f.mode == 'r':
            contents = f.read()
            f.close()
            contents = string.replace(contents, ">*.aiml", ">" + pathUPfolder + "/*.aiml")
            contents = string.replace(contents, "small_talk/", pathUPfolder + "/small_talk/")
            p = open(pathUPfolder + "/std-startup.xml", "w")
            p.write(contents)
            p.close()

        CreateUrl.bot = bot_helper_service.WebMessages(app_name, pathUPfolder, 'std-startup.xml', "", "", "", "", "")

        bot = bot_helper_service.WebMessages(app_name, pathUPfolder, 'std-startup.xml', "", "", "", "", "")
        print("kernel 1")
        kernel = bot.loadKernel("load aiml b")
        CreateUrl.kernel = bot.loadKernel("load aiml b")
        print("kernel 2")
        kernel2 = bot.loadKernel2("load aiml b2")
        CreateUrl.kernel2 = bot.loadKernel2("load aiml b2")

        print(kernel2)
        WORD = bot.loadSpellCheck("")
        WORD2 = bot.loadSpellCheck("")

        CreateUrl.WORD = bot.loadSpellCheck("")
        CreateUrl.WORD2 = bot.loadSpellCheck("")

        op_line = []
        for rule in app.url_map.iter_rules():

            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            url = url_for(rule.endpoint, **options)
            line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
            print("LINE IN POST: ", line)
            op_line.append(line)

        bot_helper_service.WebMessages(
            app_name, pathUPfolder,
            "std-startup.xml", kernel,
            kernel2, WORD, WORD2, CreateUrl.cro_flo)

        runtime_appname.append(app_name)
        routes_info()

    def update_aiml(self, question, answer, topic, path):

        a = path + topic + '.aiml'

        topic_list = []

        fo_path = path + "/update_temp.aiml"
        fo = open(fo_path, 'w+')

        '''
		fo_path_spell = path + "/spell_correcter.txt"
		fo_spell = open(fo_path_spell, 'a')
		fo_spell.close()
		fo_spell.write(" "+question.lower())
		'''
        preprocessed_q = preprocessorprop().preliminary_processing(question, path)

        print("SENT:", question)
        print("RECEIVED:", preprocessed_q)

        conn = sqlite3.connect(path + '/div_ChatBot_database.db')

        general_qna = 'general_qna'

        if topic.lower() == 'general':
            conn.execute(" INSERT INTO %s VALUES ( \" %s \" )" % (general_qna, str(preprocessed_q['input_str'])))
            int2 = []
            generalqna_cur = conn.execute('SELECT * from general_qna')
            for row in generalqna_cur:
                int2.append(row[0])

            str_update = \
                "<?xml version=\"1.0\" encoding=\"UTF-8\" ?> \
<aiml version=\"1.0\">" + "\n<category>\n<pattern>" + preprocessed_q[
                    'input_str'] + "</pattern>\n<template>" + answer + "</template>\n</category></aiml>\n"

        else:
            conn.execute(" INSERT INTO %s VALUES ( \" %s \" )" % (topic, preprocessed_q['input_str']))

            str_update = \
                "<?xml version=\"1.0\" encoding=\"UTF-8\" ?> \
    <aiml version=\"1.0\">" + "<topic name = \"" + topic + "\">" + "\n<category>\n<pattern>" + preprocessed_q[
                    'input_str'] + "</pattern>\n<template>" + answer + "</template>\n</category>\n</topic>\n</aiml>\n"

        fo.write(str_update)
        fo.close()

        print("IN CHATTTTTTTTTTTTTTTTER", glob.glob("./uploads/hdfc/untar/div/*"))

        conn.commit()
        conn.close()

        return preprocessed_q


def create_questions_spellchecker():
    app_name = request.values.get("app_name");
    path = os.path.join(app.config['UPLOAD_FOLDER'], app_name)

    pathUP = os.path.join(path, 'untar')
    print("PATH: ", pathUP)


def create_questions_and_spell_corrector(fileup):
    print("FILE UP TABLE: ", fileup)

    ############ OPENING SQLITE DATABASE #########
    conn = sqlite3.connect(fileup + '/div_ChatBot_database.db')

    filename2 = fileup + "/test.txt"
    thefile = open(filename2, 'w')

    open_questions = fileup + "/questions.txt"
    open_spell = fileup + "/spell_correcter.txt"
    # open_questions = fileup+"/questions_topic.txt"

    all_questions_list = []
    filenames = []
    for name in glob.glob(fileup + '/*.aiml'):
        filenames.append(name)
    lenfile = len(filenames)

    basename = []
    for i in range(0, len(filenames)):
        basename.append(os.path.splitext(os.path.basename(filenames[i]))[0])
    print("BASE NAME", basename)

    ##################### MAKING DATABASE TABLE OF EACH FILE ####################################
    tables = []
    for i in range(0, lenfile):
        filewise_questions = []
        sent1 = []
        tablename = basename[i]
        try:
            conn.execute("DROP TABLE %s" % (str(basename[i])))

            conn.execute('''CREATE TABLE %s
				   (
				   PATTERN VARCHAR
				   );''' % (basename[i]))
            print(basename[i] + " Table created successfully in TRY")
        except:
            conn.execute('''CREATE TABLE %s
						   (
						   PATTERN VARCHAR
						   );''' % (str(basename[i])))
            print(basename[i] + "Table created successfully in EXCEPT")
        f = open(filenames[i], 'r')
        print(filenames[i])
        data = f.read()
        print("data has been read")
        filewise_questions.extend(re.findall(r'<pattern>(.*?)</pattern>', data, re.DOTALL))
        for i in range(0, len(filewise_questions)):
            words1 = filewise_questions[i].split()
            sent = sorted(words1)
            sent = " ".join(sent)
            sent = " " + sent + " "
            sent1.append(sent)

        i = 0
        new_list = []
        while i < len(sent1):
            new_list.append(sent1[i:i + 1])
            i += 1

        new_list = [tuple(l) for l in new_list]

        conn.executemany("INSERT into " + tablename + " VALUES  (?) ", new_list)

    sent1 = []
    thefile = open(open_questions, 'w')
    for item in all_questions_list:
        thefile.write("%s\n" % item)

    for line in all_questions_list:
        line = line.replace("*", '')
        line = line.replace("?", "")
        line = line.replace("'", "")
        line = line.replace(":", "")
        line = line.replace(",", "")
        line = line.replace("-", "")
        line = line.replace("_", "")
        line = line.replace("(", "")
        line = line.replace(")", "")
        line = line.replace(".", "")
        line = line.replace("\"", "")
        line = line.replace(";", "")
        line = line.lstrip()

        thefile.write("%s\n" % line)

    for i in range(0, lenfile):
        f = open(filenames[i], 'r')
        data = f.read()
        all_questions_list.extend(re.findall(r'<pattern>(.*?)</pattern>', data, re.DOTALL))
    thefile1 = open(open_spell, 'a')

    for item in all_questions_list:
        thefile.write("%s\n" % item)

    for line in all_questions_list:
        line = line.lower()
        line = line.replace("*", '')
        line = line.replace("?", "")
        line = line.replace("'", "")
        line = line.replace(":", "")
        line = line.replace(",", "")
        line = line.replace("-", "")
        line = line.replace("_", "")
        line = line.replace("(", "")
        line = line.replace(")", "")
        line = line.replace(".", "")
        line = line.replace("\"", "")
        line = line.replace(";", "")
        line = line.lstrip()

        thefile1.write("%s\n" % line)

    filenames1 = []
    for name in glob.glob(fileup + '/*.aiml'):
        filenames1.append(name)
        lenfile = len(filenames1)
    print("new code", filenames1)
    save_lines = []
    print(len(filenames1))
    final_match = []
    input_div = '<topic name = '
    divdiv = []
    final_list = []

    for i in range(0, len(filenames1)):
        with open(filenames1[i]) as f: save_lines.append(f.readlines()[0:6])
        # print ("SAVELINES", save_lines[i])
        s1 = save_lines[i]

        div1 = sorted(save_lines[i], key=lambda x: custom_difflib.SequenceMatcher(None, x, input_div).ratio(),
                      reverse=True)
        # print (div1[0])
        # print ("new code ", div1)
        temp_str = div1[0].replace('<topic name = ', '')
        temp_str = temp_str.replace('>', '')
        temp_str = temp_str.replace('\"', "")
        temp_str = temp_str.replace('\n', "")
        temp_str = temp_str + ".aiml"
        final_list.append(temp_str)
    original_list = []
    for i in range(0, len(filenames)):
        fil = filenames[i]
        fil = fil.replace("./", "")
        original_list.append(fil)
    print("MY ALL AIMLs ARE", basename)
    print("MY TOPICS R IN", final_list)
    basename1 = []
    for i in range(0, len(basename)):
        mybase = str(basename[i])
        mybase = mybase + ".aiml"
        basename1.append(mybase)

    print(basename1)
    print(final_list)

    croflo = []
    bf1 = []
    for i in range(0, len(basename)):
        cam = str(basename[i])
        cam = cam + ".aiml"
        bf1.append(cam)
    print("basenames....", bf1)
    for mac in final_list:
        if mac in bf1:
            croflo.append(mac)
    print("my final necessary details for cross flow topis handling are:..")
    print("cross flow: ", croflo)

    general = list(set(basename1) - set(final_list))

    print("GENERAL FILES", general)

    with open(fileup + "/div_res.txt", "w") as outfile:
        for f in general:
            with open(fileup + "/" + f, "r") as infile:
                outfile.write(infile.read())

    my_general_que = []
    f = open(fileup + "/div_res.txt", 'r')
    data = f.read()
    my_general_que.extend(re.findall(r'<pattern>(.*?)</pattern>', data, re.DOTALL))
    for i in range(0, len(my_general_que)):
        words1 = my_general_que[i].split()
        sent = sorted(words1)
        sent1.append(" ".join(sent))

    ####################### GENERAL QNA DATABASE TABLE ##########################################

    thefile12 = open(fileup + "/general_qna.txt", 'w')

    for line in sent1:
        line = line.replace("*", '')
        line = line.replace("?", "")
        line = line.replace("'", "")
        line = line.replace(":", "")
        line = line.replace(",", "")
        line = line.replace("-", "")
        line = line.replace("_", "")
        line = line.replace("(", "")
        line = line.replace(")", "")
        line = line.replace(".", "")
        line = line.replace("\"", "")
        line = line.replace(";", "")

        line = line.lstrip()

        thefile12.write("%s\n" % line)

    general_qna = "general_qna"

    try:

        conn.execute("DROP TABLE %s" % (general_qna))

        conn.execute('''CREATE TABLE %s
	       (
	       PATTERN VARCHAR
	       );''' % (general_qna))
        print("GENERAL QNA Table created successfully in TRY")
    except:
        conn.execute('''CREATE TABLE %s
			       (
			       PATTERN VARCHAR
			       );''' % (general_qna))
        print("GENERAL QNA Table created successfully in EXCEPT")

    for line in sent1:
        conn.execute(" INSERT INTO %s VALUES ( \" %s \" )" % (general_qna, str(line)))

    print("Successfully inserted values in GENERAL QNA TABLE")

    generlqna_cur = conn.execute("SELECT * from %s" % (general_qna))

    gnrl = []
    for row in generlqna_cur:
        gnrl.append(row[0])

    print("Printing Table Value", gnrl)

    conn.commit()

    ################## Small Talk Database #########################
    small_talk = 'small_talk'
    try:

        conn.execute("DROP TABLE %s" % (small_talk))

        conn.execute('''CREATE TABLE %s
				       (
				       PATTERN VARCHAR
				       );''' % (small_talk))
        print("SMALL_TALK Table created successfully in TRY")
    except:
        conn.execute('''CREATE TABLE %s
						       (
						       PATTERN VARCHAR
						       );''' % (small_talk))
        print("SMALL TALK Table created successfully in EXCEPT")

    #########################################################################

    small_talk_folder = fileup + "/small_talk"
    filenames = []
    for name in glob.glob(small_talk_folder + '/*.aiml'):
        filenames.append(name)
    lenfile = len(filenames)

    print("SMALL TALK FILES: ", filenames)
    print("Length of small talk is: ", lenfile)

    basename = []
    for i in range(0, len(filenames)):
        basename.append(os.path.splitext(os.path.basename(filenames[i]))[0])
    print("BASE NAMES of small talk", basename)
    filewise_questions = []
    for i in range(0, len(filenames)):

        f = open(filenames[i], 'r')
        print(filenames[i])

        data1 = f.read()
        print("data has been read from file: ", filenames[i])
        filewise_questions.extend(re.findall(r'<pattern>(.*?)</pattern>', data1, re.DOTALL))
        for i in range(0, len(filewise_questions)):
            words1 = filewise_questions[i].split()
            # sent = sorted(words1)
            sent = filewise_questions[i]
            # print (sent)
            # sent = " " + sent + " "
            # sent1.append(sent)
            # print (sent)
            conn.execute("INSERT INTO %s VALUES ( \" %s \" )" % (small_talk, str(sent)))

    # f.close()
    print("Successfully inserted values in SMALL_TALK table")

    return croflo
    conn.commit()
    conn.close()


def routes_info():
    output = []
    endpoints = []

    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)
    endpoints.append(rule.endpoint)
    for line in sorted(output):
        print(line)

    return endpoints


def del_route(endpoint):
    checkFlag = 0
    index = 0;
    for rule in app.url_map.iter_rules():
        index = index + 1
        if rule.endpoint in endpoint:
            checkFlag = 1

    if checkFlag == 1:
        app.url_map.pop(index);


@app.after_request
def apply_caching(response):
    # ....response.headers['Server'] = "Gray matrix service"
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Cache-Control";

    print('response in apply_caching is')

    print(response)
    # create_questions_spellchecker()

    return response

# print(dir(CreateUrl))
api.add_resource(CreateUrl, '/create')


@app.route("/")
def index():
    routes_info()
    return render_template('index.html')

@app.route("/updateKernel/bot/<bot>", methods=['GET', 'POST'])
def update(bot):
    try:
        question = request.values.get('question')
        answer = request.values.get('answer')
        topic_to_update = request.values.get('topic').upper()

        print("que: ", question)
        print("ans: ", answer)
        print("topic: ", topic_to_update)

        bot_helper_service.Topic_to_update(str(topic_to_update))

        obb = CreateUrl()
        obb.updateKernel(str(bot), question, answer, topic_to_update)

        return "Kernel Update of " + bot
    except:
        return "No Such Topic Exists in " + bot


# routes_info()
print(app.config)
app.run(host='0.0.0.0', threaded=True)
print("here")
routes_info()
