FILE(REMOVE_RECURSE
  "../srv_gen"
  "../srv_gen"
  "../src/baxter_srv/srv"
  "CMakeFiles/ROSBUILD_gensrv_py"
  "../src/baxter_srv/srv/__init__.py"
  "../src/baxter_srv/srv/_ImageSrv.py"
)

# Per-language clean rules from dependency scanning.
FOREACH(lang)
  INCLUDE(CMakeFiles/ROSBUILD_gensrv_py.dir/cmake_clean_${lang}.cmake OPTIONAL)
ENDFOREACH(lang)
