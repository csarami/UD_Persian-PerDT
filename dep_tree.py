import codecs, os, sys
from collections import defaultdict
#import mwe

class Features:
    def __init__(self, feat_str):#process all features in feat_str and put them in dictionary (feat_dict)
        self.feat_str = feat_str
        feat_spl = feat_str.strip().split('|')
        self.feat_dict = dict()
        for feat in feat_spl:
            k,v = feat.split('=')
            self.feat_dict[k] = v

    def __str__(self):
        return self.feat_str

    def feat(self, feat):#get the value of a specific feature (feat)
        return self.feat_dict[feat]
    def add_feat(self,new_feat_dict):
        for key,val in new_feat_dict.items():
            self.feat_dict[key]=val
            self.feat_str+='|'+key+'='+val

class DependencyTree:
    def __init__(self, sent_num, sent_str, words, tags, ftags, heads, labels, lemmas, other_features,semiFinal_tags,final_tags):
        self.sent_descript=sent_num
        self.sent_str=sent_str
        self.words = words
        self.lemmas = lemmas
        self.tags = tags
        self.ftags = ftags
        self.heads = heads
        self.labels = labels
        self.semiFinal_tags=semiFinal_tags
        self.final_tags=final_tags
        self.reverse_tree = defaultdict(set)
        self.other_features = list()
        for f in other_features:
            self.other_features.append(Features(f))

        self.index = dict()
        self.reverse_index = dict()
        for i in range(0,len(words)):

            self.index[i]=i+1
            self.reverse_index[i+1]=i+1

        # We need to increment index by one, because of the root.
        for i in range(0,len(heads)):
            self.reverse_tree[heads[i]].add(i+1)

    def __eq__(self, other):
        if isinstance(other, DependencyTree):
            return self.conllu_str() == other.conllu_str()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.conllu_str())

    @staticmethod
    def trav(rev_head,h,visited): #method to traverse tree rev_head: list of heads, h: the head to be visited, visited: the list of already visited heads
        if rev_head.has_key(h):
            for d in rev_head[h]:
                if d in visited:
                    return True
                visited.append(d)
                DependencyTree.trav(rev_head,d,visited)
        return False

    @staticmethod
    def is_full(heads):
        for dep1 in range(1,len(heads)+1):
            head1=heads[dep1-1]
            if head1<0:
                return False
        return True

    @staticmethod
    def is_nonprojective_arc(d1,h1,d2,h2):
        if d1 > h1 and h1 != h2:
            if (d1 > h2 and d1 < d2 and h1 < h2) or (d1 < h2 and d1 > d2 and h1 < d2):
                return True
        if d1 < h1 and h1 != h2:
            if (h1 > h2 and h1 < d2 and d1 < h2) or (h1 < h2 and h1 > d2 and d1 < d2):
                return True
        return False

    @staticmethod
    def get_nonprojective_arcs(heads):
        non_projectives = set()
        for i in range(len(heads)):
            if i in non_projectives:
                continue
            dep1,head1 = i+1,heads[i]
            for j in range(len(heads)):
                if i==j: continue
                dep2,head2 = j+1, heads[j]
                if DependencyTree.is_nonprojective_arc(dep1, head1, dep2, head2):
                    non_projectives.add(i+1)
                    non_projectives.add(j+1)
        return non_projectives

    @staticmethod
    def is_projective(heads):
        rev_head=defaultdict(list)
        for dep1 in range(1,len(heads)+1):
            head1=heads[dep1-1]
            if head1>=0:
                rev_head[head1].append(dep1)

        visited=list()
        #print rev_head
        if DependencyTree.trav(rev_head,0,visited):
            return False
        if len(visited)<len(heads) and DependencyTree.is_full(heads):
            return False

        rootN=0
        for dep1 in range(1,len(heads)+1):
            head1=heads[dep1-1]
            if head1==0:
                rootN+=1
            if rev_head.has_key(dep1):
                for d2 in rev_head[dep1]:
                    if (d2<head1 and head1<dep1) or (d2>head1 and head1>dep1) and head1>0:
                        return False

            for dep2 in range(1,len(heads)+1):
                head2=heads[dep2-1]
                if head1==-1 or head2==-1:
                    continue
                if dep1>head1 and head1!=head2:
                    if dep1>head2 and dep1<dep2 and head1<head2:
                        return False
                    if dep1<head2 and dep1>dep2 and head1<dep2:
                        return False
                if dep1<head1 and head1!=head2:
                    if head1>head2 and head1<dep2 and dep1<head2:
                        return False
                    if head1<head2 and head1>dep2 and dep1<dep2:
                        return False
        if rootN<1:
            return False
        return True


    @staticmethod
    def load_tree_from_conllu_string(tree_str):
        """
        Loads a conllu string into a DependencyTree object.
        """
        lines = tree_str.strip().split('\n')
        words = list()
        tags = list()
        heads = list()
        labels = list()
        lemmas = list()
        ftags = list()
        semiFinal_tags = list()
        final_tags = list()
        sent_descript=lines[0]
        sent_str=lines[1]
        other_features = list()
        for i in range(2,len(lines)):#for jumping over two first lines (one is sentence number & other is sentence's string
            spl = lines[i].split('\t')  
            if '-' in spl[0]:
                continue
            words.append(spl[1])          #word form
            lemmas.append(spl[2])         #lemma
            tags.append(spl[3])           #pos
            ftags.append(spl[4])          #cpos
            heads.append(int(spl[6]))     #dep head
            other_features.append(spl[5]) #featurs
            labels.append(spl[7])         #dep_rol
            semiFinal_tags.append(spl[8]) #semi final tag 
            final_tags.append(spl[9])     #last tag

        tree = DependencyTree(sent_descript, sent_str, words, tags, ftags, heads, labels, lemmas, other_features,semiFinal_tags,final_tags)
        return tree

    @staticmethod
    def load_trees_from_conllu_file(file_str):
        """
        Loads a conll file into a list of DependencyTree object.
        """
        tree_list = list()
        [tree_list.append(DependencyTree.load_tree_from_conllu_string(tree_str)) for tree_str in open(file_str,'r',encoding='utf-8').read().strip().split('\n\n')]#codecs.
        return tree_list


    def conllu_str(self):
        """
        Converts a DependencyTree object to Conll string.
        """
        lst = list()
        lst.append(self.sent_descript) #adding first line as sentence number
        lst.append(self.sent_str)      #adding second line as sentence string
        for i in range(len(self.words)):
            feats = [str(i+1),self.words[i],self.lemmas[i], self.tags[i],self.ftags[i],str(self.other_features[i]),str(self.heads[i]),self.labels[i],self.semiFinal_tags[i],self.final_tags[i]]
            # ln = str(i+1) +'\t'+self.words[i]+'\t'+self.lemmas[i]+'\t'+self.tags[i]+'\t'+self.ftags[i]+'\t'+str(self.other_features[i])+'\t'+ str(self.heads[i])+'\t'+self.labels[i]+'\t_\t_'
            lst.append('\t'.join(feats))
        return '\n'.join(lst)

    @staticmethod
    def write_to_conllu(tree_list, output_path):
        """
        Write a list of DependencyTree objects into a conll file.
        """
        writer = open(output_path, 'w',encoding='utf-8')
        for tree in tree_list:
            writer.write(tree.conllu_str().strip()+'\n\n')
        writer.close()
    
    def convert_pos(self, universal_tree, ner_tree):
        """
        self is the original tree, the two others are suggestions from
        auto-tagged and auto-ner.
        """
        pass
    def find_children(self,idx):
        return [key for key,val in enumerate(self.heads) if val==idx]
    def exchange_child_parent(self,parent_idx,child_idx,new_rel):
        self.heads[child_idx]=self.heads[parent_idx]
        self.heads[parent_idx]=self.index[child_idx]
        self.labels[child_idx]=self.labels[parent_idx]
        self.labels[parent_idx]=new_rel
    def simple_rel_change(old_rel,new_rel):
        pass

    def convert_tree(self):
        for idx in range(0,len(self.words)):
            old_role=self.labels[idx]
            old_head=self.heads[idx]
            rol_changed=False
            dadeg_pos=self.other_features[idx].feat_dict['dadeg_pos']
            #if dadeg_pos=='PREP' or dadeg_pos=='POSTP':
            #    children=self.find_children(self.index[idx])
            #    if len(children)==1:
            #        self.exchange_child_parent(idx,children[0],'case')
            #    rol_changed=True
            if old_role=='ROOT':
                self.labels[idx]='root'
                rol_changed=True
            elif old_role=='PUNC':
                self.labels[idx]='punct'
                rol_changed=True
            #elif old_role=='APP':
            #    self.labels[idx]='appos'
            #    rol_changed=True
            if rol_changed:
                self.other_features[idx].add_feat({'dadeg_h':old_role,'dadeg_r':str(old_head)})
                #print(str(self.other_features[idx]))#.feat_str  str(self.other_features[i])
                #self.other_features[idx]+='|'+'dadeg_hPar='+old_role+'|dadeg_rP='+str(self.heads[idx])
                

    @staticmethod
    def fix_mwe_entries(tree_list):
        tmas = dict()
        tmas_count = defaultdict(int)
        mwe_file = os.path.dirname(os.path.abspath(__file__)) + '/mwe_conversion.txt'
        mwe_replacements = {line.strip().split('\t')[0]:[line.strip().split('\t')[1],line.strip().split('\t')[2]] for line in open(mwe_file, 'r')}

        lemma_dict = dict()
        for tree in tree_list:
            for i in range(len(tree.words)):
                word, lemma, pos = tree.words[i], tree.lemmas[i], tree.tags[i]
                if len(word.split(' '))>1:
                    assert pos=='V'
                elif pos=='V' and word not in lemma_dict:
                    lemma_dict[word] = lemma

        count_wrong = 0
        # replacing mwes
        for tree in tree_list:
            for i in range(len(tree.words)):
                word, lemma, pos = tree.words[i], tree.lemmas[i], tree.tags[i]
                tree.words[i], tree.lemmas[i], tree.tags[i] = mwe.fix_word_entries(word, lemma, pos, mwe_replacements, lemma_dict)
                if len(word.split())>1:
                    entry = tree.other_features[i].feat('tma')+'\t'+tree.ftags[i]
                    if tree.other_features[i].feat('tma')=="H" and tree.ftags[i]=='ACT':
                        print(tree.words[i])
                        print(" ".join(tree.words))
                        count_wrong += 1
                    if entry not in tmas:
                        tmas[entry] = tree.words[i]
                    tmas_count[entry] += 1
        for entry in sorted(tmas.keys()):
            print(tmas_count[entry], entry, tmas[entry])
        print(count_wrong)

if __name__ == '__main__':
    input_file = os.path.abspath(sys.argv[1])
    #universal_file = os.path.abspath(sys.argv[1])
    #ner_file = os.path.abspath(sys.argv[3])
    output_file = os.path.abspath(sys.argv[2])

    tree_list = DependencyTree.load_trees_from_conllu_file(input_file)
    
    
    #print('fixing MWE inconsistencies')
    #DependencyTree.fix_mwe_entries(tree_list)

    #universal_tree_list = DependencyTree.load_trees_from_conllu_file(universal_file)
    #ner_tree_list = DependencyTree.load_trees_from_conll_file(ner_file)

    # First pass: convert POS tags
    #print('fixing POS inconsistencies')
    #for i, tree in enumerate(tree_list):
    #    tree.convert_pos(universal_tree_list[i], ner_tree_list[i])    

    print('fixing tree inconsistencies')
    # Second pass: convert tree structure
    for i, tree in enumerate(tree_list):
        tree.convert_tree()#(universal_tree_list[i])    
        
    DependencyTree.write_to_conllu(tree_list, output_file)