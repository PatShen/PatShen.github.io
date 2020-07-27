---
layout: post
title: CallKit
tag: CallKit

---

* TOC
{:toc}


# CallKit 能做什么？

## 接听来电

### 通过 Voip 通知接收来电事件

```Swift
// MARK: PKPushRegistryDelegate
func pushRegistry(_ registry: PKPushRegistry, didReceiveIncomingPushWith payload: PKPushPayload, forType type: PKPushType) {
    // report new incoming call
}
```

### 处理来电

在上面的函数中调用：

```Swift
if let uuidString = payload.dictionaryPayload["UUID"] as? String,
    let identifier = payload.dictionaryPayload["identifier"] as? String,
    let uuid = UUID(uuidString: uuidString) {
        let update = CXCallUpdate()    
        update.callerIdentifier = identifier
        
        provider.reportNewIncomingCall(with: uuid, update: update) { error in
            // …
        }
    }

```

### 接通后

系统会调用 `CallKit` 的代理方法：`provider(_:perform:)`，我们在这个代理方法中，可以配置 `AVAudioSession` 并在完成后调用 `fulfill()` 方法：

```Swift
func provider(_ provider: CXProvider, perform action: CXAnswerCallAction) {
    // configure audio session
    action.fulfill()
}
```


## 拨打电话

三种方式：

* 通过 CallKit api 在 app 中直接拨打；
* 通过自定义 URL 唤起；
* 通过 Siri 拨打；

通过 API：

```Swift
let uuid = UUID()
let handle = CXHandle(type: .emailAddress, value: "jappleseed@apple.com")
 
let startCallAction = CXStartCallAction(call: uuid)
startCallAction.destination = handle
 
let transaction = CXTransaction(action: startCallAction)
callController.request(transaction) { error in
    if let error = error {
        print("Error requesting transaction: \(error)")
    } else {
        print("Requested transaction successfully")
    }
}
```

接收者应答后，系统会调用下面的方法，操作过程与被叫一方一样

```Swift
func provider(_ provider: CXProvider, perform action: CXAnswerCallAction) {
    // configure audio session
    action.fulfill()
}
```

## 呼叫阻止和识别

这个功能可以通过 `Call Directory Extension` 来实现，

### 识别

识别过程：

收到来电->到本机通讯录查询匹配->应用程序扩展

应用程序提供标识信息：

```Swift
class CustomCallDirectoryProvider: CXCallDirectoryProvider {
    override func beginRequest(with context: CXCallDirectoryExtensionContext) {
        let labelsKeyedByPhoneNumber: [CXCallDirectoryPhoneNumber: String] = [ … ]
        for (phoneNumber, label) in labelsKeyedByPhoneNumber.sorted(by: <) {
            context.addIdentificationEntry(withNextSequentialPhoneNumber: phoneNumber, label: label)        
        }

        context.completeRequest()
    }
}
```

> ⚠️注意：由于仅在系统启动应用程序扩展时才调用此方法，而不是针对每个单独的调用才调用此方法，因此您必须一次指定所有的呼叫标识信息；否则，将不执行任何操作。例如，您无法向Web服务发出请求以查找有关来电的信息。

### 阻止

过程与识别一致，先到本机黑名单中查询是否有匹配，再到应用程序扩展

```Swift
class CustomCallDirectoryProvider: CXCallDirectoryProvider {
    override func beginRequest(with context: CXCallDirectoryExtensionContext) {
        let blockedPhoneNumbers: [CXCallDirectoryPhoneNumber] = [ … ]
        for phoneNumber in blockedPhoneNumbers.sorted(by: <) {
            context.addBlockingEntry(withNextSequentialPhoneNumber: phoneNumber)
        }
        
        context.completeRequest()
    }
}
```


## CXProviderDelegate

定义了一个必须实现的方法：

```Swift
func providerDidReset(_ provider: CXProvider) {
    
}
```

provider 会在会话被重置时，调用这个函数；开发者需要在此做一些重置操作，比如终止所有正在通话的会话，设置一个默认状态等；

## 点击应答/对方应答

```Swift
func provider(_ provider: CXProvider, perform action: CXAnswerCallAction) {
    
}
```

## 接通成功

```Swift
func provider(_ provider: CXProvider, didActivate audioSession: AVAudioSession) {
    
}
```

## 结束会话

```Swift
func provider(_ provider: CXProvider, perform action: CXEndCallAction) {

    let endCallAction = CXEndCallAction(call: call.callUUID)
    let transaction = CXTransaction(action: endCallAction)
    
    let callController: CXCallController()
    callController.request(transaction) { error in
      if let error = error {
        print("Error requesting transaction: \(error)")
      } else {
        print("Requested transaction successfully")
      }
    }
}
```

## 呼叫保留

```Swift
func provider(_ provider: CXProvider, perform action: CXSetHeldCallAction) {
    // 告知系统执行保留操作
    let setHeldCallAction = CXSetHeldCallAction(call: call.uuid, onHold: onHold)
    let transaction = CXTransaction()
    transaction.addAction(setHeldCallAction)
    
    let callController: CXCallController()
    callController.request(transcation) { error in
        
    }
}
```


## 呼出电话

```Swift
func provider(_ provider: CXProvider, perform action: CXStartCallAction) {
    
}
```

呼出电话基本操作：

1. 配置 audiosession
2. 发起通话，根据发起通话是否成功，调用 action 的 fail() 或 fulfill() 方法
3. 监听通话状态，上报给系统

# 参考链接

* [CallKit | Apple Developer Documentation](https://developer.apple.com/documentation/callkit)
* [CallKit Tutorial for iOS](https://www.raywenderlich.com/1276414-callkit-tutorial-for-ios)