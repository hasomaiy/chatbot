from nltk.corpus import stopwords
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import re
# from dateutil.parser import _timelex, parser
import ast
###################Defining a list which contains topics for definite ComplexQueries

class CompQ_NotFlow:

    def __init__(self,prev_list,flo,raw_sentence,  fileup_path):
        ##HELLO
        self.input_raw_sentence = raw_sentence.lower()
        self.fileup_path = fileup_path
        self.prev_list = prev_list
        self.flo = flo

    def generic_nflo(self):
        match = self.Match_threshold()
        flow = match['flow']
        print (flow, "  flow")
        method_to_call = getattr(self, flow)()
        final_result = method_to_call
        print ("Printing from Generic: ", final_result)
        return final_result


############# PREMIUM CALCULATION
    def calculatepremiumflow(self):
        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']
        count = 0
        # %%%%%%%%%%%%%%%%mobile
        try:
            mob = (re.findall(r'\d+', string))
            for m in mob:
                if len(m) == 10:
                    mob = m
                else:
                    mob = None
            if not mob:
                mob = None
        except:
            mob = None

            # %%%%%%%%%%%%email
        try:
            string = ' '.join(d)
            string = string.replace('*$', '.')
            email = re.findall(r'[\w\.-]+@[\w\.-]+', string)
            email = email[0]
            email = email.replace('.', '*$')
        except:
            email = None

            # %%%%%%%%%%%%name
        try:
            string = ' '.join(d)
            string = re.sub(r'[^A-Za-z]+', '', string)
            try:
                em = re.sub(r'[^A-Za-z]+', '', email)
                name_str = string.replace(em, '')
            except:
                name_str = string
            name = name_str.replace(self.flo, '')
            if 'calculatepremium' in name:
                name = None
            if not name:
                name = None
        except:
            name = None

        string = ''.join(d)

        try:
            sum_nt = (re.findall(r'amount\d+', string)) or (re.findall(r'assured\d+', string)) or (
                re.findall(r'sum\d+', string)) or (re.findall(r'\d+am.', string)) or (re.findall(r'\d+sum.', string))
            sum_nt = re.findall(r'\d+', str(sum_nt[0]))
            sum_nt = int(sum_nt[0])
        except:
            sum_nt = 'None'

        try:
            age_nt = (re.findall(r'age\d+', string)) or (re.findall(r'female\d+y.', string)) or (
                re.findall(r'male\d+y.', string)) or (re.findall(r'non.\d+y.', string)) or (
                         re.findall(r'smoker\d+y.', string))
            age_nt = ''.join(age_nt[0])
            print (age_nt, "AGE_NT")
            age_nt = re.findall(r'\d+', age_nt)
            age_nt = int(age_nt[0])

        except:
            age_nt = 'None'

        try:
            term_nt = re.findall(r'policy\d+', string) or re.findall(r'term\d+', string) or re.findall(r'limit\d+',
                                                                                                       string)
            term_nt = re.findall(r'\d+', str(term_nt[0]))
            term_nt = int(term_nt[0])

        except:
            term_nt = 'None'

        gen = ["male", "m", "female", "f"]
        ske = ["non smoker", "non-smoker", "nonsmoker", "non smokey", "non-smokey", "smoker", "smokey", "smoke"]

        try:
            gen_value = self.compare(gen, d)
            gen_value = d[gen_value]

        except:
            gen_value = 'None'

        try:
            ske_value = self.compare(ske, d)
            ske_value = d[ske_value]

        except:
            ske_value = 'None'

        vlue_value = str(sum_nt)
        yrs_value = str(age_nt)
        policy_value = str(term_nt)
        gen_value = str(gen_value)
        ske_value = str(ske_value)
        name = str(name)
        mob = str(mob)
        email = str(email)

        val = [name,mob,email,vlue_value,yrs_value,policy_value,gen_value,ske_value]
        val_start = val
        final_list = []

        for item in self.prev_list:           ####setting previous list's '' into 'None'. and getting a final_list
            if item:
                final_list.append(item)
            else:
                final_list.append('None')

        print ("############")
        print ("val: ",val)
        print ("final_list: ",final_list)
        print ("############")


        ll = []


        for f, b in zip(val, final_list):     ####setting previously obtained valid values into current list.
            if (f != b):
                if f != 'None':
                    ll.append(f)

                elif b is not 'None':
                    ll.append(b)

            else:
                if (f != 'None'):
                    ll.append(f)
                else:
                    ll.append('None')

        val = ll
        '''
        val2 = []
        for v in val:
            if v:
                v = v.replace('F', 'None')
                val2.append(v)
            else:
                v = 'None'
                val2.append(v)
        val = val2
        '''
        print ("AfterFINAL VALLLLLLLLLLLLLLLLLLLLLL: ", ll)
        print ("AfterFINAL VALLLLLLLLLLLLLLLLLLLLLL: ", val)

        max_count = len(val)

        count_val = 0
        for j in val:
            if j == 'None':
                count_val = count_val + 1

        original_count = len(val_start)
        final_count = count_val

        print ("COUNTINGGGGGGG: ")
        print ('original cnt: ', original_count)
        print ("final count: ", final_count)
        if original_count != final_count:
            intimation_complex = "MY KERNEL"
        else:
            intimation_complex = "MOVE AHEAD"



        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)
        if None_count == 'notpresent':
            val = 'notpresent'
        else:

            f_val = [val[0],'/$/', val[1],'/$/', val[2],'/$/', val[3],'/$/', val[4],'/$/', val[5],'/$/', val[6],'/$/', val[7]]
            val = ' '.join(f_val)

        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']
        Complex_Flow = {}

        if (threshold >= 70):
            Complex_Flow["param"] = val
            #Complex_Flow["flow"] = string2


        else:
            Complex_Flow["param"] = "notpresent"
            #Complex_Flow["flow"] = "notpresent"
        ret_dict  = {'Complex_Flow': Complex_Flow, 'intimation_complex': intimation_complex}

        return ret_dict

