#!/usr/bin/python
# -*- coding: utf-8 -*-


from flask import Flask, request
from flask_restful import Resource, Api
import MYNewAiml as aiml
import re
from utility import input
from collections import Counter
import custom_difflib
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
from nltk.tag import pos_tag
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from mypattern.pattern.text.en.inflect import singularize
# from pattern.text.en import singularize
import sqlite3
import json
from nltk.stem.wordnet import WordNetLemmatizer
import time, threading
import ast
from ComplexQueries.ComplexQueries import ComplexQueries
from ComplexQueries.CompQ_NotFLow import CompQ_NotFlow
import nltk
import datefinder
import datetime
from nltk import pos_tag, word_tokenize
import requests
import simplejson as json

nltk.data.path.append('/mnt/newDisk/NLTKDAT')

class Topic_to_update:
    final_updated_topic = ''
    def __init__(self, topic_to_update):
        Topic_to_update.final_updated_topic = topic_to_update



class WebMessages(Resource):
    def __init__(
            self,
            data,
            aiml_path,
            std_startup,
            kernel,
            kernel2,
            words,
            words2,
            cross_flow
    ):

        self.file_path = data
        self.aiml_location = aiml_path
        self.std = std_startup
        self.kernel = kernel
        self.kernel2 = kernel2
        self.words = words
        self.words2 = words2
        self.cross_flow = cross_flow



    def getDetail(self):
        return self.file_path

    def loadKernel(self, command):
        loaction = self.aiml_location + '/' + self.std
        return myAiml(loaction, app_name=self.file_path).loadKernel(command)

    def loadKernel2(self, command):
        loaction = self.aiml_location + '/' + self.std
        return myAiml2(loaction).loadKernel(command)

    def setValue(
            self,
            key,
            value,
            kernel,
            kernel2
    ):

        print ("myAiml setbotpredicate", myAiml('').setBotPredicate(key, value, kernel))
        return myAiml(self).setBotPredicate(key, value, kernel)

    def getValue(self, key, kernel):
        return myAiml(self).getPredicate(key, kernel)

    def loadSpellCheck(self, path):
        loaction = self.aiml_location + '/spell_correcter.txt'
        spellWord = spellingCorrector(loaction)
        spellWord.redFiles(loaction)
        return spellWord.getWords()

    def get(self):
        location = self.aiml_location + '/' + self.std
        aiml_path = self.aiml_location
        kernel = self.kernel
        session_id = request.values.get('session')
        sentence = request.values.get('message')
        flow_name = request.values.get('flow_name')
        set_val = request.values.get('setval')
        try:
            flow_reset = int(request.values.get('flow_reset'))
        except:
            flow_reset = 100

        if set_val == "$$SetValues$$":
            SetReset(sentence, session_id, location, aiml_path, kernel, set_val, flow_name,flow_reset).SetValues()

        else:
            SetReset(sentence, session_id, location, aiml_path, kernel, set_val, flow_name,flow_reset).ResetValues()

    def post(self):
        print("################ NEW QUERY ##################")

        ## Path of the uploaded untar files on server
        loaction = self.aiml_location + '/' + self.std

        ## Path of spell correcter.txt (a helper file)
        loaction1 = self.aiml_location + '/spell_correcter.txt'

        ## Getting message (user's qur(y), session ID and timestamo from Tawheed's Node
        sentence = request.values.get('message')
        print("USER INPUT:      ", sentence)
        ## Encoding to ASCII in order to deal with smileys etc from facebook, etc.
        sentence = sentence.encode('ascii', sentence)
        ## If user's query is blank then, it returns this
        if not sentence:
            return {'success': 0,
                    'message': 'Please Provide me the conversation Message'}

        ## Getting Session ID fron Node.
        ## According to platforms used (fb, whatsapp, skype, talkk, etc)
        session_id = request.values.get('session')
        myAiml(loaction).setPredicate('SessionId', self.kernel, session_id, session_id)

        if not session_id:
            return {'success': 0,
                    'message': 'Please Provide me the Conversation Session ID'}

        ## Getting timestamp message
        timestamp = request.values.get('timestamp')
        if not timestamp:
            myAiml(loaction).setPredicate('timestamp', self.kernel,
                                          timestamp, session_id)
        ## Checking for the attachment URL if any from Facebook Messanger
        attachment_url = 'empty'
        try:
            attachment_url = re.search("(?P<url>https?://[^\s]+)", sentence).group("url")

        except:
            pass

        myAiml(loaction).setPredicate('attachment_url', self.kernel, attachment_url, session_id)
        ## Checking for the source of this message Facebook Messanger/Whatsapp
        source = 'empty'
        try:
            source = request.values.get('source')
            if source == None or source == '':
                source = 'empty'
            source = source.lower()
        except:
            pass

            ## Checking for the Location coordinates if any from Facebook Messanger
        try:
            lat = request.values.get('lat')
            _long = request.values.get('long')
            if lat == None or lat == '' or _long == None or _long == '':
                lat = 'empty'
                _long = 'empty'

        except:
            pass

        myAiml(loaction).setPredicate('lat', self.kernel, lat, session_id)
        myAiml(loaction).setPredicate('long', self.kernel, _long, session_id)

        print ("LOCATION:", myAiml(loaction).getPredicate('lat', self.kernel, session_id))
        myAiml(loaction).getPredicate('long', self.kernel, session_id)

        myAiml(loaction).setPredicate('source', self.kernel, source, session_id)
        ## In order to run the validations files which reside in 'validations' folder in tar.gz, we have to provide it's path as tar.gz will be uploaded to server
        ## 'BuildPath' is the variable in which the location of 'untar/../validations/' reside (in order to run from command line)
        myAiml(loaction).setPredicate('BuildPath', self.kernel,
                                      self.aiml_location, session_id)
        ## Setting this to user type query (without any processing)
        raw_sentence = sentence
        print ("BEFORE:")
        print (nltk.data.path)
        #self.lead_capture(raw_sentence, session_id)

        ## As inputting . (period) to AIML kernel may give / gives multiple outputs and ruins the flow.
        ## Hence converting . (period to '*$'
        raw_sentence = raw_sentence.decode('utf8')
        raw_sentence = raw_sentence.replace('.', '*$')

        ## initialising all delimiters used
        question_delim = '*#~que~*#'  # Bot asked question
        break_delim = '#~a*b~#'  # Multiple messages Break
        valid_delim = '$$valid$$'  # Bot replied a valid answer (need in critical flows where validations are required or API)
        invalid_delim = '$$invalid$$'  # Bot replied an invalid answer (need in critical flows where validations are required or API)
        restart_demil = '$$restart$$'  # Need to restart the critical flow (need in critical flows where validations are required or API)
        direct_delim = '#$direct$#'  # Sending the user inputted string directly to Bot without any preprocessing

        ###rake extraction_ NOT IN USEEEE#########

        ##RAKE

        ## Assuring that the recommendation variable is giving us results
        ## Can be ignore if you are at beginner level to this code

        ## For Question remembrance, this variable is most important
        ## Has to be first set in AIML in order to access it's functionality
        ## Topic Sensing Part Comes here
        ## Whenever the bot goes in topic, this variable is set to topic name
        check_instance = myAiml(self)

        check_instance.response(self.kernel, '', session_id)
        topic = check_instance.topic

        ## Making sure whether topic exists or not
        ## Outputs either True or False

        ## Prints Topic Name
        print ('Topic Name: ', topic)

        ## predicted_sentence is variable in which the Bot's final response is returned and sent back as reply to user
        predicted_sentence = ''

        ## Applying sentiment analysis
        ## Currently this module has been parked as it makes it unstable and solves only subset of user's negative queries
        polarity_negative_score = \
            self.positive_negative_sentiments(raw_sentence)

        preliminary_processing_result = self.preliminary_processing(sentence, loaction1)
        div_sentence = preliminary_processing_result['div_sentence']
        input_str = preliminary_processing_result['input_str']
        input_str = input_str.split(" ")
        input_str = sorted(input_str)
        input_str = " ".join(input_str)

        print ("PROCESSED input DIVSENTENCE:     ", (div_sentence))
        print ("PROCESSED input INPUT_STR:     ",(input_str))

        ## Sensing User's Compound queries (For example 'I want benefits and then calculate my premium')
        splitted_multiple_questions = re.split(
            r'\s(?=(?:and|nor|but|yet|so|;|consequently|further|however|indeed|therefore|nevertheless|then)\b)',
            div_sentence)



        ## Retrieving chat_log from AIML kernel in order to keep track of whether bot has asked question or not
        chat_log = myAiml(loaction).div_aiml_old_convertations(self.kernel, session_id)
        if chat_log != []:
            le1 = chat_log[-1]
        else:
            le1 = ''


        # Storing bot's recent reply (latest one) in le1


        try:
            sant_sentence = re.sub(r'[^A-Za-z0-9]+', ' ', sentence)
            complex_obj1 = ComplexQueries(sant_sentence, self.aiml_location)  ###, flow_name, comp)
            complex_result = complex_obj1.generic()
            flow_name = complex_result['flow']
            parameters = complex_result['param']
            print ("Complex TRY")
            print (flow_name)
            print (parameters)
            print ("end try")
        except:
            flow_name = 'notpresent'
            parameters = 'notpresent'
            print ("Complex Except")

        if flow_name != 'notpresent':
            myAiml(loaction).setPredicate('flow_name', self.kernel, flow_name, session_id)

        flow_aiml_name = myAiml(loaction).getPredicate('flow_name', self.kernel, session_id)
        print ("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN: ", flow_aiml_name)

        if ((flow_name) and ("notpresent" not in flow_name) and ("notpresent" not in parameters)):
            myAiml(loaction).response(self.kernel, flow_name, session_id)
            predicted_sentence = myAiml(loaction).response(self.kernel, parameters, session_id)
            pred_sent = self.proc(predicted_sentence)
            print ("BOT_ANSWER:  246    ", pred_sent)
            return {'success': 1, 'message': pred_sent,
                    'session': session_id}

        input_raw = raw_sentence
        input_raw = re.sub('[^A-Za-z0-9]+', ' ', input_raw)
        input_raw = input_raw.upper()
        rr = input_raw.split()
        op_cr = []
        for flow_cr in self.cross_flow:
            flow_cr = flow_cr.replace('.aiml', '')
            op_cr.append(flow_cr)
        res = list(set(rr) & set(op_cr))
        cmp_thres_cmpd = 0

        if (False):

            a = []
            for flow_name_cr in Cross_Flow_Memory.inputHist:
                flow_name_cr = flow_name_cr.replace('.aiml', '')
                a.append(flow_name_cr)

            input_raw = raw_sentence
            input_raw = re.sub('[^A-Za-z0-9]+', ' ', input_raw)

            res = " ".join(res)

            for item in a[::-1]:
                car = item.split("in")[1]
                car = car.strip()
                if res == car:
                    final_ress = item
                    break
            try:
                predicted_sentence = self.c_r_result(final_ress, session_id)
            except:
                pass

        elif (direct_delim in le1):
            direct_sentence = raw_sentence
            predicted_sentence = myAiml(loaction).response(self.kernel, direct_sentence, session_id)
        ## if found length of 'splitted_multiple_questions' > 1, then process the complex query by splitting in simple fragments of sentences

        ## Handling for negative user queries
        ## Currently parked
        # if polarity_negative_score > 100 and not topic and compound_status == 0 and direct_status == 0:
        #   predicted_sentence = self.negative_handling(div_sentence,
        #          loaction1, lines1)

        ## Now the actual answers finding for user query starts depending on,
        ##  1. Bot asked Question
        ##  2. Bot did not ask Question
        ##  3. Valid response from Bot
        ##  4. Invalid response from Bot
        ##  5. Handling critical flow resume, restart and cancel
        else:

            ## Bot asked question or not
            ## Question Sensing
            chat_log = myAiml(loaction).div_aiml_old_convertations(self.kernel, session_id)
            print (chat_log)
            if (question_delim in le1):

                bot_answer = Flow_Handling(self).question_flow(input_str, raw_sentence, topic, loaction,
                                                               question_delim, break_delim, valid_delim, invalid_delim,
                                                               restart_demil, direct_delim, flow_aiml_name, session_id)
                predicted_sentence = bot_answer

            else:

                bot_answer = Flow_Handling(self).regular_flow(input_str, raw_sentence, topic, loaction, session_id)
                predicted_sentence = bot_answer

        pred_sent = self.proc(predicted_sentence)

        self.writeLog(self.aiml_location + '/Chat_Logs/' + session_id + '.txt', raw_sentence, pred_sent);

        print ("BOT_ANSWER: ", pred_sent)
        print ("question_resume: ")




        return {'success': 1, 'message': pred_sent,
                'session': session_id}



        # small_talk_dictionary = self.small_talk_processing(raw_sentence)
        # print ('SMALL_TALK_DICT: ',small_talk_dictionary)
        # small_talk_input = small_talk_dictionary['small_talk']
        # small_talk_threshold = small_talk_dictionary['threshold']

        #  if (small_talk_status == 1):

        #            small_talk = myAiml2(location2).response(self.kernel2, small_talk_input, session_id)
        #           print ('OP small talk:L ',small_talk)
        #      elif (small_talk_threshold>85):
        #         small_talk = myAiml2(location2).response(self.kernel2, small_talk_input, session_id)
        #        print ('OP small talk:L ', small_talk)
        #   else:
        #      small_talk = ''

    def proc(self, predicted_sentence):

        question_delim = '*#~que~*#'  # Bot asked question
        break_delim = '#~a*b~#'  # Multiple messages Break
        valid_delim = '$$valid$$'  # Bot replied a valid answer (need in critical flows where validations are required or API)
        invalid_delim = '$$invalid$$'  # Bot replied an invalid answer (need in critical flows where validations are required or API)
        restart_demil = '$$restart$$'  # Need to restart the critical flow (need in critical flows where validations are required or API)
        direct_delim = '#$direct$#'  # Sending the user inputted string directly to Bot without any preprocessing
        resume_delim = "$$rresume$$"

        predicted_sentence = predicted_sentence.encode().decode('unicode-escape')
        predicted_sentence = predicted_sentence.replace('*$', '.')
        predicted_sentence = predicted_sentence.replace(question_delim, '').replace(direct_delim, '').replace(
            invalid_delim, '').replace(valid_delim, '').replace(restart_demil, '').replace(resume_delim, '').replace("$$resumestop$$",'').replace('$$cancel$$', '').replace("$$restart$$", '').replace("$$endflow$$", '')
        predicted_sentence1 = predicted_sentence.split(break_delim)
        p = []
        for eachP in predicted_sentence1:
            eachP = eachP.strip()  ## Re
            p.append(eachP)
        predicted_sentence1 = p
        n = len(predicted_sentence1)

        small_talk = ''
        predicted_sentence = []
        dict1 = {'message': small_talk}
        predicted_sentence.append(dict1)

        for i in range(0, n):
            bl2 = re.findall(r'<.*>', predicted_sentence1[i])
            plText = None
            xmlList = len(bl2)
            if (xmlList > 0):
                bl2 = ''.join(bl2)
                bl3 = ' '
                plText = input(bl2, bl3)
                plText = json.loads(plText)
            else:
                plText = predicted_sentence1[i]
            dict2 = {'message': plText}
            predicted_sentence.append(dict2)

        return predicted_sentence

    def c_r_result(self, raw_sentence, session_id):
        location = self.aiml_location

        ##topic extraction from raw_sentence
        cro_list = self.cross_flow
        rr = raw_sentence.split()
        cross_flow = []
        for each_flow in cro_list:
            each_flow = each_flow.replace('.aiml', '')
            cross_flow.append(each_flow)


        topic = list(set(rr) & set(cross_flow))
        inter = topic
        inter = " ".join(inter)

        topic = " ".join(topic)
        topic = "cross" + topic
        myAiml(location).response(self.kernel, topic, session_id)
        check_instance = myAiml(self)
        check_instance.response(self.kernel, '', session_id)
        topic = check_instance.topic
        print ("topic", topic)

        ###sending raw sentence to preliminary processing
        preliminary_processing_result = self.preliminary_processing(raw_sentence, location)
        div_sentence = preliminary_processing_result['div_sentence']
        input_str = preliminary_processing_result['input_str']

        ####sending input_str to mybestmatch
        input_str = input_str.replace(inter, '')
        result = self.my_bestmatch_threshold(input_str, topic, 1)

        div_sentence1 = result['bestmatch']
        threshold = result['threshold']
        predicted_sentence = myAiml(location).response(self.kernel, div_sentence1, session_id)

        return predicted_sentence

    def lead_capture(self, raw_sentence,session):

        print ("IN LEAD CAPTURE::")
        lmtzr = WordNetLemmatizer()
        # extract email
        raw_sentence = raw_sentence
        user_input = raw_sentence.lower().strip()
        match = re.search(r'[\w\.-]+@[\w\.-]+', user_input)
        if (match == None):
            email = "F"
        else:
            email = match.group(0)

        # age extraction
        try:
            matches = list(datefinder.find_dates(raw_sentence))
            # print ("matches- ",matches

            if len(matches) > 0:
                # date returned will be a datetime.datetime object. here we are only using the first match.
                birth_date = str(matches[0]).split()[0]
                # print  birth_date[0]


                # for match in matches:
                # birth_date = str(match)[0:11]
            birth_date = str(birth_date).replace('-', '')
            birth_date = (birth_date.replace('-', '').replace(' ', ''))
            birth_date = datetime.datetime.strptime(birth_date.replace('-', ''), "%Y%m%d").date()
            # print ("birth ",birth_date



            days_in_year = 365.2425
            age = int((datetime.date.today() - birth_date).days / days_in_year)

        except:
            age = "F"

        # name extraction
        for_email = raw_sentence.lower().strip()

        match = re.search(r'[\w\.-]+@[\w\.-]+', for_email)
        if (match == None):
            email = "F"
        else:
            email = match.group(0)

        if email != 'F':
            raw_sentence = raw_sentence.replace(email,'and')

        sentence = raw_sentence.title()
        tokens = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(tokens)
        tagged[0:6]
        entities = nltk.chunk.ne_chunk(tagged)
        # print entities
        docs = []
        stopwords = ['aisle', 'i', 'ok', 'find', 'thank', 'me', "'", ':', ',', '-', '_', '(', ')', '.', '"', ';', '?',
                     'hello', 'myself','smoker','non','female']

        for subtree in entities.subtrees(filter=lambda t: t.label() == 'PERSON'):
            o = " ".join([a for (a, b) in subtree.leaves()])
            # print ("ONLY OLD:",o
            if 'single' not in o and 'married ' not in o:
                if len([a for (a, b) in subtree.leaves()]) < 3:
                    l = []
                    product_name = ""
                    for w in word_tokenize(o):
                        # print ("OG", w
                        lem = lmtzr.lemmatize(w, 'v')
                        # print ("later", lem
                        l.append(lem)

                    after_lemma = pos_tag(l)

                    # print ("AFTER NEW:",after_lemma

                    nouns = []
                    for w, pos in after_lemma:
                        if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'):
                            nouns.append(w)
                            n = " ".join(nouns)

                        for word in stopwords:
                            if word.title() in nouns:
                                n = n.replace(word.title(), "")

                    # n=n.split()

                    # print n

                    if nouns == []:
                        print ("F")
                    else:
                        product_name = n
                        docs.append(product_name.strip())

        if "".join(docs) == '':
            name = "F"
        else:
            name = "".join(docs)

        # extract contact number

        try:
            input_string = raw_sentence.split()
            for x in input_string:
                # print (x)
                m1 = re.findall('^(?<!\d)(?:\+91|91|091)?\W*(?P<mobile>[789]{1}\d{9})(?!\d)$', x)
                # print m1
                if (len(m1) == 1):
                    user_input = "".join(m1[0])
                    # print user_input
                    contact = user_input
                    # print contact ,"mobile"
                    if contact:
                        break
                else:
                    contact = "F"
        except:
            contact = "F"

        # marital status
        user_input = raw_sentence.lower()
        if 'single' in user_input or ('not ' in user_input and 'married' in user_input):
            status = "S"
        elif 'married' in user_input or ('not ' in user_input and 'single' in user_input) or 'wife' in user_input or 'husband' in user_input:
            status = "M"
        else:
            status = "F"

        #Gender
        gender = raw_sentence.lower()

        if ("female" in gender or "girl" in gender or "baby" in gender ):
            gen = "female"
        elif ("male" in gender or "man" in gender or "boy" in gender):
            gen = "male"
        else:
            gen = "F"
        #SmokerNonsnoker
        smok_str = raw_sentence.lower()
        smok_str = smok_str.lower()
        if ("nonsmoker" in smok_str or ('not' in smok_str and 'smoke' in smok_str)):
            smk = "N"
        elif ("smoker" in smok_str or "smokey" in smok_str or 'smoke' in smok_str):
            smk = "Y"
        else:
            smk = "F"

        # print ("name:",name,"\t","age:",age,"\t","mobile_no:",contact,"\t","email:",email,"\t","marital:",status


        # a =[name,age,contact,email,status]
        # print a


        d = {'name': name, 'age': age, 'mobile': contact, 'email': email, 'gender': gen, 'is_smoker': smk}
        #d = {'name': name, 'age': age, 'mobile': contact, 'email': email, 'status': status}
        _param = {"session_id": session}
        param_count=0
        for key, value in d.items():
            if value != "F":
                _param[key] = value
                param_count += 1

        # print  _param,"param"






        # x = [x for x in a if x != "F"]
        # print x

        param = {"data": {"_action": "captureLead", "_param": _param

        }}

        print (param,param_count, "PARAM:")

        '''
        param = {
            "data" : {
                "_action" : "captureLead",
                "_param"  : { 
                    "session_id": session,
                    "name"      : name,
                    "mobile"    : contact,
                    "email"     : email ,
                    "mood"      : mood  
                }
            }
        }

        '''
        if param_count>0:
            try:

                headers = {'content-type': 'application/json'}
                response = requests.post("http://45.64.194.62:5523/v1/sbi", data=json.dumps(param), headers=headers,
                                         verify=False);
                # print response
                myresponse = (response.content)
                print ("my response", myresponse)
                url = json.loads(myresponse)
                # print url
                mydata = url.get('success')
                if mydata == 1:
                    print ("url:", url)
                else:
                    print ("url:", url)

            except:
                print ("Error in API CALL:")



    def writeLog(self, path, raw_sentence, predicted_str):

        predicted_str = str(predicted_str)
        conversation_files = open(path, 'a')
        conversation_files.write('User Input: ' + raw_sentence + '\n' +
                                 'Chatbot Reply: ' + predicted_str + '\n\n\n')
        conversation_files.close();

    def preliminary_processing(self, sentence, loaction1):
        div_sentence = self.get_uip(sentence)
        div_sentence = div_sentence.lower()
        div_sentence = \
            spellingCorrector(loaction1).iterate_spell(div_sentence,
                                                       self.words)
        temp_list = []
        lmtzr = WordNetLemmatizer()

        input_str = \
            self.semantic_restructure(div_sentence.lower())
        if input_str:
            input_str = input_str
        else:
            input_str = div_sentence
        input_str = input_str.split()
        for q in input_str:
            temp_list.append(lmtzr.lemmatize(q))
        input_str = sorted(temp_list)
        input_str = ' '.join(input_str)
        input_str = self.remove_single_letters(input_str)
        input_str = input_str.upper()
        preliminary_processing_result = {"div_sentence": div_sentence,
                                         "input_str": input_str}
        return preliminary_processing_result

    def preliminary_processing2(self, sentence, loaction1):
        div_sentence = self.get_uip(sentence)
        div_sentence = div_sentence.lower()
        div_sentence = \
            spellingCorrector(loaction1).iterate_spell(div_sentence,
                                                       self.words)
        temp_list = []
        lmtzr = WordNetLemmatizer()

        input_str = \
            self.semantic_restructure2(div_sentence.lower())
        input_str = input_str.split()
        for q in input_str:
            temp_list.append(lmtzr.lemmatize(q))
        input_str = sorted(temp_list)
        input_str = ' '.join(input_str)
        input_str = self.remove_single_letters(input_str)
        input_str = input_str.upper()

        preliminary_processing_result = {"div_sentence": div_sentence,
                                         "input_str": input_str}

        return preliminary_processing_result

    ## Removes all special characters, symbols and punctuations
    def get_uip(self, sentence):
        sentence = sentence.decode('utf-8')
        sentence = sentence.replace('?', '')
        sentence = sentence.replace('', '')
        sentence = sentence.replace(':', '')
        sentence = sentence.replace(',', '')
        sentence = sentence.replace('-', '')
        sentence = sentence.replace('_', '')
        sentence = sentence.replace('(', '')
        sentence = sentence.replace(')', '')
        sentence = sentence.replace('.', '*$')
        sentence = sentence.replace(';', '')
        userinput2 = sentence
        return userinput2

    ## Removing unnecessary words (Optional and may differ from Bot to Bot
    def remove_single_letters(self, sentence):
        try:

            location_remove_words = self.aiml_location + '/Remove_Words/remove_words2.txt'

            stop = set(open(location_remove_words).read().split())
            sent = [i for i in sentence.lower().split() if i not in stop]
            sent = ' '.join(sent)
            sent_to_compare = sent.split(" ")

            if (len(sent_to_compare) == 0):
                location_remove_words = self.aiml_location + '/Remove_Words/remove_words.txt'
                stop = set(open(location_remove_words).read().split())
                sent = [i for i in sentence.lower().split() if i not in stop]
                sent = ' '.join(sent)

        except:
            location_remove_words = self.aiml_location + '/remove_words.txt'
            stop = set(open(location_remove_words).read().split())
            sent = [i for i in sentence.lower().split() if i not in stop]
            sent = ' '.join(sent)

        return sent

    ## Helper for dealing with complex sentences
    def questions_replace(self, each_question):
        each_question = str(each_question)
        each_question.replace('and', '');
        each_question.replace('nor', '');
        each_question.replace('but', '');
        each_question.replace('or', '');
        each_question.replace('yet', '');
        each_question.replace('so', '');
        each_question.replace(';', '');
        each_question.replace('consequently', '');
        each_question.replace('further', '');
        each_question.replace('however', '');
        each_question.replace('indeed', '');
        each_question.replace('therefore', '');
        each_question.replace('nevertheless', '');
        each_question.replace('then', '');
        return each_question

    def compound_sentences_results(self, splitted_multiple_questions, topic, loaction, break_delim, session_id):

        multiple_answers = []
        for each_question in splitted_multiple_questions:
            thresh_res = []
            input_str = self.questions_replace(each_question)
            input_str = self.semantic_restructure(str(input_str).lower())
            input_str = input_str.split()
            input_str = sorted(input_str)
            input_str = ' '.join(input_str)
            input_str = self.remove_single_letters(input_str)
            input_str = input_str.upper()

            # INPUTS: input_str , lines1
            ###################################################################################################
            result = self.my_bestmatch_threshold(input_str, topic)
            result = result['bestmatch']
            thresholdd = result['threshold']
            thresh_res.append(thresholdd)

            predicted_sentence_intermediate = myAiml(loaction).response(self.kernel, result, session_id)

            predicted_sentence = predicted_sentence_intermediate + break_delim
            multiple_answers.append(predicted_sentence)

        final_answers = []
        for i in multiple_answers:
            if i not in final_answers:
                final_answers.append(i)
        predicted_sentence = ' '.join(final_answers)

        return predicted_sentence

    def threshold_init(self, input_str, topic):

        ## ##

        ## ##

        result = self.my_bestmatch_threshold(input_str, topic)
        div_sentence1 = result['bestmatch']
        threshold = result['threshold']

        threshold_init_answer = {"div_sentence1": div_sentence1,
                                 "threshold": threshold}

        return threshold_init_answer



    def semantic_restructure(self, text):
        ts = pos_tag(text.split())
        vb = [word for (word, pos) in ts if pos == 'VB']
        vb = ' '.join(vb)
        vbd = [word for (word, pos) in ts if pos == 'VBD']
        vbd = ' '.join(vbd)
        vbg = [word for (word, pos) in ts if pos == 'VBG']
        vbg = ' '.join(vbg)
        vbn = [word for (word, pos) in ts if pos == 'VBN']
        vbn = ' '.join(vbn)
        vbp = [word for (word, pos) in ts if pos == 'VBP']
        vbp = ' '.join(vbp)
        jj = [word for (word, pos) in ts if pos == 'JJ']
        jj = ' '.join(jj)
        jjr = [word for (word, pos) in ts if pos == 'JJR']
        jjr = ' '.join(jjr)
        jjs = [word for (word, pos) in ts if pos == 'JJS']
        jjs = ' '.join(jjs)
        vbz = [word for (word, pos) in ts if pos == 'VBZ']
        vbz = ' '.join(vbz)
        nns = [word for (word, pos) in ts if pos == 'NNS']
        nns = ' '.join(nns)
        nnp = [word for (word, pos) in ts if pos == 'NNP']
        nnp = ' '.join(nnp)
        nnps = [word for (word, pos) in ts if pos == 'NNPS']
        nnps = ' '.join(nnps)
        nn = [word for (word, pos) in ts if pos == 'NN']
        nn = ' '.join(nn)
        cd = [word for (word, pos) in ts if pos == 'CD']
        cd = ' '.join(cd)
        rb = [word for (word, pos) in ts if pos == 'RB']
        rb = ' '.join(rb)
        wdt = [word for (word, pos) in ts if pos == 'WDT']
        wdt = ' '.join(wdt)
        wp = [word for (word, pos) in ts if pos == 'WP']
        wp = ' '.join(wp)
        wrb = [word for (word, pos) in ts if pos == 'WRB']
        wrb = ' '.join(wrb)

        div_input = vb + ' ' + vbd + ' ' + vbg + ' ' + vbn + ' ' + vbp \
                    + ' ' + vbz + ' ' + jj + ' ' + jjr + ' ' + jjs + ' ' + nns + ' ' + nnp + ' ' + nnps + ' ' + nn \
                    + ' ' + cd + ' ' + rb + ' ' + wdt + ' ' + wp + ' ' + wrb
        div_input = ' '.join(div_input.split())
        div_input = div_input.split(" ")
        temp_inp = []

        for i in div_input:
            if i not in temp_inp:
                temp_inp.append(i)

        div_input = " ".join(temp_inp)
        return div_input

    def semantic_restructure2(self, text):
        ts = pos_tag(text.split())
        cd = [word for (word, pos) in ts if pos == 'CD']
        cd = ' '.join(cd)
        rb = [word for (word, pos) in ts if pos == 'RB']
        rb = ' '.join(rb)
        wdt = [word for (word, pos) in ts if pos == 'WDT']
        wdt = ' '.join(wdt)
        wp = [word for (word, pos) in ts if pos == 'WP']
        wp = ' '.join(wp)
        wrb = [word for (word, pos) in ts if pos == 'WRB']
        wrb = ' '.join(wrb)
        div_input = cd + ' ' + rb + ' ' + wdt + ' ' + wp + ' ' + wrb
        div_input = ' '.join(div_input.split())
        div_input = div_input.split(" ")
        temp_inp = []

        for i in div_input:
            if i not in temp_inp:
                temp_inp.append(i)

        div_input = " ".join(temp_inp)
        return div_input

    def negative_handling(
            self,
            sentence,
            loaction1,
            lines1,
    ):
        div_sentence = sentence
        predicted_sentence = 'NEGATIVE HAI'
        div_sentence = \
            spellingCorrector(loaction1).iterate_spell(div_sentence,
                                                       self.words)
        input_str = self.semantic_restructure(div_sentence.lower())
        input_str = self.remove_single_letters(input_str)
        input_str = input_str.upper()
        div_sentence1 = sorted(lines1, key=lambda x: \
            custom_difflib.SequenceMatcher(None, x,
                                        input_str).ratio(), reverse=True)
        div_sentence1 = div_sentence1[0]

        seq = custom_difflib.SequenceMatcher(None, input_str,
                                          div_sentence1)
        threshold = seq.ratio() * 100

        if threshold > 75:
            div_Mysent = div_sentence1

            loaction = self.aiml_location
            dirs = os.listdir(loaction)
            all_files_list = []
            for file in dirs:
                all_files_list.append(file)

            div_Mysent = div_Mysent.replace('\n', '')
            res = [k for k in all_files_list if '.aiml' in k]
            opres = []
            for i in range(0, len(res)):

                if div_Mysent in open(loaction + '/' + res[i]).read():
                    opres.append(res[i])
                else:
                    print ('false')

            input_div = '<topic name = '
            save_lines = []
            final_match = []
            for i in range(0, len(opres)):
                with open(loaction + '/' + opres[i]) as f:
                    save_lines.append(f.readlines())
                    s1 = save_lines[i]
                    div1 = sorted(s1[1:6], key=lambda x: \
                        custom_difflib.SequenceMatcher(None, x,
                                                    input_div).ratio(), reverse=True)

                    seq = custom_difflib.SequenceMatcher(None, input_div,
                                                      div1[0])
                    threshold_neg = seq.ratio() * 100

                    if threshold_neg > 45:
                        final_match.append(div1[0])

            pr1 = 'Do you mean..'
            pr1 = 'I can provide you '
            pr2 = []
            for i in range(0, len(final_match)):
                tostr = ''.join(final_match[i])
                str_my = '%s of %s' % (div_Mysent, tostr)
                pr2.append(str_my)

            most_final = []
            for i in range(0, len(pr2)):
                temp_str = ''.join(pr2[i])
                temp_str = temp_str.replace('<topic name = ', '')
                temp_str = temp_str.replace('>', '')
                most_final.append(temp_str)

            predicted_sentence = pr1 + ''.join(most_final)

        return predicted_sentence


    def positive_negative_sentiments(self, input_str):
        analyzer = SentimentIntensityAnalyzer()
        vs = analyzer.polarity_scores(input_str)
        return vs.get('neg')

    def chunkIt(self, seq, num):
        avg = len(seq) / float(num)
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg

        return out

    def find_my_best_matches(self, sent11, query):

        div_sentence1 = sorted(sent11, key=lambda x: custom_difflib.SequenceMatcher(None, x, query).ratio(),
                               reverse=True)
        res = process.extractOne(query, sent11)

        output = {'difflib': div_sentence1[0], 'fuzzy': res[0]}
        return output

    result_list = []



    def small_talk_bestmatch(self, query, small_talk_db):
        query = query.upper()
        matches = small_talk_db
        print ('COUNT SMALL TALK: ', len(matches))
        matches2 = []
        for i in matches:
            if i not in matches2:
                matches2.append(i)
        matches = matches2
        print (len(matches))

        div_sentence1 = sorted(matches, key=lambda x: custom_difflib.SequenceMatcher(None, x, query).ratio(),
                               reverse=True)

        res = process.extractOne(query, matches)
        div_sentence1 = div_sentence1[0]
        res = list(res)[0]

        string1 = query.split(' ')
        string2 = div_sentence1.split(' ')
        string3 = res.split(' ')

        string1 = [singularize(plural) for plural in string1]
        string2 = [singularize(plural) for plural in string2]
        string3 = [singularize(plural) for plural in string3]

        print ('###################### Small Talk ###############################')
        print (string1)
        print (string2)
        print (string3)
        print ('###################### Small Talk ###############################')

        inter1 = set(string1) & set(string2)
        inter2 = set(string1) & set(string3)
        len1 = len(inter1)
        len2 = len(inter2)
        print (len1)
        print (len2)

        if (len1 > len2):
            div_sentence1 = div_sentence1
            seq = custom_difflib.SequenceMatcher(None, query, div_sentence1)
            threshold = seq.ratio() * 100
            threshold = fuzz.partial_ratio(query, div_sentence1)
            print ('IF Thresh small talk: ', threshold)
            print ('IF Small talk', div_sentence1)
        else:
            div_sentence1 = res
            threshold = fuzz.partial_ratio(query, div_sentence1)
            print ('ELSE thresh small talk: ', threshold)
            print ('ELSE small talk', res)

        print ('HENCE FINAL DIV SENT small talk: ', div_sentence1)

        result = {'bestmatch': div_sentence1, 'threshold': threshold}

        return result

    def driving_func(self, matched_pattern, loaction, session_id, topic=None):
        location_recommendation_db = self.aiml_location + '/recommendation.txt'

        f_small = open(location_recommendation_db, 'r')
        recommendation_db = f_small.read()
        recommendation_db = ast.literal_eval(recommendation_db)
        new_choices = self.find_my_best_matches(recommendation_db.keys(), matched_pattern)

        new_choices_fuzzy = []
        new_choices_difflib = []

        new_choices_difflib.append(new_choices['difflib'])
        new_choices_fuzzy.append(new_choices['fuzzy'])

        new_choices_fuzzy = ' '.join(new_choices_fuzzy)
        new_choices_difflib = ' '.join(new_choices_difflib)

        string1 = matched_pattern.split(' ')
        string2 = new_choices_difflib.split(' ')
        string3 = new_choices_fuzzy.split(' ')

        inter1 = set(string1) & set(string2)
        inter2 = set(string1) & set(string3)
        len1 = len(inter1)
        len2 = len(inter2)

        if (len1 > len2):
            div_sentence1 = new_choices_difflib
            threshold = fuzz.partial_ratio(matched_pattern, div_sentence1)

        else:
            div_sentence1 = new_choices_fuzzy
            threshold = fuzz.partial_ratio(matched_pattern, div_sentence1)

        if threshold == 100:
            driving_question = recommendation_db[div_sentence1]
            result = self.my_bestmatch_threshold(driving_question, topic)
            driving_question_best = result['bestmatch']
            secretrecom = myAiml(loaction).response(self.kernel,
                                                    driving_question_best, session_id)
            myAiml(loaction).setPredicate('secretrecom', self.kernel,
                                          secretrecom, session_id)

            return driving_question
        else:
            return None

    ## The Bot's recommendation engine
    def recommendation_engine(self, result_driving_question, predicted_sentence, break_delim, loaction, session_id):
        try:
            if result_driving_question != None:
                full_question = 'Shall I tell you about ' + result_driving_question + '?'
                predicted_sentence = predicted_sentence + break_delim + '<template><type>Card</type><elements><subtitle>' + full_question + '</subtitle><default_action><type>postback</type><payload>Yes</payload></default_action><buttons><type>postback</type><payload>Yes</payload><title>Yes</title></buttons><buttons><type>postback</type><payload>No</payload><title>No</title></buttons></elements></template>'

            if result_driving_question != None:
                my_secret_recommendation = 'SECRETRECOMMENDATIONHDFC'
                recom = myAiml(loaction).response(self.kernel,
                                                  my_secret_recommendation, session_id)

        except:
            predicted_sentence = predicted_sentence

        return predicted_sentence


