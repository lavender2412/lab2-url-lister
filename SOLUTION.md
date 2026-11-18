# Lab 2: UrlCount with Hadoop Streaming (Python)

## Solution
UrlCount counts every `href="..."` URL in two Wikipedia articles (Apache Hadoop and MapReduce) and outputs only URLs that appear more than 5 times, using Hadoop Streaming with Python.

- `URLMapper.py` reads the HTML line by line and uses the regex `href="([^"]*)"` to capture everything between `href="` and the next double quote. A single line can contain many links, so it uses `findall` and emits `url<TAB>1` for each one. It counts every href attribute, including `<link>` tags such as `mw-data:TemplateStyles:...`, not only visible hyperlinks.
- `URLReducer.py` relies on Hadoop sorting map output by key, so identical URLs arrive consecutively. It sums the counts for the current URL, and when the URL changes it prints the previous one only if its total is greater than 5.
- `make urlstream` runs the job (see the Makefile). Locally: `cat input/* | ./URLMapper.py | sort | ./URLReducer.py`.

Result: 10 URLs pass the threshold. Top entries: `mw-data:TemplateStyles:r1333433106` (122), `mw-data:TemplateStyles:r1295599781` (33), `#` (22), `/wiki/ISBN_(identifier)` and `/wiki/Doi_(identifier)` (18 each). Exact numbers vary with the download date.

## Software needed
Python 3 (3.11 used) and Hadoop 3.3.6 with the streaming jar. The Makefile's `STREAM_JAR` path is for the CSEL environment. On Dataproc, use `make urlstream STREAM_JAR=/usr/lib/hadoop/hadoop-streaming.jar`.

## Combiner and the `> 5` filter
The filter can only be applied in the final reducer. The two articles go to different mappers, so each mapper sees only partial counts. A URL with 3 occurrences in one article and 4 in the other has a true total of 7 and must pass, but a combiner or mapper that filtered early would drop both partial counts. So no combiner is used. If one were added, it could only sum, never filter.

## Dataproc timing (e2-standard-2 nodes, us-east4)
| Cluster | `real` time | Map tasks | Reduce tasks |
|---|---|---|---|
| 1 master + 2 workers | 1m42.845s | 10 | 3 |
| 1 master + 4 workers | 1m36.612s | 22 | 7 |

Both runs produced the same 10 URLs as the local CSEL run.

## Discussion
Doubling the workers saved only about 6 seconds (about 6%), far from a 2x speedup. The input is two small files (about 850 KB in total), so the actual map and reduce work takes a few seconds, and fixed costs dominate: submitting the job, starting YARN containers, JVM and Python startup in every task, and the shuffle. Dataproc also scales the default number of tasks with the cluster (10 maps and 3 reducers on 2 workers, 22 and 7 on 4), so more workers meant more, smaller tasks, each with its own startup overhead.

Caveat: Dataproc's default 1000 GB boot disks exceeded my project's disk quota for a 4-worker cluster, so I rebuilt the 4-worker cluster with 100 GB disks. The 2-worker run used the default 1000 GB disks, so the comparison is not perfectly like-for-like. Smaller standard disks can also have lower I/O throughput. Also, because there were several reducers, the output was spread across multiple `part-*` files rather than one.

## Resources and collaboration
- Hadoop and Streaming docs, Michael Noll's Python streaming tutorial, and the course README.
- I used Claude as a tutor for guidance and debugging. I wrote and ran the code myself.
- Collaborators: none.
