# dadegan_train_path="Persian-Universal-Dependency-Dadegan-master/Universal_Dadegan/train.conllu"#"Persian_Dependency_Treebank_(PerDT)_V1.1.1/Data/train.conll"
dadegan_train_path = "Persian_Dependency_Treebank_(PerDT)_V1.1.1/Data/dev.conll"  # 'UD_Persian-Seraji-master/fa_seraji-ud-train.conllu'
fr = open(dadegan_train_path, 'r', encoding="utf-8")
trainConll = open("dev_ner.txt", 'w', encoding="utf-8")
prev_word_f = ''
prev_word_pos = ''
prev_space = False
prev_pos = ''
prev_sp = []
aft_sp = []
prev_line = ''
sent_i = ''
pos_of_faramosh = []
rParent_of_faramosh = []
for line in fr.readlines():
    if line.strip() != '':  # and (not line.strip().startswith('#')):
        elems = line.strip().split('\t')
        tok_id = elems[0]
        word_form = elems[1]
        word_lemma = elems[2]
        pos = elems[3]
        cpos = elems[4]
        features = elems[5]
        rParent = elems[7]
        new_line = word_form + '\n'
        trainConll.write(new_line)
        trainConll.flush()
        features = features.split('|')
        seperated_feature = {}
        senId = ''
        for part in features:
            key_val = part.split('=')
            seperated_feature[key_val[0]] = key_val[1]
        prev_word_f = word_form
        prev_word_pos = pos
        prev_pos = pos
        prev_line = line
    else:
        trainConll.write('\n')
        trainConll.flush()
        prev_word_f = ''
        prev_word_pos = ''
        prev_pos = ''
        prev_space = False
        prev_line = ''
if line.strip() != '':
    elems = line.strip().split('\t')
    tok_id = elems[0]
    word_form = elems[1]
    word_lemma = elems[2]
    pos = elems[3]
    cpos = elems[4]
    features = elems[5]
    rParent = elems[7]
    new_line = word_form + '\n'
    trainConll.write(new_line)
    trainConll.flush()

trainConll.close()
fr.close()
