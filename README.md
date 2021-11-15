# industry-eval-EA

The code and benchmark of paper _**An Industry Evaluation of Embedding-based Entity Alignment**_ [[arxiv](https://arxiv.org/pdf/2010.11522.pdf)] [[coling](https://aclanthology.org/2020.coling-industry.17.pdf)] in Proceedings of COLING 2020.

## Code

We present the source code to generate biased seed mappings for EA.
```
code
|__ check_benchmark.py
|__ sample_benchmark.py
|__ config.json
```
Specifically, we present a total of **four** settings in extracting biased seed mappings:

* baseline [without any bias]
  * "Ideal" in 4.2 of our paper
  * "With No Bias" in 4.3 of our paper
* name-biased [same name]
  * "With Name Bias" in 4.3 of our paper
* attr-biased [more attributes]
  * "With Attribute Bias" in 4.3 of our paper
* industry [same name & more attributes]
  * "Industrial" in 4.2 of our paper

all of which follow the algorithm introduced in 3.2 of our paper.

To check the validity of any to-be-used benchmark, please run ```check_benchmark.py``` to verify the benchmark format.

To generate/sample biased seed mappings from to-be-used benchmark, please run ```sample_benchmark.py``` and later check train/val/test splits in the ```target_root_dir``` defined in ```config.json```.

To reproduce the experimental results in our paper, please refer to [OpenEA](https://github.com/nju-websoft/OpenEA) to run the experiments based on the biased seed mappings (mentioned above).

### examples

We list some statistics of sampled biased seed mappings as follows.
```
<D_W_15K_V2> train_ratio: 0.02 val_ratio: 0.01
train-name-bias-stats:   same1.00  close0.00  diff0.00
train-attr-bias-stats:   large1.00  mid0.00  small0.00
val-name-bias-stats:   same1.00  close0.00  diff0.00
val-attr-bias-stats:   large1.00  mid0.00  small0.00
test-name-bias-stats:   same0.32  close0.21  diff0.47
test-attr-bias-stats:   large0.57  mid0.32  small0.10
```
When sampling biased seed mappings from the public benchmark [D_W_15K_V2](https://github.com/nju-websoft/OpenEA) under the **industry** setting (both name-biased and attribute-biased), it can be seen that train/val splits only contains biased seed mappings, which have the *same* name and *large* number of attributes.

## Benchmark

We extracted the industry benchmark, named **MED-BBK-9K**, from two real-world medical KGs for alignment, which can be found [here](./benchmark/industry.zip).
```
industry.zip
|__ attr_triples_1          # attribute triples of KG1
|__ attr_triples_2          # attribute triples of KG2
|__ ent_links               # entity links between KGs (ground-truth)
|__ rel_triples_1           # relation triples of KG1
|__ rel_triples_2           # relation triples of KG2
```

The statistics of the industry benchmark is listed as follows. [D_W_15K_V2](https://github.com/nju-websoft/OpenEA) is also recorded for the purpose of comparison.

| Benchmark | KGs | #Ents | #Rels | #Rel triples | Rel degree | #Attrs | #Attr triples | Attr degree |
| --------- | --- | ----- | ----- | ------------ | ---------- | ------ | ------------- | ----------- |
| MED-BBK-9K | MED | 9,162 | 32 | 158,357 | 34.04 | 19 | 11,467 | 1.24 |
| MED-BBK-9K | BBK | 9,162 | 20 | 50,307 | 10.96 | 21 | 44,987 | 4.91 |
| D-W-15K | DBpedia | 15,000 | 167 | 73,983 | 8.55 | 175 | 66,813 | 4.40 |
| D-W-15K | Wikidata | 15,000 | 121 | 83,365 | 10.31 | 457 | 175,686 | 11.59 |

### examples

We list some fragments of our industry benchmark as follows.

**ent_links**
```
<月经异常>\t<月经不调>
<弓形体病性巩膜炎>\t<弓形虫病性巩膜炎>
<巨趾症>\t<巨趾症>
<发细菌感染>\t<a40292>
<脑溢血后遗症>\t<脑出血后遗症>
```
**rel_triples**
```
<骨关节病>\t<典型症状>\t<僵硬>
<额区感觉减退>\t<相关疾病>\t<下肢动脉硬化闭塞症>
<绦虫病>\t<典型症状>\t<恶心>
<胆汁返流性胃炎>t<典型症状>\t<反酸>
<脐炎>\t<典型症状>\t<发热>
```
**attr_triples**
```
<病毒性食管炎>\t<英文名>\t<viralesophagitis>
<碱中毒>\t<临床表现>\t<它是呼吸系统对碱中毒的代偿现象，借助于浅而慢的呼吸，得以增加肺泡内的pco，使[bhco] [hhco]的分母加大，以减少因分子变大而发生的比值改变（稳定ph值）。躁动、兴奋、谵语、嗜睡、严重时昏迷。有手足搐搦，腱反射亢进等。如已发生钾缺乏，可能出现酸性尿的矛盾现象，应特别注意。标准碳酸氢（sb）、实际碳酸氢（ab）、缓冲碱（bb）、碱剩余（be）增加，血液paco、血液ph值升高。>
<十二指肠溃疡>\t<就诊科室>\t<消化内科>
```

## Citation

If you have any difficulty or question in running code and reproducing experimental results, please email to zihengzhang1025@gmail.com

If you use this model or code, please cite it as follows:

```
@inproceedings{zhang2020industry,
  title={An Industry Evaluation of Embedding-based Entity Alignment},
  author={Zhang, Ziheng and Liu, Hualuo and Chen, Jiaoyan and Chen, Xi and Liu, Bo and Xiang, YueJia and Zheng, Yefeng},
  booktitle={Proceedings of the 28th International Conference on Computational Linguistics: Industry Track},
  pages={179--189},
  year={2020}
}
```
