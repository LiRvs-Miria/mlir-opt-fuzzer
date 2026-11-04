module {
  func.func @f(%a : i32) -> i32 {
    return %a : i32
  }
}
builtin.module(func.func(cse))