class Flow_Handling(WebMessages):
    def __init__(self, webmessages):
        self.aiml_location = webmessages.aiml_location
        self.kernel = webmessages.kernel
        self.cross_flow = webmessages.cross_flow

        self.question_delim = '*#~que~*#'  # Bot asked question
        self.break_delim = '#~a*b~#'  # Multiple messages Break
        self.valid_delim = '$$valid$$'  # Bot replied a valid answer (need in critical flows where validations are required or API)
        self.invalid_delim = '$$invalid$$'  # Bot replied an invalid answer (need in critical flows where validations are required or API)
        self.restart_demil = '$$restart$$'  # Need to restart the critical flow (need in critical flows where validations are required or API)
        self.direct_delim = '#$direct$#'  # Sending the user inputted string directly to Bot without any preprocessing

    def regular_flow(self, input_str, raw_sentence, topic=None, loaction=None, session_id=None):

        if topic:
            print ("I AM IN REGULAR FLOW IN TOPIC")
            input_str = str(input_str).split()
            inp_str = []
            for i in input_str:
                if i not in inp_str:
                    inp_str.append(i)

            inp_str = ' '.join(inp_str)

            result = self.my_bestmatch_threshold(inp_str, topic)
            div_sentence1 = result['bestmatch']
            threshold = result['threshold']

            try:
                location_recommendation_db = self.aiml_location + '/recommendation.txt'

                f_small = open(location_recommendation_db, 'r')

                result_driving_question = self.driving_func(div_sentence1, loaction, session_id, topic)

            except:
                result_driving_question = None

            if threshold > 75:
                predicted_sentence = \
                    myAiml(loaction).response(self.kernel,
                                              div_sentence1, session_id)
                predicted_sentence = self.recommendation_engine(result_driving_question, predicted_sentence,
                                                                "#~a*b~#", loaction,
                                                                session_id)

            else:
                print ("RAW SENTTTTTTTTTTTTTT IN: ",raw_sentence)
                predicted_sentence =  myAiml(loaction).response(self.kernel,
                                              raw_sentence, session_id)
                '''
                # if isinstance(topic, topic_list):

                cro_flo_result = self.return_topic_names(inp_str, topic, self.cross_flow)

                topic = str(topic)
                topic = topic + ".aiml"

                print ("CRO_FLO_RESULT:      ", cro_flo_result)
                if topic == cro_flo_result:
                    predicted_sentence = \
                        myAiml(loaction).response(self.kernel,
                                                  raw_sentence, session_id)

                else:

                    cro_flo_result = cro_flo_result.split()

                    x = '<template><type>Card</type><elements><subtitle>I found your query in : </subtitle><default_action><type>postback</type><payload>m</payload></default_action>'
                    for i in cro_flo_result:
                        x = x + '<buttons><type>postback</type><payload>' + i + '</payload><title>' + i + '</title></buttons>'

                    x += '</elements></template>'
                    x = x.replace(".aiml", '')
                    predicted_sentence = x

                    obj_cr = Cross_Flow_Memory()

                    crr = []
                    for each_cro in cro_flo_result:
                        each_cro = each_cro.replace('.aiml', '')
                        crr.append(each_cro)

                    for each_cr in crr:
                        obj_cr.AddMe(raw_sentence + " in " + each_cr)'''



            bot_answer = predicted_sentence
            print ("IN TOPIC BOT_ANSWER :    1111    ", bot_answer)


        else:
            print ("I AM IN REGULAR FLOW NOT IN TOPIC")
            input_str = str(input_str).split()
            inp_str = []
            for i in input_str:
                if i not in inp_str:
                    inp_str.append(i)

            inp_str = ' '.join(inp_str)

            result = self.my_bestmatch_threshold(inp_str, topic)
            div_sentence1 = result['bestmatch']
            threshold = result['threshold']

            try:
                location_recommendation_db = self.aiml_location + '/recommendation.txt'
                f_small = open(location_recommendation_db, 'r')
                result_driving_question = self.driving_func(div_sentence1, loaction, session_id, topic)

            except:
                result_driving_question = None

            if threshold > 75:
                predicted_sentence = \
                    myAiml(loaction).response(self.kernel,
                                              div_sentence1, session_id)

            else:

                predicted_sentence = \
                    myAiml(loaction).response(self.kernel,
                                              raw_sentence, session_id)

            bot_answer = predicted_sentence
            print ("NOT IN TOPIC BOT_ANSWER:  1148   ", bot_answer)

        return bot_answer

    # def cross_topic(self,query,topic):
    def return_topic_names(self, query, topic, cross_flow):
        location = self.aiml_location
        query = query.upper()

        conn = sqlite3.connect(location + '/div_ChatBot_database.db')

        # remove current topic from topic_list
        # for ()

        # topic = list(topic)
        topic = str(topic)
        topic = topic.strip()
        topic = topic + ".aiml"

        # if topic in cross_flow:
        #   top_l=[]            #top_l = list(set(cross_flow) - set(topic))
        # cross_flow.remove(topic)
        print ("CURRENT TOPIC:       ",topic)
        topic1 = []
        for i in range(0, len(cross_flow)):
            print( 'CHANGED TOPIC NAME IS:       ', cross_flow[i])
            cr_flow = str(cross_flow[i])
            cr_flow = cr_flow.replace(".aiml", "")
            result = self.my_bestmatch_threshold(query, cr_flow, topic_status_direct=1)
            rut_sentence = result['bestmatch']
            threshold = result['threshold']

            if threshold > 75:
                topic1.append(cross_flow[i])

        topic1 = " ".join(topic1)
        if not topic1:
            topic1 = topic
            print ("CURRENT TOPIC AFTER CROSS_FLOW:      ", topic1)

        return topic1

    def question_flow(self, input_str, raw_sentence, topic, loaction, question_delim, break_delim,
                      valid_delim, invalid_delim, restart_demil, direct_delim, flow_aiml_name, session_id):
        print ("line    1312")
        if topic:

            print ("I AM IN QUESTION FLOW IN TOPIC")
            raw_z = re.sub(r'[^A-Za-z0-9@_*$]+', ' ', raw_sentence)
            punctuation = "\"`~!@#$%^&*()-_=+[{]}\|;:',<.>/?"
            puncStripRE = re.compile("[" + re.escape(punctuation) + "]")
            my_new_raw = re.sub(puncStripRE, " ", raw_sentence)
            my_new_raw = my_new_raw.strip()
            len_raw = len(my_new_raw)
            conn = sqlite3.connect(self.aiml_location + '/div_ChatBot_database.db')

            topic_db = []
            topyc_cur = conn.execute('SELECT * from %s' % (topic))
            for row in topyc_cur:
                topic_db.append(str(row[0]).lower().replace(' ',''))

            general_db = []
            generalqna_cur = conn.execute('SELECT * from general_qna')
            for row in generalqna_cur:
                general_db.append(str(row[0]).lower().replace(' ',''))


            conn.close()

            if (str(raw_sentence).lower().strip() in topic_db or str(raw_sentence).lower().strip() in general_db):
                print ("FOUND")
                raw_sentence1 = raw_sentence+"aa"
            else:
                print ("NOT FOUND")
                raw_sentence1 = raw_sentence

            predicted_sentence_new_response = myAiml(loaction).response(self.kernel, raw_sentence1,
                                                                        session_id)

            print(("ORIGINAL: ", predicted_sentence_new_response))
            print ("line    1347")

            original = predicted_sentence_new_response



            if (len_raw == 0):
                question_forgiveness_status = 1
            else:
                question_forgiveness_status = 0

            if ((invalid_delim not in predicted_sentence_new_response) and (
                        valid_delim in predicted_sentence_new_response)):

                if ("$$endflow$$" in predicted_sentence_new_response):
                    predicted_sentence = predicted_sentence_new_response
                else:

                    print ("SET RESET: ", SetReset.my_set_variables)
                    try:
                        S_R1 = (SetReset.my_set_variables)
                        S_R1 = S_R1.values()
                    except:
                        S_R1 = []

                    lsr1 = []
                    lsr2 = []

                    for each_value in S_R1:
                        each_value = each_value.replace('F', '').replace(' ','')
                        lsr1.append(each_value)
                    for each_value in lsr1:
                        if each_value:
                            lsr2.append(each_value)

                    set1 = len(lsr2)
                    print ("SET RESET LENGTH 1: ", set1)


                    try:
                        print ("IN TRY")
                        fileopen = open(self.aiml_location + "/Flow_Database/RSET/Rset.txt", "r")
                    except:
                        print ("IN EXCEPT")
                        fileopen = ''

                    if fileopen:
                        if flow_aiml_name:
                            print ("IN FLOW_AIML_NAME")
                            print ("FLOW NAME PRESENT: ", flow_aiml_name)
                            dictionary_db_flow = fileopen.read()
                            dictionary_db_flow = ast.literal_eval(dictionary_db_flow)
                            fileopen.close()
                            dd = (dictionary_db_flow[flow_aiml_name])
                            ss = sorted(dd.keys())
                            param_list = []
                            for each_key in ss:
                                param_list.append(myAiml(loaction).getPredicate(each_key, self.kernel, session_id))

                            compq_obj = CompQ_NotFlow(param_list, flow_aiml_name, raw_z, self.aiml_location)
                            res_compq = compq_obj.generic_nflo()

                            Complex_Flow = res_compq['Complex_Flow']
                            parameters = Complex_Flow['param']
                            intimation = res_compq['intimation_complex']

                            print ("$$$$$")
                            print (Complex_Flow)
                            print (parameters)
                            print (intimation)
                            print ("$$$$$")

                            print ("SENDINGGGGG: ", parameters)
                            myAiml(loaction).response(self.kernel, flow_aiml_name, session_id)
                            parameters = parameters.replace('.', '*$')
                            predicted_sentence_inter = myAiml(loaction).response(self.kernel, parameters, session_id)
                            print ("FINAL SET RESET: ", SetReset.my_set_variables)
                            S_R2 = (SetReset.my_set_variables)
                            S_R2 = S_R2.values()
                            lsr3 = []
                            lsr4 = []

                            for each_value in S_R2:
                                each_value = each_value.replace('F', '').replace(' ','')
                                lsr3.append(each_value)
                            for each_value in lsr3:
                                if each_value:
                                    lsr4.append(each_value)

                            set2 = len(lsr4)
                            print ("SET RESET LENGTH 2: ", set2)

                            if set2 > set1:
                                myAiml(loaction).response(self.kernel, flow_aiml_name, session_id)
                                parameters = parameters.replace('.', '*$')
                                predicted_sentence = myAiml(loaction).response(self.kernel, parameters, session_id)
                                print ("my kernel: ", predicted_sentence)
                            else:
                                predicted_sentence = predicted_sentence_new_response
                        else:
                            print ("ELSE of FLOWAIML")
                            predicted_sentence = predicted_sentence_new_response

                    else:
                        print ("ELSE of FILENOTOPEN")
                        predicted_sentence = predicted_sentence_new_response









            elif (question_forgiveness_status == 1):
                predicted_sentence = predicted_sentence_new_response
                print ("line 1445:   ", predicted_sentence)



            else:
                print ("ELSEEEE")

                result = self.my_bestmatch_threshold(input_str, topic)
                div_sentence1 = result['bestmatch']
                threshold = result['threshold']

                if (threshold > 75):
                    print (">75")
                    predicted_sentence = \
                        myAiml(loaction).response(self.kernel,
                                                  div_sentence1, session_id)

                    print ("ORIGINAL 2:      ",predicted_sentence)

                    predicted_sentence_DIV_test = \
                        myAiml(loaction).response(self.kernel,
                                                  div_sentence1, session_id)
                    print ("ORIGINAL 3:      ", predicted_sentence_DIV_test)

                    flow_restart = "RESTARTCALCULATION"+str(flow_aiml_name).upper()

                    if ("$$cancel$$" in predicted_sentence):
                        predicted_sentence_restart = ''


                    else:
                        print (topic, "TTOOPPIICC")
                        if topic == str(flow_aiml_name).upper():
                            predicted_sentence_restart = myAiml(loaction).response(self.kernel,
                                                      flow_restart, session_id)
                            print ("FLOW RESTART;    ", flow_restart)
                            print ("ORIGINAL 4:      ", predicted_sentence_restart)
                        else:
                            predicted_sentence_restart = ""
                        print ("\n\n")
                        print ("OG 5:        ",predicted_sentence)
                        print ("\n\n")


                    chat_log = myAiml(loaction).div_aiml_old_convertations(self.kernel, session_id)
                    if chat_log != []:
                        le1 = chat_log[-1]
                    else:
                        le1 = ''

                    myAiml(loaction).setPredicate('question_resume', self.kernel,
                                                       le1+ ' '+'$$resumestop$$' , session_id)

                    print ("PPPPPP: ", le1)

                    if ("$$resumestop$$" in predicted_sentence or "$$cancel$$" in predicted_sentence or "$$restart$$" in predicted_sentence):
                        print ("CANCELLING")
                        predicted_sentence = predicted_sentence
                    else:
                        predicted_sentence = predicted_sentence + break_delim + predicted_sentence_restart




                else:
                    print ("<75")
                    try:
                        print ("IN TRY")
                        fileopen = open(self.aiml_location + "/Flow_Database/RSET/Rset.txt", "r")
                    except:
                        print ("IN EXCEPT")
                        fileopen = ''

                    if fileopen:
                        if flow_aiml_name:
                            print ("IN FLOW_AIML_NAME")
                            print ("FLOW NAME PRESENT: ", flow_aiml_name)
                            dictionary_db_flow = fileopen.read()
                            dictionary_db_flow = ast.literal_eval(dictionary_db_flow)
                            fileopen.close()
                            dd = (dictionary_db_flow[flow_aiml_name])
                            ss = sorted(dd.keys())
                            param_list = []
                            for each_key in ss:
                                param_list.append(myAiml(loaction).getPredicate(each_key, self.kernel, session_id))

                            compq_obj = CompQ_NotFlow(param_list, flow_aiml_name, raw_z, self.aiml_location)
                            res_compq = compq_obj.generic_nflo()

                            Complex_Flow = res_compq['Complex_Flow']
                            parameters = Complex_Flow['param']
                            intimation = res_compq['intimation_complex']

                            print ("$$$$$")
                            print (Complex_Flow)
                            print (parameters)
                            print (intimation)
                            print ("$$$$$")

                            if (intimation == 'MY KERNEL'):
                                print ("MY KERNEL SECOND COMPLEX")
                                print ("sendig: ", parameters)
                                myAiml(loaction).response(self.kernel, flow_aiml_name, session_id)
                                parameters = parameters.replace('.','*$')
                                predicted_sentence = myAiml(loaction).response(self.kernel, parameters, session_id)

                                print ("my kernel: ", predicted_sentence)

                            elif (intimation == "MOVE AHEAD"):
                                print ("MOVE AHEAD")
                                predicted_sentence = predicted_sentence_new_response
                                print ("move ahead: ", predicted_sentence)
                            else:
                                predicted_sentence = predicted_sentence_new_response
                                print ("else move ahead: ", predicted_sentence)
                        else:
                            print ("ELSE of FLOWAIML")
                            predicted_sentence = predicted_sentence_new_response

                    else:
                        print ("ELSE of FILENOTOPEN")
                        predicted_sentence = predicted_sentence_new_response







        else:
            print ("I AM IN QUESTION FLOW NOT IN TOPIC")
            predicted_sentence_new_response = myAiml(loaction).response(self.kernel, raw_sentence, session_id)

            if (invalid_delim not in predicted_sentence_new_response):
                print (('NOT IN TOPIC and VALID'))
                predicted_sentence = predicted_sentence_new_response
            else:
                print (('NOT IN TOPIC and INVALID'))
                result = self.my_bestmatch_threshold(input_str, topic)
                div_sentence1 = result['bestmatch']
                threshold = result['threshold']

                if (threshold > 75):
                    predicted_sentence = \
                        myAiml(loaction).response(self.kernel,
                                                  div_sentence1, session_id)
                else:
                    predicted_sentence = predicted_sentence_new_response

        print ("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print ("final return questin flow: ", predicted_sentence)
        return predicted_sentence


    def recommendation_engine(self, result_driving_question, predicted_sentence, break_delim, loaction, session_id):
        try:

            if result_driving_question != None:
                full_question = 'Shall I tell you about ' + result_driving_question + '?'
                predicted_sentence = predicted_sentence + break_delim + '<template><type>Card</type><elements><subtitle>' + full_question + '</subtitle><default_action><type>postback</type><payload>Yes</payload></default_action><buttons><type>postback</type><payload>Yes</payload><title>Yes</title></buttons><buttons><type>postback</type><payload>No</payload><title>No</title></buttons></elements></template>'

            if result_driving_question != None:
                my_secret_recommendation = 'SECRETRECOMMENDATIONHDFC'
                recom = myAiml(loaction).response(self.kernel,
                                                  my_secret_recommendation, session_id)

        except:
            predicted_sentence = predicted_sentence

        return predicted_sentence

    def my_bestmatch_threshold(self, query, topic=None, topic_status_direct=0):
        print ("LINE 1358")
        location = self.aiml_location
        query = query.upper()
        query_split = query.split()

        conn = sqlite3.connect(location + '/div_ChatBot_database.db')

        int1 = []
        int2 = []

        query_list = query.split(' ')
        query_list = [x + ' ' for x in query_list]
        query_list = [' ' + x for x in query_list]
        stuff = query_list

        if topic:
            print ("BEST MATCH TOPIC")
            topic1 = []
            print ('TOPIC NAME IS: ', topic)

            start_time = time.time()
            for word in query_split:
                str = '\'% ' + word + ' %\''
                topyc_cur = conn.execute('SELECT * from %s' % (topic))

                for row in topyc_cur:
                    topic1.append(row[0])
            print (topic1)
            if (topic_status_direct == 0):

                generalqna_cur = conn.execute('SELECT * from general_qna')
                for row in generalqna_cur:
                    int2.append(row[0])

            topic1.extend(int2)
            choices = topic1

        else:

            generalqna_cur = conn.execute('SELECT * from general_qna')
            for row in generalqna_cur:
                int1.append(row[0])
            choices = int1
        matches = choices


        div_sentence1 = sorted(matches, key=lambda x: custom_difflib.SequenceMatcher(None, x, query).ratio(),
                               reverse=True)
        res = process.extractOne(query, matches)

        div_sentence1 = div_sentence1[0]
        res = list(res)[0]
        string1 = query.split(' ')
        string2 = div_sentence1.split(' ')
        string3 = res.split(' ')

        string2=[x for x in string2 if x!='']
        string3 = [x for x in string3 if x != '']


        inter1 = set(string1) & set(string2)
        inter2 = set(string1) & set(string3)
        len1 = len(inter1)
        len2 = len(inter2)
        print ('###################### My Best Match ###############################')
        print (string1)
        print ("DIV:",string2)
        print ("FUZZ:",string3)
        print ('###################### My Best Match ###############################')

        if (len1 > len2):
            div_sentence1 = div_sentence1

        elif (len1 == len2):
            div_sentence1 = res
            seq = custom_difflib.SequenceMatcher(None, query, div_sentence1)

        else:
            div_sentence1 = res


        threshold = fuzz.partial_ratio(query, div_sentence1)
        div_sentence1 = div_sentence1
        seq = custom_difflib.SequenceMatcher(None, query, div_sentence1)
        threshold = fuzz.partial_ratio(query, div_sentence1)

        result = {'bestmatch': div_sentence1, 'threshold': threshold}
        print ("RESULT OF BEST_MATCH:        ", result)
        return result


class Cross_Flow_Memory:
    inputHist = []

    def AddMe(self, query):
        Cross_Flow_Memory.inputHist.append(query)


class myAiml:
    appname_list = []
    app_dict = {}

    def __init__(self, std_start, app_name=''):
        self.std = std_start
        self.app_name = app_name

    def loadKernel(self, command):

        if self.app_name not in myAiml.appname_list:
            kernel = aiml.Kernel()
            kernel.bootstrap(learnFiles=self.std, commands=command)
            myAiml.app_dict.update({self.app_name: kernel})
            mykernel = kernel
        elif (Topic_to_update.final_updated_topic):
                kernel = myAiml.app_dict[self.app_name]
                print (kernel)
                kernel.learn('./uploads/'+self.app_name+'/untar/div/update_temp.aiml')
                print ("kernel updated")
                mykernel = kernel
        else:
            # kernel.resetBrain()
            # kernel.bootstrap(learnFiles=self.std, commands=command)            #self.kernel_list.append(kernel)
            kernel = myAiml.app_dict[self.app_name]

            print (kernel)

            kernel.learn(self.std)
            kernel.respond("load aiml b")
            myAiml.app_dict.update({self.app_name: kernel})
            myAiml.appname_list.append(self.app_name)
            mykernel = kernel
        myAiml.appname_list.append(self.app_name)
        return mykernel

    def response(
            self,
            kernel,
            message,
            session_id,
    ):
        self.topic = kernel.getPredicate('topic', session_id)
        return kernel.respond(message, session_id)

    def div_aiml_old_convertations(self, kernel, session_id):
        sessionData = kernel.getSessionData(session_id)
        return sessionData.get('_outputHistory')

    def div_aiml_old_convertations1(self, kernel, session_id):
        sessionData = kernel.getSessionData(session_id)
        return sessionData.get('_inputHistory')

    def div_aiml_old_convertations3(self, kernel, session_id):
        sessionData = kernel.getSessionData(session_id)
        return sessionData

    def setPredicate(
            self,
            key,
            kernel,
            value,
            session_id,
    ):
        return kernel.setPredicate(key, value, session_id)

    def getPredicate(
            self,
            key,
            kernel,
            session_id,
    ):
        return kernel.getPredicate(key, session_id)

    def setBotPredicate(
            self,
            Key,
            Value,
            kernel,
    ):
        kernel.setBotPredicate(Key, Value)


class myAiml2:
    def __init__(self, std_start):
        self.std = std_start

    def loadKernel(self, command):
        kernel = aiml.Kernel()

        kernel.bootstrap(learnFiles=self.std, commands=command)
        return kernel

    def response(
            self,
            kernel,
            message,
            session_id,
    ):
        return kernel.respond(message, session_id)


class spellingCorrector:
    def __init__(self, path):
        self.spell_path = path

    def words(self, text):
        return re.findall(r'\w+', text.lower())

    def redFiles(self, path):
        self.WORDS = Counter(self.words(open(path).read()))

    def getWords(self):
        return self.WORDS

    def getCount(self):
        return sum(self.words.values())

    def P(self, word, N=0):
        '''Probability of `word`.'''

        N = self.getCount()
        return self.words[word] / N

    def correction(self, word):
        '''Most probable spelling correction for word.'''

        return max(self.candidates(word), key=self.P)

    def candidates(self, word):
        '''Generate possible spelling corrections for word.'''

        return self.known([word]) or self.known(self.edits1(word)) \
               or self.known(self.edits2(word)) or [word]

    def known(self, word):
        '''The subset of `words` that appear in the dictionary of WORDS.'''

        return set(w for w in word if w in self.words)

    def edits1(self, word):
        '''All edits that are one edit away from `word`.'''
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for (L, R) in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for (L, R) in splits
                      if len(R) > 1]
        replaces = [L + c + R[1:] for (L, R) in splits if R for c in
                    letters]
        inserts = [L + c + R for (L, R) in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        '''All edits that are two edits away from `word`.'''
        return (e2 for e1 in self.edits1(word) for e2 in
                self.edits1(e1))

    def spell_check(self, input_message):
        return self.correction(input_message)

    def iterate_spell(self, div_input, WORDS):
        self.words = WORDS
        myip = div_input
        myip3 = []
        myip4 = []
        myip2 = myip.split()
        for i in range(0, len(myip2)):
            myip3 = self.correction(''.join(myip2[i])).split()
            myip4 = myip4 + myip3

        correct_spelling = ' '.join(myip4)

        return correct_spelling


class SetReset:
    my_set_variables = ''
    def __init__(self, sentence, session_id, location, aiml_path, kernel, set_val, flowname, flow_reset):
        self.sentence = sentence
        self.session_id = session_id
        self.location = location
        self.aiml_path = aiml_path
        self.kernel = kernel
        self.set_val = set_val
        self.flowname = flowname
        self.flow_reset = flow_reset

    def SetValues(self):
        complex_sentence = ast.literal_eval(self.sentence)
        SetReset.my_set_variables = complex_sentence
        print (complex_sentence, "COMP SMASH")
        if len(complex_sentence) > 0:
            for key, value in complex_sentence.items():
                value = str(value).strip()

                myAiml(self.location).setPredicate(key, self.kernel,
                                                   value, self.session_id)
                print ("VARIABLES %s:%s" % (key, value))
                print (myAiml(self.location).getPredicate(key, self.kernel, self.session_id))

    def ResetValues(self):
        empty = ""
        if self.flow_reset == 0:
            myAiml(self.location).setPredicate("flow_name", self.kernel,
                                               empty, self.session_id)
            print ("Printing Flow RESET")
            print (myAiml(self.location).getPredicate("flow_name", self.kernel, self.session_id))

        fileopen = open(self.aiml_path + "/Flow_Database/RSET/Rset.txt", "r")
        dictionary_db = fileopen.read()
        dictionary_db = ast.literal_eval(dictionary_db)
        key_db = dictionary_db.keys()
        for i in key_db:
            if i == self.flowname:
                val_db = dictionary_db[i]

                for key, value in val_db.items():
                    value = ""

                    myAiml(self.location).setPredicate(key, self.kernel,
                                                       value, self.session_id)
                    print ("VARIABLES %s:%s" % (key, value))
                    print ("Printing in RESET")
                    print (myAiml(self.location).getPredicate(key, self.kernel, self.session_id))