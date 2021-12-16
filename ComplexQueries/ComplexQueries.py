from nltk.corpus import stopwords
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import re
# from dateutil.parser import _timelex, parser
import ast
###################Defining a list which contains topics for definite ComplexQueries

class ComplexQueries:

    def __init__(self, input_raw_sentence, fileup_path): ###, aiml_flow_name, comp):
        ##HELLO
        self.input_raw_sentence = input_raw_sentence
        self.fileup_path = fileup_path
        #self.AI_name = aiml_flow_name
        #self.comp = comp

    def generic(self):
        match = self.Match_threshold()
        flow = match['flow']
        print ("in COMP query flowname: ", flow)
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

        val = [name, mob, email, vlue_value, yrs_value, policy_value, gen_value, ske_value]

        print ("VALLLLLLLLLLLLLLLLLLLLLL: ", val)

        max_count = len(val)

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)
        if None_count == 'notpresent':
            val = 'notpresent'
        else:
            val = [name,'/$/', mob,'/$/', email,'/$/',vlue_value,'/$/', yrs_value,'/$/', policy_value,'/$/', gen_value,'/$/', ske_value]
            val = ' '.join(val)

        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']
        Complex_Flow = {}

        if (threshold >=70):
            Complex_Flow["param"] = val
            Complex_Flow["flow"] = string2


        else:
            Complex_Flow["param"] = "notpresent"
            Complex_Flow["flow"] = "notpresent"

        return Complex_Flow

########## LEAVE BALANCE
    def leavebalanceflow(self):
        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']
        try:
            emp_nt = (re.findall(r'id\d+', string)) or (re.findall(r'\d+emp.', string))
            emp_nt = ''.join(emp_nt[0])
            emp_nt = re.findall(r'\d+', emp_nt)
            emp_nt = int(emp_nt[0])
        except:
            emp_nt = None

        bal = ["balance", "available"]

        try:
            bal_value = self.compare(bal, d)
            bal_value = d[bal_value] or "leave"
        except:
            bal_value = "None"

        emp_value = str(emp_nt)

        val = [bal_value, emp_value]
        count = 0
        max_count = 2

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)

        if None_count == 'notpresent':
            val = 'notpresent'
        else:
            val = [bal_value,'/$/', emp_value]
            val = ' '.join(val)

        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']
        Complex_Flow = {}


        if (threshold >= 70):
            Complex_Flow["param"] = val
            Complex_Flow["flow"] = string2
        else:
            Complex_Flow["param"] = "notpresent"
            Complex_Flow["flow"] = "notpresent"

        return Complex_Flow

########### HR POLICY
    def hrpolicyflow(self):
        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']

        try:
            emp_nt = (re.findall(r'id\d+', string)) or (re.findall(r'\d+emp.', string))
            emp_nt = ''.join(emp_nt[0])
            emp_nt = re.findall(r'\d+', emp_nt)
            emp_nt = int(emp_nt[0])
        except:
            emp_nt = None

        hr = ["hr", "hrpolicy", "hrpolicies"];

        try:
            hr_value = self.compare(hr, d)
            hr_value = d[hr_value]

        except:
            hr_value = "None"
        emp_value = str(emp_nt)
        val = [hr_value,emp_value]
        count = 0
        max_count = 2

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)

        if None_count == 'notpresent':
            val = 'notpresent'
        else:
            val = [hr_value,'/$/', emp_value]
            val = ' '.join(val)


        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']

        Complex_Flow = {}
        if (threshold >= 70):
            Complex_Flow["param"] = val
            Complex_Flow["flow"] = string2
        else:
            Complex_Flow["param"] = "notpresent"
            Complex_Flow["flow"] = "notpresent"

        return Complex_Flow

########### HOLIDAY LIST
    def holidaylistflow(self):
        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']

        try:
            emp_nt = (re.findall(r'id\d+', string)) or (re.findall(r'\d+emp.', string))
            emp_nt = ''.join(emp_nt[0])
            emp_nt = re.findall(r'\d+', emp_nt)
            emp_nt = int(emp_nt[0])
        except:
            emp_nt = None
        holiday = ["holiday", "list"]

        try:
            holiday_value = self.compare(holiday, d)
            holiday_value = d[holiday_value]
        except:
            holiday_value = "None"
        emp_value = str(emp_nt)
        val = [holiday_value, emp_value]
        count = 0
        max_count = 2

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)

        if None_count == 'notpresent':
            val = 'notpresent'
        else:
            val = [holiday_value,'/$/', emp_value]
            val = ' '.join(val)


        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']
        Complex_Flow = {}

        if (threshold >= 70):
            Complex_Flow["param"] = val
            Complex_Flow["flow"] = string2
        else:
            Complex_Flow["param"] = "notpresent"
            Complex_Flow["flow"] = "notpresent"

        return Complex_Flow

