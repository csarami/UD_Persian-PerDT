"""
* Fix "wa"s that are tagged as SUBR
* Change wrong dependencies in PARCL.
* Change VConj order.
* Convert active to passive for Shodan verbs.
"""

from dep_tree import DependencyTree


def fix_verb_conj_order(tree, v, label):
    v_head = tree.heads[v] - 1
    v_grand_head = tree.heads[v_head]
    tree.heads[v] = v_grand_head
    tree.labels[v] = tree.labels[v_head]
    tree.heads[v_head] = v + 1
    tree.labels[v_head] = label
    tree.rebuild_children()


def fix_cc_order(tree, cc, label):
    if len(tree.children[cc + 1]) == 0:
        print("Warning: No CC children", tree.other_features[0].feat_dict['senID'])
        return

    children = sorted(list(tree.children[cc + 1]))
    cc_dep = None
    for c in children:
        child = c - 1
        if child < cc + 1 and tree.tags[child] in {"ADR", "V", "PSUS", "N", "PREM", "ADJ"}:
            cc_dep = child

    if cc_dep is None:
        print("Orphaned", tree.other_features[0].feat_dict['senID'])
        return


    cc_head = tree.heads[cc] - 1
    cc_grand_head = tree.heads[cc_head]
    cc_grand_label = tree.labels[cc_grand_head - 1] if cc_grand_head > 0 else "ROOT"
    tree.heads[cc_dep] = cc_grand_head
    tree.labels[cc_dep] = cc_grand_label
    tree.heads[cc_head] = cc + 1
    tree.labels[cc_head] = "POSDEP"
    tree.heads[cc] = cc_dep + 1
    tree.labels[cc] = label
    tree.rebuild_children()


def fix_vconj_order(tree):
    vconj_list = []
    for i in range(len(tree.labels) - 1, -1, -1):
        label = tree.labels[i]
        if label == "VCONJ":
            if tree.tags[i] == "CONJ":
                fix_cc_order(tree, i, tree.labels[i])
            else:
                fix_verb_conj_order(tree, i, tree.labels[i])
            vconj_list.append((i, tree.heads[i], tree.tags[i], tree.words[i]))


if __name__ == '__main__':
    input_files = ['Persian_Dependency_Treebank_(PerDT)_V1.1.1/Data/train.conll',
                   'Persian_Dependency_Treebank_(PerDT)_V1.1.1/Data//dev.conll',
                   'Persian_Dependency_Treebank_(PerDT)_V1.1.1/Data//test.conll']
    output_files = ['Persian_Dependency_Treebank_(PerDT)_V1.1.1/Data/train.conll',
                    'Persian_Dependency_Treebank_(PerDT)_V1.1.1/Data//dev.conll',
                    'Persian_Dependency_Treebank_(PerDT)_V1.1.1/Data//test.conll']

    for f_idx, inp_f in enumerate(input_files):
        parcl_trees = []
        vconj_trees = []
        tree_list = DependencyTree.load_trees_from_conll_file(inp_f)
        for i, tree in enumerate(tree_list):
            for w, (lemma, word, ftag) in enumerate(zip(tree.lemmas, tree.words, tree.ftags)):
                if lemma == "گشت#گرد" and ftag=="PASS":
                    tree.ftags[w] = "ACT"
                if lemma == "شد#شو" and ftag=="PASS":
                    tree.ftags[w] = "ACT"
                if lemma in {"کرد#کن"} and ftag=="PASS":
                    if "شو" not in word and "شد" not in word:
                        tree.ftags[w] = "ACT"
                        print(word)
                    else:
                        tree.ftags[w] = "ACT"
                        tree.lemmas[w] = "شد#شو"

            # for w, word in enumerate(tree.words):
            #     if word == "و" and tree.tags[w] == "SUBR":
            #         tree.tags[w] = "CONJ"
            #         tree.ftags[w] = "CONJ"
            # if "PARCL" in tree.labels:
            #     parcl_trees.append(tree)
            # if "VCONJ" in tree.labels:
            #     vconj_trees.append(tree)
            #     fix_vconj_order(tree)



        for tree in parcl_trees:
            include_tree = False
            parcl_idx = [i for i, label in enumerate(tree.labels) if label == "PARCL"]
            for idx in parcl_idx:
                head_index = tree.heads[idx]
                head_id = head_index - 1

                for dep in range(0, idx):
                    if tree.heads[dep] > idx + 1:
                        if tree.labels[dep] not in {"PREDEP", "PARCL", "MOS", "NVE", "VPP", "PUNC", "OBJ", "NPP",
                                                    "VCONJ"}:
                            if tree.labels[dep] in {"SBJ", "AJUCL", "ADV"}:
                                # Change the head for SBJ/AJUCL/ADV
                                tree.heads[dep] = idx + 1
        DependencyTree.write_to_conll(tree_list, output_files[f_idx])