################# LIVE CHAT
    def chatliveagentflow(self):

        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']
        count = 0

    #%%%%%%%%%%%%%%%%mobile
        try:
            mob = (re.findall(r'\d+', string))
            for m in mob:
                if len(m) == 10:
                    mob = m
                else:
                    mob = None
            if not mob:
                mob = None
        except:
            mob = None

    #%%%%%%%%%%%%email
        try:
            string = ' '.join(d)
            string = string.replace('*$', '.')
            email = re.findall(r'[\w\.-]+@[\w\.-]+', string)
            email = email[0]
            email = email.replace('.', '*$')
        except:
            email = None

    #%%%%%%%%%%%%name
        try:
            string = ' '.join(d)
            string = re.sub(r'[^A-Za-z]+', '', string)
            try:
                em = re.sub(r'[^A-Za-z]+', '', email)
                name_str = string.replace(em, '')
            except:
                name_str = string
            name = name_str.replace(self.flo,'')
            if 'chatliveagent' in name:
                name = None
            if not name:
                name = None
        except:
            name = None

        name = str(name)
        mob  = str(mob)
        email = str(email)

        val = [name,mob ,email]
        val_start = val
        final_list = []

        for item in self.prev_list:  ####setting previous list's '' into 'None'. and getting a final_list
            if item:
                final_list.append(item)
            else:
                final_list.append('None')

        print ("############")
        print (self.prev_list)
        print (val)
        print (final_list)
        print ("############")

        ll = []
        for f, b in zip(val, final_list):     ####setting previously obtained valid values into current list.
            f = f.strip()
            b = b.strip()
            if (f != b):
                if f != 'None':
                    ll.append(f)

                elif b != 'None':
                    ll.append(b)
            else:
                if (f != 'None'):
                    ll.append(f)
                else:
                    ll.append('None')

        val = ll
        val2 = []
        for v in val:
            if v:
                v = v.replace('F', 'None')
                val2.append(v)
            else:
                v = 'None'
                val2.append(v)
        val = val2
        print ("AfterFINAL VALLLLLLLLLLLLLLLLLLLLLL: ",      ll)
        print ("AfterFINAL VALLLLLLLLLLLLLLLLLLLLLL: ",      val)

        max_count = len(val)

        count_val = 0
        for j in val:
            if j == 'None':
                count_val = count_val + 1


        original_count = len(val_start)
        final_count = count_val


        print ("COUNTINGGGGGGG: ")
        print ('original cnt: ', original_count)
        print ("final count: ", final_count)

        if original_count != final_count:
            intimation_complex = "MY KERNEL"
        else:
            intimation_complex = "MOVE AHEAD"


        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)
        if None_count == 'notpresent':
            val = 'notpresent'
        else:

            f_val = [val[0],'/$/', val[1],'/$/', val[2]]
            val = ' '.join(f_val)

        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']
        Complex_Flow = {}

        if (threshold >= 70):
            Complex_Flow["param"] = val
            #Complex_Flow["flow"] = string2

        else:
            Complex_Flow["param"] = "notpresent"
            #Complex_Flow["flow"] = "notpresent"

        ret_dict  = {'Complex_Flow': Complex_Flow, 'intimation_complex': intimation_complex}
        return ret_dict

