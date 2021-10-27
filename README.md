# An Arxiv Spider

做为一个cser，杰出男孩深知内核对连接到计算机上的硬件设备进行管理的高效方式是中断而不是轮询。每当小伙伴发来一篇刚挂在arxiv上的”热乎“好文章时，杰出男孩都会感叹道：”师兄这是每天都挂在arxiv上呀，跑的好快~“。于是杰出男孩找了找 github，借鉴了一下其他大佬们的脚本，实现了一个每天向自己的邮件发送('cs.CV','cs.AI','stat.ML','cs.LG','cs.RO')里面感兴趣的文章的spider，支持自定义**key word**以及感兴趣的**author**。

## How to run

1. 配置main.py里面的邮箱用户名和密码，记得开启邮箱的pop3验证

2. 修改run.sh里面代码的目录和运行的python env的路径

3. 使用crontab设置定时任务

   ```bash
   crontab -e
   ```

   contrab内容为

   ```bash
   0 10 * * 1,2,3,4,5 bash your_dir/arxiv_spider/run.sh
   ```

   即每周一到周五，早上10点定时推送arxiv当天更新到邮箱

arxiv是一个非常棒的网站，用脚本高频率爬取肯定是要被谴责的行为。但文章每天只更新一次，所以建议大家每天运行一次脚本，相当于每天逛一次arxiv了~

## Result

```
Today arxiv has 338 new papers in ['cs.CV', 'cs.AI', 'stat.ML', 'cs.LG', 'cs.RO'] area, and 127 of them is about CV, 2/2 of them contain your keywords.

Ensure your keywords is ['(?i)offline.*(RL|reinforcement learning)', '(?i)(RL|reinforcement learning).*offline'].

This is your paperlist.Enjoy!

------------1------------
arXiv:2110.12468
Title: SCORE: Spurious COrrelation REduction for Offline Reinforcement Learning
['Machine Learning (cs.LG)', 'Artificial Intelligence (cs.AI)']
https://arxiv.org/abs/2110.12468

------------2------------
arXiv:2110.13060
Title: Safely Bridging Offline and Online Reinforcement Learning
['Machine Learning (cs.LG)', 'Machine Learning (stat.ML)']
https://arxiv.org/abs/2110.13060

Ensure your authors is ['Sergey Levine', 'Song Han'].

This is your paperlist.Enjoy!

------------1------------
arXiv:2110.12080
Title: C-Planning: An Automatic Curriculum for Learning Goal-Reaching Tasks
['Machine Learning (cs.LG)', 'Artificial Intelligence (cs.AI)']
https://arxiv.org/abs/2110.12080

------------2------------
arXiv:2110.12543
Title: Understanding the World Through Action
['Machine Learning (cs.LG)']
https://arxiv.org/abs/2110.12543
```

## Acknowledgement

This code is built upon the implementation from https://github.com/ZihaoZhao/Arxiv_daily
