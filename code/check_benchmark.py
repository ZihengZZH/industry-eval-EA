import os
import json


def read_rdf(fp):
    """
    read RDF-format triples
    """
    with open(fp) as f:
        lines = f.readlines()
        items = [line.strip().split('\t') for line in lines]
    return items


def valid_ent_links(root_dir):
    """
    check validity of ent_links
    """
    ent_links = read_rdf(os.path.join(root_dir, 'ent_links'))
    for item in ent_links:
        assert len(item) == 2

    ents1 = [item[0] for item in ent_links]
    ents2 = [item[1] for item in ent_links]
    assert len(ents1) == len(set(ents1))
    assert len(ents2) == len(set(ents2))
    assert len(ent_links) == len(set([tuple(item) for item in ent_links]))


def valid_attr(root_dir):
    """
    check validity of attr_triples
    """
    ent_links = read_rdf(os.path.join(root_dir, 'ent_links'))
    ents1 = set([item[0] for item in ent_links])
    ents2 = set([item[1] for item in ent_links])
    attr_triples1 = read_rdf(os.path.join(root_dir, 'attr_triples_1'))
    attr_triples2 = read_rdf(os.path.join(root_dir, 'attr_triples_2'))
    for item in attr_triples1:
        assert len(item) == 3
        assert item[0] in ents1
    for item in attr_triples2:
        assert len(item) == 3
        assert item[0] in ents2
    assert len(attr_triples1) == len(set(tuple(item) for item in attr_triples1))
    assert len(attr_triples2) == len(set(tuple(item) for item in attr_triples2))


def valid_rel(root_dir):
    """
    check validity of rel_triples
    """
    ent_links = read_rdf(os.path.join(root_dir, 'ent_links'))
    ents1 = set([item[0] for item in ent_links])
    ents2 = set([item[1] for item in ent_links])
    rel_triples1 = read_rdf(os.path.join(root_dir, 'rel_triples_1'))
    rel_triples2 = read_rdf(os.path.join(root_dir, 'rel_triples_2'))
    rel_ents1 = set([item[0] for item in rel_triples1] + [item[2] for item in rel_triples1])
    rel_ents2 = set([item[0] for item in rel_triples2] + [item[2] for item in rel_triples2])
    for item in rel_triples1:
        assert len(item) == 3
        assert item[0] in ents1
        assert item[2] in ents1
    for item in rel_triples2:
        assert len(item) == 3
        assert item[0] in ents2
        assert item[2] in ents2
    assert len(rel_triples1) == len(set(tuple(item) for item in rel_triples1))
    assert len(rel_triples2) == len(set(tuple(item) for item in rel_triples2))
    for ent1 in ents1:
        assert ent1 in rel_ents1, ent1
    for ent2 in ents2:
        assert ent2 in rel_ents2, ent2


if __name__ == '__main__':
    config = json.load(open('config.json', 'r'))
    for benchmark in config['benchmark']:
        root_dir = os.path.join(config['source_root_dir'], benchmark)
        valid_ent_links(root_dir)
        valid_attr(root_dir)
        valid_rel(root_dir)
        print('benchmark checking passed ', root_dir)
