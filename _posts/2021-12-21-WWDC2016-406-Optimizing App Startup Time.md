---
layout: post
title: WWDC2016-406-Optimizing App Startup Time
tag: iOS

---

* TOC
{:toc}
本文是对另一篇[博文](https://xiamoon.com/2018/09/23/WWDC2016-406-Optimizing-App-Startup-Time/#more)的转载，以做备份。

# 理论部分

## 一、Mach-O文件：运行时可执行文件的文件类型

### 类型

* 可执行文件。Executable — Main binary for application.
* Dylib — Dynamic library.（aka DSO or DLL）
* Bundle — Dylib that can not be linked. 只能在运行时用dlopen()函数打开。



* Images — Any executable dylib or bundle.
* Framework — Dylib with directory for resources and headers.
* 图像格式：分成3段，每一段都是页面大小的倍数。

下面这个例子：TEXT段是3页，DATA和LINKEDIT各占3页。

![p_1.png](/assets/img/20201221/p_1.png)

页面大小由硬件决定，arm64处理器页面大小是16K，其他的是4K。

> 实际上，几乎每个二进制文件都包含着三段。
>
> * __TEXT：Has headers, code, and read-only constants.
> * __DATA：Has all read-write content: gloables, static variables, etc
> * __LINKEDIT：Has “meta data” about how to load the program.包含变量函数信息，比如名称和地址。

### 通用文件：Universal Files.

假设你有一个Mach-O文件运行在64位(arm64)处理器的设备上，如果你想把它运行在32位(armv7s)的设备上，Xcode里会发生什么变化？

> 会生成另一个单独的Mach-O文件。
>
> 然后这两个文件合并生成第三个文件，这个文件就是通用文件。
>
> 通用文件会有一个头文件，占一页大小。
>
> ![p_2.png](/assets/img/20201221/p_2.png)

## 二、虚拟内存：Virtual Memory

```
意义： 间接层。当所有的进程存在时，该如何管理所有的物理内存？—使用间接层。每一个进程都是一个逻辑地址空间，映射到RAM的某个物理页面。
Features：虚拟内存的作用
```

* Page fault。如果一个虚拟内存不映射到任何物理内存，那么访问这个进程 时，就会产生页面错误，内核会停止该进程，并试图找出解决方案。
* 多个进程可以共享同一块物理内存，进程共享。
* File backed pages：基于文件的映射：不用把整个文件读入RAM，而是调用mmap()函数告诉虚拟内存系统，我想把这个文件映射到进程里的这段地址。

- Copy-On-Write (COW)：写入时复制。写入时复制所做的就是它积极地在所有进程里共享DATA页面，只要进程只读有共享内容的全局变量，但是一旦有进程想要写入其DATA页面，写入时复制开始。内核会把该页面复制，放入另一个物理RAM并重定向映射，所以该进程有了该页面的副本。
- Dirty vs. clean Pages：脏页面和干净页面。上面的副本被认为是脏页面。脏页面是指含有进程特定信息。干净页面是指内核可以按照需要重新建立的页面，比如重新读取磁盘的时候。脏页面比干净页面昂贵得多。

## 三、安全如何影响Dyld

ASLR：把加载地址随机化。

* Adderss Space Layout Randomization.
* Images load at random address.

Code Signing：代码签名。

* Content of each page is hashed.
* Hash is verified on page-in.

## 四、exec() —> main()

```
进程是如何启动的
```

* exec()是一个系统调用。当你进入一个内核，说：我想把这个进程换成这个新程序。然后内核会抹去整个地址来映射这个新的可执行程序。ASLR会给它分配一个随机地址。下一步是从该随机地址回溯到0地址，如下图：把整个地址标记为不可访问。

  ![p_3.png](/assets/img/20201221/p_3.png)

  但是Dylib并不用内核来加载，而是用帮助程序来加载：

  ![p_4.png](/assets/img/20201221/p_4.png)

* Kernal loads helper program
* Dyld (Dynamic loader)
* Executions starts in Dyld (aka LD.SO)

所以，当内核完成内存映射之后，就把指针指向Dyld，**让Dyld来完成进程的启动**。它的工作是加载所有依赖的Dylib，让它们准备好开始运行。其加载过程如下：

![p_5.png](/assets/img/20201221/p_5.png)

### Load dylibs

* 读取所有依赖的Dylib。首先从内核中读取已经加载好的主可执行文件。在这个主可执行文件的Header中有所有依赖库的列表。然后打开和运行这些Dylib，验证它是不是一个Mach-文件，找到它的编码签名，在内核里对它进行注册，在该Dylib的每一段调用mmap()函数。
* 在加载每个Dylib时，每个Dylib可能还依赖于另一个Dylib，所以需要递归式的把它们一个一个找出来加载到内存。

### DATA修复

当所有的Dylib都加载完毕后，他们都是彼此独立的，需要把他们绑在一起。
为了能让一个Dylib调用另一个Dylib，Code-gen实际上在该Dylib的DATA段里新建了一个指针，该指针指向我们想要调用的那个Dylib的位置，然后代码加载该指针，就可以跳向另一个Dylib。
这种修复有两种：

* 重设基址（Rebase）：遍历所有内部数据指针，然后为它们添加一个滑动值。这些指针在段里的位置都编码在__LINKEDIT段里。I/O比较多。
* 绑定（Bind）：针对那些指向Dylib范围外的指针而言的。其计算复杂度比Rebase要高得多。
* ObjC：经过前两步之后，在ObjC运行时还需要一些额外的操作。在ObjC运行时，必须要维护一张表格，包含所有名称及其映射的类。每次加载的名称都将定义一个类，名称需要登记在一个全局表格里

### Initializer

* 进入+load()方法（如果有的话），现在不建议使用。
* 调用顺序是从下往上。

### 跳转到main()函数

## 四、总结

![p_6.png](/assets/img/20201221/p_6.png)

# 实际部分

## 一、启动速度多快才是好的用户体验？

答：400 ms

应用的launch过程，这里复述了理论部分的内容：

![p_7.png](/assets/img/20201221/p_7.png)

* Warm launch：冷启动

  App is not in kernel buffer cache.

  应用在kill掉之后很长一段时间后，或者reboot重启手机之后，再打开应用的时候就是冷启动。

* Cold launch：热启动。

  App and data already in memory.

  应用启动时还在内存里，或者之前启动过，然后退出了，此时应用还在内核的磁盘缓存里。

## 二、如何测量启动速度？Why is launch slow？我们可以做什么？

Measuring before main()

在应用启动并运行之前，一般的方法是无法测量这个时间的。

### DYLD_PRINT_STATICTICS environment variable

在Xcode里的Edit Scheme里设置环境变量：

![p_8.png](/assets/img/20201221/p_8.png)

然后重新开始运行APP，控制台里会打印出在main()之前耗费的时间：

![p_9.png](/assets/img/20201221/p_9.png)

这个是我的APP所花费的时间。这个测量是支持模拟器运行的，不过最好用真机测试。

* dylib loading: OS dylibs 加载很快，因为构建OS时，会预计算大量的dylib数据，但是始终无法全部预算。所以，Embedded dylibs are expensive.

  减少使用dylibs：Merge existing dylibs，Use static archives，使用延时加载，但是尽量不要使用dlopen()。

* rebase/bind: rebase由于I/O的原因，会比较慢。时间都花费在修复__DATA里的指针。所以方法就是减少需要修复的指针。

  减少ObjC类对象和ivars的数量

  减少使用C++虚拟函数

  使用Swift语言 ：Swift通常用的数据要少一些。而且Swift更为内联，可以更好地使用code-gen减少消耗

* ObjC setup：它要注册类，处理非脆弱ivar，注册目录，让选择器变成唯一。但是这里一般不需要我们人为的过多的处理。

* Initializer：

  显示的初始化器：ObjC +load()方法。（如果你是用的话最好换成+initialize()方法，因为不推荐使用+load()方法） 但是这种显示的初始化器最好换成点初始化器：dispatch_once()或者pthread_once()或者std::once()

  隐式初始化器：大部分来自C++的全局变量，带有非默认的初始化器，非默认的构造函数。这里可以用前面提到的点初始化器替代，或者把全局的换成非全局的结构或者指针，指向想要初始化的对象。或者Only set simple values (PODs)。或者用Swift重新编写，Swift的全局变量可以在使用前确保被初始化，其本质还是在后台调用了点初始化器。

  > 注意：
  >
  > * 不要使用dlopen()，会有死锁或者其他未定义的行为发生，还会导致性能下降
  > * 不要在初始化器上开启线程。会带来性能下降和正确性的问题

## 三、总结

![p_10.png](/assets/img/20201221/p_10.png)

# 更多

## 二进制重排

原因：虚拟内存；内存分页；缺页异常（常见于app启动时）

方法：使用order文件进行（libobjc.order）

检验：

1. Build Settings -> Write Link Map File => YES
2. add xxx.order，写入你想要执行的方法的顺序
3. Build Settings -> Order File 加入order文件路径

效果：可以让启动时需要加载的方法尽量集中，减少缺页异常提高启动速度。

# 参考链接

* [https://xiamoon.com/2018/09/23/WWDC2016-406-Optimizing-App-Startup-Time/#more](https://xiamoon.com/2018/09/23/WWDC2016-406-Optimizing-App-Startup-Time/#more)
* [https://developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time](https://developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time)
