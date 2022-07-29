autoslurm()
{
    export PYTHONPATH=/usr/local/sw/hpclib
    # Instead of using $OLDPWD as the location we came from to run
    # autoslurm, let's set an environment variable so that we can
    # know that this shell function launched autoslurm.
    export AUTOSLURM_DEFAULT_DIR=$(realpath $PWD)
    command pushd /usr/local/sw/autoslurm.dev >/dev/null
    python autoslurm.py --dryrun $@
    command popd >/dev/null
}
