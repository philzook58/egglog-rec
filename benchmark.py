import glob
import time
import subprocess
import subprocess
import os
my_env = os.environ.copy()
my_env["RUST_LOG"] = "error"
for name in glob.glob('egglog/rec/*.egg'):
    start = time.time()
    print(name)
    try:
        subprocess.run(["../egg-smol2/target/release/egg-smol",
                        name], env=my_env, timeout=100)
    except Exception as e:
        print("test failed", e)
    print(name, "time", time.time()-start)
