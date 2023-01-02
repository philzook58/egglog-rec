# Rewriting engine competition translated to egglog.

<https://sourcesup.renater.fr/scm/viewvc.php/rec/2019-CONVECS/> Thanks to the authors of these benchmarks which at least includes Hubert Garavel and others.

- scrape.py was used to get stuff off the website. You probably don't need this
- rec.py generates egglog files from the rec files. There may still be bugs in this translation
- benchmark.py runs the tests. You'll need to add your egglog binary

There may still be significant bugs in the translation of rules.

The natlist and hanoi examples are currently disabled. Hanoi seems to be missing the relevant original code. natlist isn't parsing due to resource restrictions.