################# CALL BACK
    def callbackflow(self):

        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']
        count = 0

    # %%%%%%%%%%%%%%%%mobile
        try:
            mob = (re.findall(r'\d+', string))
            for m in mob:
                if len(m) == 10:
                    mob = m
                else:
                    mob = None
            if not mob:
                mob = None
        except:
            mob = None

    # %%%%%%%%%%%%email
        try:
            string = ' '.join(d)
            string = string.replace('*$', '.')
            email = re.findall(r'[\w\.-]+@[\w\.-]+', string)
            email = email[0]
            email = email.replace('.', '*$')
        except:
            email = None

    # %%%%%%%%%%%%name
        try:
            string = ' '.join(d)
            string = re.sub(r'[^A-Za-z]+', '', string)
            try:
                em = re.sub(r'[^A-Za-z]+', '', email)
                name_str = string.replace(em, '')
            except:
                name_str = string
            name = name_str.replace(self.flo, '')
            if 'callback' in name:
                name = None
            if not name:
                name = None
        except:
            name = None

        name = str(name)
        mob = str(mob)
        email = str(email)

        val = [name, mob]
        val_start = val
        final_list = []

        for item in self.prev_list:  ####setting previous list's '' into 'None'. and getting a final_list
            if item:
                final_list.append(item)
            else:
                final_list.append('None')

        print ("############")
        print (self.prev_list)
        print (val)
        print (final_list)
        print ("############")

        ll = []
        for f, b in zip(val, final_list):  ####setting previously obtained valid values into current list.
            f = f.strip()
            b = b.strip()
            if (f != b):
                if f != 'None':
                    ll.append(f)

                elif b != 'None':
                    ll.append(b)
            else:
                if (f != 'None'):
                    ll.append(f)
                else:
                    ll.append('None')

        val = ll

        val2 = []
        for v in val:
            if v:
                v = v.replace(' F ', 'None')
                val2.append(v)
            else:
                v = 'None'
                val2.append(v)
        val = val2
        print ("AfterFINAL VALLLLLLLLLLLLLLLLLLLLLL: ", ll)
        print ("AfterFINAL VALLLLLLLLLLLLLLLLLLLLLL: ", val)

        max_count = len(val)

        count_val = 0
        for j in val:
            if j == 'None':
                count_val = count_val + 1

        original_count = len(val_start)
        final_count = count_val

        print ("COUNTINGGGGGGG: ")
        print ('original cnt: ', original_count)
        print ("final count: ", final_count)

        if original_count != final_count:
            intimation_complex = "MY KERNEL"
        else:
            intimation_complex = "MOVE AHEAD"

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)
        if None_count == 'notpresent':
            val = 'notpresent'
        else:

            f_val = [val[0], '/$/', val[1]]
            val = ' '.join(f_val)

        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']
        Complex_Flow = {}

        if (threshold >= 70):
            Complex_Flow["param"] = val
            # Complex_Flow["flow"] = string2

        else:
            Complex_Flow["param"] = "notpresent"
            # Complex_Flow["flow"] = "notpresent"

        ret_dict = {'Complex_Flow': Complex_Flow, 'intimation_complex': intimation_complex}
        return ret_dict



