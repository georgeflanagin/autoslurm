autoslurm()
{
    export PYTHONPATH=/usr/local/sw/hpclib
    export AUTOSLURM_DEFAULT_DIR="$PWD"
    command pushd /usr/local/sw/autoslurm.dev >/dev/null
    python autoslurm.py --dryrun $@
    command popd >/dev/null
}
