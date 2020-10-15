import os
import json
import random
from shutil import copytree, rmtree


def get_configs(config_file):
    """
    define and retrieve config for name-biased sampling
    """
    config = json.load(open(config_file, 'r'))
    sample_type = config['sample_type']
    source_root_dir = config['source_root_dir']
    target_root_dir = config['target_root_dir']
    datasets = config['benchmark']
    train_val_ratios = [
        config['train_val_ratio']['1st'],
        config['train_val_ratio']['2nd'],
        config['train_val_ratio']['3rd']
    ]
    attr_pivots = config['attr_pivots']
    cfgs = []
    for dataset in datasets:
        for train_ratio, val_ratio in train_val_ratios:
            cfg = dict(source_root_dir=source_root_dir,
                       target_root_dir=target_root_dir,
                       dataset=dataset)
            cfg['train_val_ratios'] = train_val_ratios
            cfg['train_ratio'] = train_ratio
            cfg['val_ratio'] = val_ratio
            cfg['source_dir'] = os.path.join(source_root_dir,
                                             dataset)
            cfg['target_dir'] = os.path.join(target_root_dir,
                                             f'{dataset}_{sample_type}_{train_ratio:.2f}_{val_ratio:.2f}')
            cfg['attr_pivots'] = attr_pivots
            cfg['sample_type'] = sample_type
            cfgs.append(cfg)
    return cfgs


def copy_source_data(cfgs):
    """
    copy source data to target directory
    """
    rmtree(cfgs[0]['target_root_dir'], ignore_errors=True)
    for cfg in cfgs:
        source_dir = cfg['source_dir']
        target_dir = cfg['target_dir']
        rmtree(target_dir, ignore_errors=True)
        copytree(source_dir, target_dir)
        print(f'copy source data: dataset: {cfg["dataset"]} \
                train_ratio: {cfg["train_ratio"]} \
                val_ratio: {cfg["val_ratio"]}')


def read_rdf(fp):
    """
    read triples in RDF-format
    """
    with open(fp) as f:
        lines = f.readlines()
        items = [line.strip().split('\t') for line in lines]
    return items


def write_rdf(rdf_items, fp):
    """
    write triples in RDF-format
    """
    with open(fp, 'w') as f:
        for item in rdf_items:
            if len(item) == 3:
                item = item[:2]
            item_str = '\t'.join(item)
            f.write(item_str)
            f.write('\n')


def build_attr_dict(attr_triples):
    """
    build attribute dictionary (dict[entity][attr] = value)
    """
    d = dict()
    for e, a, v in attr_triples:
        d.setdefault(e, dict())
        d[e][a] = v
    return d


def get_attr_count(ent, attr_dict, dataset):
    """
    calculate count of attributes of given entity
    """
    if ent not in attr_dict:
        return 0
    return len(attr_dict[ent])


def get_name(ent, attr_dict, dataset):
    """
    retrieve name from entity (D_W / D_Y / others)
    """
    if ent not in attr_dict:
        return ent.split('/')[-1].replace('_', ' ').lower()

    if 'D_Y' in dataset:
        name_attribute_list = ['skos:prefLabel',
                               'http://dbpedia.org/ontology/birthName']
    elif 'D_W' in dataset:
        name_attribute_list = ['http://www.wikidata.org/entity/P373',
                               'http://www.wikidata.org/entity/P1476']
    else:
        name_attribute_list = []

    for a, v in attr_dict[ent].items():
        if a in name_attribute_list:
            return v.lower()
    return ent.split('/')[-1].replace('_', ' ').lower()


def split_data(seq, train_ratio, val_ratio):
    """
    Split data into train/val partitions
    """
    train_num = int(len(seq) * train_ratio)
    val_num = int(len(seq) * val_ratio)

    train_seq = seq[:train_num]
    val_seq = seq[train_num:train_num + val_num]
    test_seq = seq[train_num + val_num:]
    return train_seq, val_seq, test_seq


def calc_edit_distance(word1, word2):
    """
    calculate edit distance score based on (edit distance / max length)
    """
    size1 = len(word1)
    size2 = len(word2)
    max_size = max(size1, size2)
    last = 0
    temp = list(range(size2 + 1))
    value = None
    for ii in range(size1):
        temp[0] = ii + 1
        last = ii
        for jj in range(size2):
            if word1[ii] == word2[jj]:
                value = last
            else:
                value = 1 + min(last, temp[jj], temp[jj + 1])
            last = temp[jj + 1]
            temp[jj + 1] = value
    return (1 - (value / max_size))


def get_name_bias_stats(links, attr_dict1, attr_dict2, cfg):
    """
    get statistics of name-biased links (return ratio)
    """
    num_same = 0
    num_close = 0
    num_diff = 0
    for ii in range(len(links)):
        ent_name1 = get_name(links[ii][0], attr_dict1, cfg['dataset'])
        ent_name2 = get_name(links[ii][1], attr_dict2, cfg['dataset'])
        score = calc_edit_distance(ent_name1, ent_name2)
        if score == 1.0:
            num_same += 1
        elif score == 0.0:
            num_diff += 1
        else:
            num_close += 1
    ratio = "  same%.2f  close%.2f  diff%.2f" % (
        num_same / len(links),
        num_close / len(links),
        num_diff / len(links))
    return ratio


