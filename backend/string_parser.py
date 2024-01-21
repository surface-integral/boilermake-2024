import spacy
from textblob import TextBlob

NER = spacy.load("en_core_web_sm")

def determine_type_add(question: str):
    if (('more' in question) | ('than' in question)):
        return "More Than"
    elif (('and' in question) | ('another' in question) | ('total' in question) | ('altogether' in question)):
        return "And"
    else: 
        return "Original Amount"

def parse_problem(question: str, operation: str, problem_type: str): 
    output = {"Question":"", "Subject1":"", "Quantity1":"", "Subject2":"", "Quantity2":"", "Operation":"", "Type":""}
    output["Operation"] = operation
    output["Type"] = problem_type
    doc = NER(question)

    sents = [] 
    subject = ""
    quantity = ""
    for sent in doc.sents: 
        sents.append(sent)
    output["Question"] = sents[-1].text
    for sent in sents[:len(sents)-1]:
        for token in sent:
            if(token.pos_ == "NUM") and (output["Quantity1"] != ""):
                output["Quantity2"] = token.text
            if (token.dep_ == "nummod"): 
                subtree = list(token.subtree)
                start = subtree[0].i
                end = subtree[-1].i + 1
                j = 1
                for token2 in doc[end:]:
                    if not subject:
                        if token2.pos_ == "NOUN":
                            for token3 in doc[end:end+j]:
                                subject += token3.text+" "
                            break; 
                j += 1 
                quantity = doc[start:end].text
                if output["Quantity1"] == "":
                    output["Quantity1"] = quantity
                else: 
                    output["Quantity2"] = quantity

                if output["Subject1"] == "":
                    output["Subject1"] = subject
                else: 
                    output["Subject2"] = subject
            if (not subject) and (not quantity):
                if (("subj" in token.dep_) or ("dobj" in token.dep_)):
                    subtree = list(token.subtree)
                    start = subtree[0].i
                    end = subtree[-1].i + 1
                    adj = ""
                    contains_num = [True if "NUM" == token.pos_ else False for token in doc[start:end]]
                    contains_noun = [True if "NOUN" == token.pos_ else False for token in doc[start:end]]
                    k = 0 
                    seg1 = doc[start:end]
                    seg2 = ""
                    for token in doc[start:end]:
                        if (token.pos_ == "CCONJ"): 
                            if True in [True if "NUM" == token.pos_ else False for token in doc[k+1:]]: 
                                seg1 = doc[start:end][:k]
                                seg2 = doc[start:end][k+1:]
                        k += 1 
                    for seg in (seg1, seg2): 
                        if seg: 
                            if ((True in contains_num) and (True in contains_noun)):
                                for token in seg[:contains_noun.index(True)+1]:
                                    if (token.pos_ == "NUM"): 
                                        quantity = token.text
                                        if output["Quantity1"] == "":
                                            output["Quantity1"] = quantity
                                        else: 
                                            output["Quantity2"] = quantity
                                    if ((token.pos_ == "ADJ") and (token.text != "more")): 
                                        adj = token.text
                                    if ((token.pos_ == "NOUN")):   # filter to only nouns 
                                        subject = adj+" "+token.text
                                        #Singularize token subjects
                                        if token.tag_ == "NNS":
                                            subject = adj + TextBlob(token.text).words[0].singularize()
                                        if output["Subject1"] == "":
                                            output["Subject1"] = subject
                                        else: 
                                            output["Subject2"] = subject
                                        adj = ""
        if output["Subject2"] == "": 
            output["Subject2"] = subject

    print(output["Subject1"])
    return output 
