Objective-C 读取Gif图片内容

首先通过 GIF 的 NSData 创建一个 CGImageSourceRef 对象

```
CGImageSourceRef source = CGImageSourceCreateWithData((__bridge CFDataRef)assetData, NULL);
```

这里 CGImageSourceRef 就是一个代表图片的不透明的数据类型，它抽象了读取图像数据的通道，但本身不会读取图像的任何数据。

读取某一帧的图片

```
CGImageRef image = CGImageSourceCreateImageAtIndex(source, i, NULL);
```

> 知道图片的fps之后，计算得到的准确度会提高


参考链接：[iOS 中对 GIF 的裁剪与展示](#http://www.cocoachina.com/ios/20180312/22546.html)