################# POST_QUERY
    def postqueryflow(self):

        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']
        count = 0

    # %%%%%%%%%%%%%%%%mobile
        try:
            mob = (re.findall(r'\d+', string))
            for m in mob:
                if len(m) == 10:
                    mob = m
                else:
                    mob = None
            if not mob:
                mob = None
        except:
            mob = None

    # %%%%%%%%%%%%email
        try:
            string = ' '.join(d)
            string = string.replace('*$', '.')
            email = re.findall(r'[\w\.-]+@[\w\.-]+', string)
            email = email[0]
            email = email.replace('.', '*$')
        except:
            email = None

    # %%%%%%%%%%%%name
        try:
            string = ' '.join(d)
            string = re.sub(r'[^A-Za-z]+', '', string)
            try:
                em = re.sub(r'[^A-Za-z]+', '', email)
                name_str = string.replace(em, '')
            except:
                name_str = string
            name = name_str.replace(self.flo, '')
            if 'postquery' in name:
                name = None
            if not name:
                name = None
        except:
            name = None

        name = str(name)
        mob = str(mob)
        email = str(email)

        val = [name, mob, email]
        val_start = val
        final_list = []

        for item in self.prev_list:  ####setting previous list's '' into 'None'. and getting a final_list
            if item:
                final_list.append(item)
            else:
                final_list.append('None')

        print ("############")
        print (self.prev_list)
        print (val)
        print (final_list)
        print ("############")

        ll = []
        for f, b in zip(val, final_list):  ####setting previously obtained valid values into current list.
            f = f.strip()
            b = b.strip()
            if (f != b):
                if f != 'None':
                    ll.append(f)

                elif b != 'None':
                    ll.append(b)
            else:
                if (f != 'None'):
                    ll.append(f)
                else:
                    ll.append('None')

        val = ll
        val2 = []
        for v in val:
            if v:
                v = v.replace(' F ', 'None')
                val2.append(v)
            else:
                v = 'None'
                val2.append(v)
        val = val2
        print ("AfterFINAL VALLLLLLLLLLLLLLLLLLLLLL: ", ll)
        print ("AfterFINAL VALLLLLLLLLLLLLLLLLLLLLL: ", val)

        max_count = len(val)

        count_val = 0
        for j in val:
            if j == 'None':
                count_val = count_val + 1

        original_count = len(val_start)
        final_count = count_val

        print ("COUNTINGGGGGGG: ")
        print ('original cnt: ', original_count)
        print ("final count: ", final_count)

        if original_count != final_count:
            intimation_complex = "MY KERNEL"
        else:
            intimation_complex = "MOVE AHEAD"

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)
        if None_count == 'notpresent':
            val = 'notpresent'
        else:

            f_val = [val[0], '/$/', val[1], '/$/', val[2]]
            val = ' '.join(f_val)

        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']
        Complex_Flow = {}

        if (threshold >= 70):
            Complex_Flow["param"] = val
            # Complex_Flow["flow"] = string2

        else:
            Complex_Flow["param"] = "notpresent"
            # Complex_Flow["flow"] = "notpresent"

        ret_dict = {'Complex_Flow': Complex_Flow, 'intimation_complex': intimation_complex}
        return ret_dict


################################Other functions
    def Initial_processing(self):
        print ("I AM IN INITIAL PROCESSING")
        #print self.input_raw_sentence
        fmt_string = self.input_raw_sentence +" " +self.flo
        stop = set(stopwords.words('english'))
        d = [i for i in fmt_string.lower().split() if i not in stop]
        #print d
        string = ''.join(d)
        #print string
        result = {'string': string, 'd': d}
        return result

    def Match_threshold(self): ## to find best match an for calculation of threshold
        Initial = self.Initial_processing()
        d = Initial['d']
        string = Initial['string']
        fileopen = open(self.fileup_path + "/Flow_Database/Santosh/flow_database.txt", "r")
        dictionary_db = fileopen.read()
        dictionary_db = ast.literal_eval(dictionary_db)
        fileopen.close()
        key_db = dictionary_db.keys()
        #print ("PRINTING KEY DB"
        #print key_db
        #print string
        #print d

        res = process.extractOne(string, key_db)
        res = list(res)[0]
        #print res
        threshold = fuzz.partial_ratio(d, res)
        #print threshold

        extracted_result = dictionary_db[res]
        result = {'flow': extracted_result ,'threshold': threshold}
        return result

    def compare(self, s1, s2): # compare the specific text from given query
        stop = set(stopwords.words('english'))
        d = [i for i in self.input_raw_sentence.lower().split() if i not in stop]
        slen = len(s1)
        y = 0
        while y < slen:
            if s1[y] in d:
                key = d.index(s1[y])
                return key
            else:
                key = -1
            y += 1

    def date(self,matches1):
        if len(matches1) > 0:
            date = matches1
            return date
        else:
            return 'No dates found'

    def mat(self,Dates): ## getting the dates
        mat1 = Dates[0]
        mat1 = mat1[0]
        mat2 = Dates[0]
        mat2 = mat2[1]
        if not mat1:
            mat1 = 'None'
            mat2 = Dates[0]
            mat2 = mat2[1]
        if not mat2:
            mat2 = 'None'
            mat1 = Dates[0]
            mat1 = mat1[0]
        return mat1, mat2

    def None_count(self,count, max_count): ##for counting number o 'None' values in  parameters
        #print count, "  NONE COUNT"
        if count == max_count:
            val = "notpresent"
        else:
            val = "present"
        return val
