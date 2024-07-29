Command line used to find this crash:

/home/ghada/Improved_EBF2_coinToss/fuzzEngine/AFLplusplus/afl-fuzz -i /home/ghada/Improved_EBF2_coinToss/EBF_Results/singleton.c_831/CORPUS_singleton.c -o /home/ghada/Improved_EBF2_coinToss/EBF_Results/singleton.c_831/AFL-Results_singleton.c -m none -t 3000+ -- /home/ghada/Improved_EBF2_coinToss/EBF_Results/singleton.c_831/Executable-Dir_singleton.c/singleton_AFL

If you can't reproduce a bug outside of afl-fuzz, be sure to set the same
memory limit. The limit used for this fuzzing session was 0 B.

Need a tool to minimize test cases before investigating the crashes or sending
them to a vendor? Check out the afl-tmin that comes with the fuzzer!

Found any cool bugs in open-source tools using afl-fuzz? If yes, please post
to https://github.com/AFLplusplus/AFLplusplus/issues/286 once the issues
 are fixed :)

