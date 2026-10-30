module {
  async.func @async_func_assert() -> !async.token {
    return
  }
  async.func @async_func_nested_assert() -> !async.token {
    %0 = call @async_func_assert() : () -> !async.token
    return
  }
}
