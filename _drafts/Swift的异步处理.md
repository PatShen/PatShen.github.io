
* Task
* await

Example:

```Swift
Task {
  do {
    try await requestManager.sendRequest
  } catch {
    // catch error
  }
}
```