def get_attr_bias_stats(links, attr_dict1, attr_dict2, cfg):
    """
    get statistics of attr-biased links (return ratio)
    """
    count_small = 0
    count_mid = 0
    count_large = 0
    pivot_1st = cfg['attr_pivots'][0]
    pivot_2nd = cfg['attr_pivots'][1]
    for ii in range(len(links)):
        ent_count1 = get_attr_count(links[ii][0], attr_dict1, cfg['dataset'])
        ent_count2 = get_attr_count(links[ii][1], attr_dict2, cfg['dataset'])
        avg_count = (ent_count1 + ent_count2) / 2
        if avg_count <= pivot_2nd:
            count_small += 1
        elif avg_count > pivot_2nd and avg_count <= pivot_1st:
            count_mid += 1
        else:
            count_large += 1
    count_sum = count_small + count_mid + count_large
    ratio = "  large%.2f  mid%.2f  small%.2f" % (
        count_large / count_sum,
        count_mid / count_sum,
        count_small / count_sum)
    return ratio


def sample_benchmark(cfg):
    """
    sample train/valid/test splits for name-biased setting
    """
    sample_type = cfg['sample_type']
    assert sample_type in ['baseline', 'name-biased', 'attr-biased', 'industry']
    root_dir = cfg['target_dir']
    ent_links = read_rdf(os.path.join(root_dir, 'ent_links'))
    attr_triples1 = read_rdf(os.path.join(root_dir, 'attr_triples_1'))
    attr_triples2 = read_rdf(os.path.join(root_dir, 'attr_triples_2'))
    attr_dict1 = build_attr_dict(attr_triples1)
    attr_dict2 = build_attr_dict(attr_triples2)
    ent_links_scored = []
    pivot_1st = cfg['attr_pivots'][0]
    pivot_2nd = cfg['attr_pivots'][1]
    # same_name_ent_links = []
    # not_same_ent_links = []
    for ent_link1, ent_link2 in ent_links:
        ent_name1 = get_name(ent_link1, attr_dict1, cfg['dataset'])
        ent_name2 = get_name(ent_link2, attr_dict2, cfg['dataset'])
        ent_count1 = get_attr_count(ent_link1, attr_dict1, cfg['dataset'])
        ent_count2 = get_attr_count(ent_link2, attr_dict2, cfg['dataset'])
        # score = z_name + z_attr
        overall_score = 0
        if sample_type in ['name-biased', 'industry']:
            edit_score = calc_edit_distance(ent_name1, ent_name2)
            if edit_score == 1.0:
                overall_score += 4
            elif edit_score < 1.0 and edit_score > 0.0:
                overall_score += 3
            elif edit_score == 0.0:
                overall_score += 1
        if sample_type in ['attr-biased', 'industry']:
            avg_count = (ent_count1 + ent_count2) / 2
            if avg_count <= pivot_2nd:
                overall_score += 1
            elif avg_count > pivot_2nd and avg_count <= pivot_1st:
                overall_score += 3
            elif avg_count > pivot_1st:
                overall_score += 4
        ent_links_scored.append([ent_link1, ent_link2, overall_score])
    # sort ent_links based on score
    ent_links_scored.sort(key=lambda x: x[2], reverse=True)
    # print(sample_type, ent_links_scored[:5])

    train_links, val_links, test_links = split_data(ent_links_scored,
                                                    train_ratio=cfg['train_ratio'],
                                                    val_ratio=cfg['val_ratio'])

    print(f'<{cfg["dataset"]}> train_ratio: {cfg["train_ratio"]} val_ratio: {cfg["val_ratio"]}')
    train_name_bias = get_name_bias_stats(train_links, attr_dict1, attr_dict2, cfg)
    train_attr_bias = get_attr_bias_stats(train_links, attr_dict1, attr_dict2, cfg)
    print(f'train-name-bias-stats: {train_name_bias}')
    print(f'train-attr-bias-stats: {train_attr_bias}')
    val_name_bias = get_name_bias_stats(val_links, attr_dict1, attr_dict2, cfg)
    val_attr_bias = get_attr_bias_stats(val_links, attr_dict1, attr_dict2, cfg)
    print(f'val-name-bias-stats: {val_name_bias}')
    print(f'val-attr-bias-stats: {val_attr_bias}')
    test_name_bias = get_name_bias_stats(test_links, attr_dict1, attr_dict2, cfg)
    test_attr_bias = get_attr_bias_stats(test_links, attr_dict1, attr_dict2, cfg)
    print(f'test-name-bias-stats: {test_name_bias}')
    print(f'test-attr-bias-stats: {test_attr_bias}')

    # in accordance with OpenEA input https://github.com/nju-websoft/OpenEA
    write_rdf(train_links, os.path.join(root_dir, '721_5fold', '1', 'train_links'))
    write_rdf(val_links, os.path.join(root_dir, '721_5fold', '1', 'valid_links'))
    write_rdf(test_links, os.path.join(root_dir, '721_5fold', '1', 'test_links'))


if __name__ == '__main__':
    random.seed(2048)
    cfgs = get_configs('config.json')

    copy_source_data(cfgs)
    for cfg in cfgs:
        sample_benchmark(cfg)
