@rem doc.cmd for all subfolders
@for /d %%i in (*) do @(
  @echo === %%i ===
  @pushd %%i
  @call doc.cmd %1 %2 %3 %4 %5
  @popd )
