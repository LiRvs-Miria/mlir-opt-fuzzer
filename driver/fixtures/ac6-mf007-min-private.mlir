module {
  func.func private @data_if(%arg0: !llvm.ptr, %arg1: i1) {
    %c40_i64 = arith.constant 40 : i64
    %0 = acc.map_info varPtr(%arg0 : !llvm.ptr) varType(f32) size(%c40_i64 : i64) elementSize(4) name("a") descKind(none) mapFlags(to,from) -> !llvm.ptr
    acc.data if(%arg1) dataOperands(%0 : !llvm.ptr) {
      acc.terminator
    }
    return
  }
}
