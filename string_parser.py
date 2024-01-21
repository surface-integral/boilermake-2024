def andrew_function(question, operation, problem_type): 
    output = {"Question":"", "Subject1":"", "Quantity1":"", "Subject2":"", "Quantity2":"", "Operation":"", "Type":""}
    output["Question"] = question
    output["Operation"] = operation
    output["Type"] = problem_type

    doc = NER(question)

    sents = [] 
    subject = ""
    for sent in doc.sents: 
        sents.append(sent)
    for sent in sents[:len(sents)-1]:
        print(sent)
        for token in sent:
            if (("subj" in token.dep_) or ("dobj" in token.dep_)):
                subtree = list(token.subtree)
                start = subtree[0].i
                end = subtree[-1].i + 1
                adj = ""
                contains_num = [True if "NUM" == token.pos_ else False for token in doc[start:end]]
                contains_noun = [True if "NOUN" == token.pos_ else False for token in doc[start:end]]
                k = 0 
                seg1 = doc[start:end]
                print(seg1)
                seg2 = ""
                for token in doc[start:end]:
                    if (token.pos_ == "CCONJ"): 
                        if True in [True if "NUM" == token.pos_ else False for token in doc[k+1:]]: 
                            seg1 = doc[start:k]
                            seg2 = doc[k+1:]
                    k += 1 
                for seg in (seg1, seg2): 
                    if seg: 
                        if ((True in contains_num) and (True in contains_noun)):
                            for token in seg[:contains_noun.index(True)+1]:
                                if (token.pos_ == "NUM"): 
                                    if output["Quantity1"] == "":
                                        #print("first quantity:" +token.text)
                                        output["Quantity1"] = token.text
                                    else: 
                                        #print("second quantity:" +token.text)
                                        output["Quantity2"] = token.text
                                if ((token.pos_ == "ADJ") and (token.text != "more")): 
                                    adj = token.text
                                if ((token.pos_ == "NOUN")):   # filter to only nouns 
                                    subject = adj+" "+token.text
                                    if output["Subject1"] == "":
                                        #print("first subject:" +subject)
                                        output["Subject1"] = subject
                                    else: 
                                        #print("second subject:" +subject)
                                        output["Subject2"] = subject
                                    adj = ""
    if output["Subject2"] == "": 
        output["Subject2"] = subject

    return output 