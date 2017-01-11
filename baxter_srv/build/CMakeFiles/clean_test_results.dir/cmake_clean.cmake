FILE(REMOVE_RECURSE
  "../srv_gen"
  "../srv_gen"
  "../src/baxter_srv/srv"
  "CMakeFiles/clean_test_results"
)

# Per-language clean rules from dependency scanning.
FOREACH(lang)
  INCLUDE(CMakeFiles/clean_test_results.dir/cmake_clean_${lang}.cmake OPTIONAL)
ENDFOREACH(lang)