################# LEAVE APPLICATION
    def leaveapplicationflow(self):
        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']
        fmt_string = Initial['fmt_string']

        try:
            emp_nt = (re.findall(r'id\d+', string)) or (re.findall(r'\d+emp.id', string))
            emp_nt = ''.join(emp_nt[0])
            emp_nt = re.findall(r'\d+', emp_nt)
            emp_nt = int(emp_nt[0])
        except:
            emp_nt = None

        emp_value = str(emp_nt)

        leave = ["leave", "apply","take"]

        try:
            leave_value = self.compare(leave, d)
            leave_value = d[leave_value]
        except:
            leave_value = "None"

        pattern1 = re.compile(r'from (.*) till (.*)')
        pattern2 = re.compile(r'from (.*) to (.*)')
        pattern3 = re.compile(r'start (.*) end (.*)')

        matches1 = re.findall(pattern1, fmt_string) or re.findall(pattern2, fmt_string) or re.findall(pattern3,
                                                                                                      fmt_string)
        Dates = self.date(matches1)


        a = self.mat(Dates)
        a = ' /$/ '.join(a)

        val = [leave_value, emp_value, a]
        count = 0
        max_count = 4

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)

        if None_count == 'notpresent':
            val = 'notpresent'
        else:
            val = [leave_value,'/$/', emp_value,'/$/',a]
            val = ' '.join(val)


        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']
        Complex_Flow = {}

        if (threshold >= 70):
            Complex_Flow["param"] = val
            Complex_Flow["flow"] = string2
        else:
            Complex_Flow["param"] = "notpresent"
            Complex_Flow["flow"] = "notpresent"

        return Complex_Flow

################# LIVE CHAT
    def chatliveagentflow(self):

        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']
        count = 0
        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']

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
            if 'chatliveagent' in name:
                name = None
            if not name:
                name = None
        except:
            name = None

        name = str(name)
        mob = str(mob)
        email = str(email)


        val = [name, mob, email]
        print ("VALLLLLLLLLLLLLLLLLLLLLL: ", val)
        max_count = len(val)

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)
        if None_count == 'notpresent':
            val = 'notpresent'
        else:
            val = [name, '/$/', mob, '/$/', email]
            val = ' '.join(val)

        Complex_Flow = {}
        #print threshold

        if (threshold >= 70):
            Complex_Flow["param"] = val
            Complex_Flow["flow"] = string2

        else:
            Complex_Flow["param"] = "notpresent"
            Complex_Flow["flow"] = "notpresent"

        return Complex_Flow


################# CALL BACK
    def callbackflow(self):

        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']
        count = 0
        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']

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

        val = [name, mob]
        print ("VALLLLLLLLLLLLLLLLLLLLLL: ", val)
        max_count = len(val)

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)
        if None_count == 'notpresent':
            val = 'notpresent'
        else:
            val = [name, '/$/', mob]
            val = ' '.join(val)

        Complex_Flow = {}
        #print threshold

        if (threshold >= 70):
            Complex_Flow["param"] = val
            Complex_Flow["flow"] = string2

        else:
            Complex_Flow["param"] = "notpresent"
            Complex_Flow["flow"] = "notpresent"

        return Complex_Flow

################# POST_QUERY
    def postqueryflow(self):

        Initial = self.Initial_processing()
        string = Initial['string']
        d = Initial['d']
        count = 0
        match = self.Match_threshold()
        string2 = match['flow']
        threshold = match['threshold']

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
        print ("VALLLLLLLLLLLLLLLLLLLLLL: ", val)
        max_count = len(val)

        for i in val:
            if i == 'None':
                count = count + 1

        None_count = self.None_count(count, max_count)
        if None_count == 'notpresent':
            val = 'notpresent'
        else:
            val = [name, '/$/', mob, '/$/', email]
            val = ' '.join(val)

        Complex_Flow = {}
        #print threshold

        if (threshold >= 70):
            Complex_Flow["param"] = val
            Complex_Flow["flow"] = string2

        else:
            Complex_Flow["param"] = "notpresent"
            Complex_Flow["flow"] = "notpresent"

        return Complex_Flow

#########################################################################################################################
    def Initial_processing(self):
        fmt_string = self.input_raw_sentence
        stop = set(stopwords.words('english'))
        d = [i for i in fmt_string.lower().split() if i not in stop]
        string = ''.join(d)
        result = {'string': string, 'd': d}
        return result

    def Match_threshold(self): ## to find best match an for calculation of threshold
        Initial = self.Initial_processing()
        d = Initial['d']
        string = Initial['string']

        print ("INPUT TO MATCH THRESHOLD: ", string)
        fileopen = open(self.fileup_path + "/Flow_Database/Santosh/flow_database.txt", "r")
        dictionary_db = fileopen.read()
        dictionary_db = ast.literal_eval(dictionary_db)
        key_db = dictionary_db.keys()
        #print ("KEYDB"
        #print key_db
        #print string


        res = process.extractOne(string, key_db)
        #print ("RES"
        #print res
        res = list(res)[0]
        #print res
        threshold = fuzz.partial_ratio(string, res)
        print ("@#$@#$@#$@#$")
        print (threshold)
        print ("@#$@#$@#$@#$")

        extracted_result = dictionary_db[res]
        #print ("MTACH FOLW"
        #print extracted_result
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
            mat1 = "None"
            mat2 = Dates[0]
            mat2 = mat2[1]
        if not mat2:
            mat2 = "None"
            mat1 = Dates[0]
            mat1 = mat1[0]
        return mat1, mat2

    def None_count(self,count, max_count): ##for counting number o None values in  parameters
        if count == max_count:
            val = "notpresent"
        else:
            val = "present"
        return val
