---
layout: post
title: GitLab CI 的 dependencies  和 needs
tag: GitLab, CI, iOS

---

* TOC
{:toc}

在GitLab CI 中，depencencies 和 needs 都是用来标记 job 之间的依赖关系，但是它们在使用场景、实现效果等方面都存在差异，下面我们来分别说明

# depencencies

官方说明：

```
By default, all artifacts from previous stages are passed to each job. However, you can use the dependencies keyword to define a limited list of jobs to fetch artifacts from. You can also set a job to download no artifacts at all.

To use this feature, define dependencies in context of the job and pass a list of all previous jobs the artifacts should be downloaded from.

You can define jobs from stages that were executed before the current one. An error occurs if you define jobs from the current or an upcoming stage.

To prevent a job from downloading artifacts, define an empty array.

When you use dependencies, the status of the previous job is not considered. If a job fails or it’s a manual job that isn’t triggered, no error occurs.
```
> [原文](https://docs.gitlab.com/ee/ci/yaml/#dependencies)


* 定义获取上一个 job 的 artifacts 的具体内容，或是阻止当前 job 获取 artifacts；
* 只能关联之前的 job（按照stage定义的顺序），否则会报错；
* 如果之前的 job 失败/未执行，当前 job 不会因为关联了之前的 job 而报错；

简单概括一下，dependencies 与 artifacts 关键字一起使用，用于控制如何使用上一个 job 生成的 artifacts（工件/生成物）。

# needs

官方说明：


```
Use needs: to execute jobs out-of-order. Relationships between jobs that use needs can be visualized as a directed acyclic graph.  

You can ignore stage ordering and run some jobs without waiting for others to complete. Jobs in multiple stages can run concurrently.
```

> [原文](https://docs.gitlab.com/ee/ci/yaml/#needs)

* needs 可以让 job 按照一定的顺序执行，使用了 needs 关联的 job 形成一个 [有向无环图](https://baike.baidu.com/item/有向无环图/10972513)；
* needs 的另一个特点是，它可以让 job 在上一个 stage 与之关联的 job 完成后立刻开始，而不需要等待上一个 stage 的所有 job 完成，这可以提升流水线的执行速度；


# 参考链接

* [https://docs.gitlab.com/ee/ci/yaml/](https://docs.gitlab.com/ee/ci/yaml/)
* [https://segmentfault.com/a/1190000011890710](https://segmentfault.com/a/1190000011890710)
* [https://ithelp.ithome.com.tw/articles/10244287](https://ithelp.ithome.com.tw/articles/10244287)
